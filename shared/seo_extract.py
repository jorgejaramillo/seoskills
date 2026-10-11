#!/usr/bin/env python3
"""Extrae señales SEO de URLs o archivos HTML y las devuelve como JSON.

Sustituye las cadenas de `curl | grep`: lee el <head> completo (title, meta,
canonical, hreflang, OG, JSON-LD) y el <body> (headings, enlaces, imágenes,
conteo de palabras). Solo usa la librería estándar.

Uso:
  python3 shared/seo_extract.py https://example.com https://example.com/blog -o pages.json
  python3 shared/seo_extract.py --dir crawler/output/example.com -o pages.json
  python3 shared/seo_extract.py pagina.html --base https://example.com/pagina
  python3 shared/seo_extract.py https://example.com --head-images   # HEAD a cada imagen (peso/tipo)
  python3 shared/seo_extract.py --sitemap https://example.com/sitemap.xml --limit 30 -o pages.json
"""
import argparse
import json
import re
import ssl
import sys
import time
import urllib.error
import urllib.request
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()
UNVERIFIED_CTX = ssl._create_unverified_context()

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
SKIP_TEXT = {"script", "style", "noscript", "template", "svg"}
ZONES = ("nav", "header", "footer", "aside", "main")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
        "meta", "source", "track", "wbr"}


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.d = {
            "lang": None, "title": None, "meta_description": None, "meta_robots": None,
            "googlebot": None, "viewport": None, "charset": None, "canonical": [],
            "hreflang": [], "og": {}, "twitter": {}, "headings": {f"h{i}": [] for i in range(1, 7)},
            "links": [], "images": [], "jsonld_raw": [], "words": 0,
        }
        self._title_buf = None
        self._heading = None
        self._anchor = None
        self._jsonld = None
        self._picture = 0

    def _zone(self):
        for t in reversed(self.stack):
            if t in ZONES:
                return t
        return "body"

    def handle_starttag(self, tag, attrs):
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag not in VOID:
            self.stack.append(tag)
        d = self.d
        if tag == "html":
            d["lang"] = a.get("lang")
        elif tag == "title" and "svg" not in self.stack[:-1] and d["title"] is None:
            self._title_buf = []
        elif tag == "meta":
            name = (a.get("name") or "").lower()
            prop = (a.get("property") or "").lower()
            content = a.get("content", "").strip()
            if "charset" in a:
                d["charset"] = a["charset"]
            if name == "description" and d["meta_description"] is None:
                d["meta_description"] = content
            elif name == "robots":
                d["meta_robots"] = content
            elif name == "googlebot":
                d["googlebot"] = content
            elif name == "viewport":
                d["viewport"] = content
            elif prop.startswith("og:"):
                d["og"][prop[3:]] = content
            elif name.startswith("twitter:"):
                d["twitter"][name[8:]] = content
        elif tag == "link":
            rel = (a.get("rel") or "").lower().split()
            if "canonical" in rel:
                d["canonical"].append(a.get("href", ""))
            if "alternate" in rel and a.get("hreflang"):
                d["hreflang"].append({"lang": a["hreflang"], "href": a.get("href", "")})
        elif tag in d["headings"]:
            self._heading = (tag, [])
        elif tag == "a" and "href" in a:
            self._anchor = {"href": a["href"], "text": [], "rel": a.get("rel", ""),
                            "zone": self._zone(), "img_alt": None}
        elif tag == "img":
            img = {k: a.get(k) for k in ("src", "alt", "width", "height", "loading",
                                         "decoding", "fetchpriority", "srcset", "sizes")}
            img["src"] = img["src"] or a.get("data-src") or a.get("data-lazy-src")
            img["has_alt"] = "alt" in a
            img["in_picture"] = self._picture > 0
            img["zone"] = self._zone()
            img["index"] = len(d["images"])
            d["images"].append(img)
            if self._anchor is not None:
                self._anchor["img_alt"] = a.get("alt")
        elif tag == "picture":
            self._picture += 1
        elif tag == "script" and "ld+json" in (a.get("type") or "").lower():
            self._jsonld = []

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag in self.stack:
            while self.stack and self.stack.pop() != tag:
                pass
        d = self.d
        if tag == "title" and self._title_buf is not None:
            d["title"] = " ".join("".join(self._title_buf).split())
            self._title_buf = None
        elif self._heading and tag == self._heading[0]:
            d["headings"][tag].append(" ".join("".join(self._heading[1]).split()))
            self._heading = None
        elif tag == "a" and self._anchor is not None:
            an = self._anchor
            an["text"] = " ".join("".join(an["text"]).split()) or (an["img_alt"] or "")
            del an["img_alt"]
            d["links"].append(an)
            self._anchor = None
        elif tag == "picture":
            self._picture = max(0, self._picture - 1)
        elif tag == "script" and self._jsonld is not None:
            d["jsonld_raw"].append("".join(self._jsonld))
            self._jsonld = None

    def handle_data(self, data):
        if self._jsonld is not None:
            self._jsonld.append(data)
            return
        if self._title_buf is not None:
            self._title_buf.append(data)
            return
        if any(t in SKIP_TEXT for t in self.stack):
            return
        if self._heading:
            self._heading[1].append(data)
        if self._anchor is not None:
            self._anchor["text"].append(data)
        if "body" in self.stack:
            self.d["words"] += len(data.split())


def schema_types(raw_blocks):
    types, errors = [], 0

    def walk(node):
        if isinstance(node, dict):
            t = node.get("@type")
            if isinstance(t, str):
                types.append(t)
            elif isinstance(t, list):
                types.extend(x for x in t if isinstance(x, str))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    for raw in raw_blocks:
        try:
            walk(json.loads(raw))
        except ValueError:
            errors += 1
    return sorted(set(types)), errors


class _Recorder(urllib.request.HTTPRedirectHandler):
    def __init__(self):
        self.chain = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.chain.append({"status": code, "url": req.full_url})
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, timeout=30, ctx=SSL_CTX):
    rec = _Recorder()
    opener = urllib.request.build_opener(rec, urllib.request.HTTPSHandler(context=ctx))
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "es,en;q=0.8"})
    t0 = time.time()
    info = {"status": None, "final_url": url, "redirects": rec.chain, "ttfb_ms": None,
            "bytes": 0, "headers": {}}
    try:
        resp = opener.open(req, timeout=timeout)
    except urllib.error.HTTPError as e:
        resp = e
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        if ctx is SSL_CTX and "CERTIFICATE" in str(e).upper():
            # Certificado inválido: es un hallazgo en sí mismo, pero seguimos analizando
            html, info = fetch(url, timeout, UNVERIFIED_CTX)
            info["ssl_error"] = str(e)
            return html, info
        info["error"] = str(e)
        return "", info
    info["ttfb_ms"] = round((time.time() - t0) * 1000)
    body = resp.read()
    info.update(status=resp.status if hasattr(resp, "status") else resp.code,
                final_url=resp.geturl(), bytes=len(body))
    h = resp.headers
    info["headers"] = {k: h.get(k) for k in ("content-type", "x-robots-tag", "content-encoding",
                                              "cache-control", "strict-transport-security", "server")
                       if h.get(k)}
    charset = h.get_content_charset() or "utf-8"
    return body.decode(charset, errors="replace"), info


def head_image(url, timeout=15):
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as r:
            size = r.headers.get("content-length")
            return {"bytes": int(size) if size else None, "type": r.headers.get("content-type"),
                    "status": r.status}
    except Exception as e:  # noqa: BLE001 - cualquier fallo de red se reporta, no detiene el análisis
        return {"bytes": None, "type": None, "status": getattr(e, "code", None)}


def unwrap(html):
    """Los HTML guardados con la respuesta cruda de Cloudflare vienen como {"success":..,"result":"<html>"}."""
    if html.lstrip().startswith('{"'):
        try:
            data = json.loads(html)
            if isinstance(data.get("result"), str):
                return data["result"]
        except ValueError:
            pass
    return html


def analyze(html, url, fetch_info=None, head_images=False):
    html = unwrap(html)
    p = SEOParser()
    p.feed(html)
    d = p.d
    host = urlparse(url).netloc.lower().removeprefix("www.")
    links = []
    for ln in d["links"]:
        href = ln["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#", "data:")) or not href:
            continue
        absu = urldefrag(urljoin(url, href))[0]
        lhost = urlparse(absu).netloc.lower().removeprefix("www.")
        ln.update(url=absu, internal=lhost == host,
                  nofollow="nofollow" in ln["rel"].lower())
        links.append(ln)
    for img in d["images"]:
        if img["src"]:
            img["url"] = urljoin(url, img["src"])
            img["ext"] = Path(urlparse(img["url"]).path).suffix.lower().lstrip(".") or None
    if head_images:
        seen = {}
        for img in d["images"]:
            u = img.get("url")
            if u and u.startswith("http"):
                seen.setdefault(u, head_image(u))
                img.update({f"head_{k}": v for k, v in seen[u].items()})
    types, jerr = schema_types(d.pop("jsonld_raw"))
    page = {
        "url": url,
        **(fetch_info or {}),
        "lang": d["lang"],
        "title": d["title"], "title_len": len(d["title"] or ""),
        "meta_description": d["meta_description"],
        "meta_description_len": len(d["meta_description"] or ""),
        "meta_robots": d["meta_robots"], "googlebot": d["googlebot"],
        "viewport": d["viewport"], "charset": d["charset"],
        "canonical": d["canonical"][0] if d["canonical"] else None,
        "canonical_count": len(d["canonical"]),
        "hreflang": d["hreflang"], "og": d["og"], "twitter": d["twitter"],
        "headings": d["headings"],
        "schema_types": types, "jsonld_errors": jerr,
        "word_count": d["words"],
        "links": links,
        "links_internal": sum(1 for x in links if x["internal"]),
        "links_external": sum(1 for x in links if not x["internal"]),
        "images": d["images"],
    }
    if page["canonical"]:
        page["canonical"] = urljoin(url, page["canonical"])
        page["canonical_self"] = page["canonical"].rstrip("/") == url.rstrip("/")
    robots = " ".join(filter(None, [d["meta_robots"], (fetch_info or {}).get("headers", {}).get("x-robots-tag")]))
    page["noindex"] = "noindex" in robots.lower()
    return page


def sitemap_urls(url, limit=50000, _depth=0):
    """URLs de un sitemap o sitemap index (recursivo). Devuelve [] si no existe."""
    xml, info = fetch(url)
    if info.get("status") != 200 or not xml:
        return []
    locs = [x.strip() for x in re.findall(r"<loc>\s*(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?\s*</loc>", xml, re.S)]
    if "<sitemapindex" in xml and _depth < 3:
        out = []
        for child in locs:
            out.extend(sitemap_urls(child, limit - len(out), _depth + 1))
            if len(out) >= limit:
                break
        return out[:limit]
    return locs[:limit]


def load_dir(directory):
    """Lee los HTML de una carpeta del crawler. Usa _manifest.json (archivo→URL) si existe."""
    directory = Path(directory)
    manifest = {}
    mpath = directory / "_manifest.json"
    if mpath.exists():
        manifest = {m["file"]: m for m in json.loads(mpath.read_text())}
    for f in sorted(directory.glob("*.html")):
        m = manifest.get(f.name, {})
        yield f, m.get("url"), {"status": m.get("status"), "source": "cloudflare-render"}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("inputs", nargs="*", help="URLs o archivos .html")
    ap.add_argument("--dir", help="Carpeta con HTML descargado por el crawler")
    ap.add_argument("--base", help="URL base para un archivo HTML suelto")
    ap.add_argument("--sitemap", help="Analiza las URLs de este sitemap (o sitemap index)")
    ap.add_argument("--limit", type=int, default=50, help="Máximo de URLs del sitemap (default 50)")
    ap.add_argument("--head-images", action="store_true", help="HEAD a cada imagen para peso y tipo")
    ap.add_argument("-o", "--out", help="Archivo JSON de salida (por defecto stdout)")
    args = ap.parse_args()

    pages = []
    jobs = []
    if args.dir:
        jobs.extend(load_dir(args.dir))
    if args.sitemap:
        urls = sitemap_urls(args.sitemap)
        print(f"  sitemap: {len(urls)} URLs, se analizan {min(len(urls), args.limit)}", file=sys.stderr)
        jobs.extend((None, u, None) for u in urls[:args.limit])
    for item in args.inputs:
        if item.startswith(("http://", "https://")):
            jobs.append((None, item, None))
        else:
            jobs.append((Path(item), args.base, {"source": "file"}))

    for path, url, info in jobs:
        if path is None:
            html, info = fetch(url)
            info["source"] = "http"
        else:
            html = path.read_text(errors="replace")
        if not url:
            # Sin URL conocida: usa canonical u og:url del propio HTML
            probe = analyze(html, "https://unknown.invalid/")
            url = probe["canonical"] if probe["canonical"] and "unknown.invalid" not in probe["canonical"] \
                else probe["og"].get("url") or f"file://{path.resolve()}"
        page = analyze(html, url, info, args.head_images)
        if path is not None:
            page["file"] = str(path)
        pages.append(page)
        print(f"  ✓ {url}  [{page.get('status') or '-'}] title={page['title_len']}c "
              f"h1={len(page['headings']['h1'])} links={len(page['links'])} imgs={len(page['images'])}",
              file=sys.stderr)

    out = json.dumps(pages, ensure_ascii=False, indent=1)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(out)
        print(f"→ {len(pages)} páginas en {args.out}", file=sys.stderr)
    else:
        print(out)


if __name__ == "__main__":
    main()
