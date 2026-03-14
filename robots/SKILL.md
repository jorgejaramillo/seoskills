---
name: robots-txt
description: "Validate, generate, and audit robots.txt files for SEO. Use this skill whenever the user mentions robots.txt, crawler directives, bot blocking, crawl control, AI crawler management, or asks about controlling how search engines or AI bots crawl their website. Also trigger when the user wants to check if their robots.txt has errors, wants to generate a new robots.txt from scratch, needs to audit an existing robots.txt for SEO issues, wants to block or allow specific bots (like GPTBot, CCBot, ClaudeBot, Googlebot, Bingbot), or asks about crawl budget optimization. Trigger even if the user just pastes a robots.txt and asks 'is this ok?' or 'review this'. Works for any CMS or static site."
---

# robots.txt Skill — Validate, Generate & Audit

This skill handles three core workflows for robots.txt files: **validation** (syntax and logic checking), **generation** (creating new files from scratch based on site needs), and **auditing** (SEO-focused review of existing files for issues and improvements).

## Quick Reference: robots.txt Fundamentals

Before doing anything, internalize these rules — they're the foundation for every validation, generation, and audit task:

### Syntax Rules (RFC 9309)
- The file MUST be served at the root: `https://domain.com/robots.txt`
- Each record starts with one or more `User-agent:` lines
- Valid directives: `User-agent`, `Disallow`, `Allow`, `Sitemap`, `Crawl-delay` (unofficial but widely supported)
- Directives are case-insensitive (`disallow` = `Disallow`), but path values are case-sensitive (`/Admin/` ≠ `/admin/`)
- An empty `Disallow:` means "allow everything" for that user-agent
- A missing or empty robots.txt = everything is allowed
- Comments start with `#` and can appear on their own line or after a directive
- Blank lines separate records (groups of directives for a user-agent)
- `Sitemap:` is a standalone directive (not tied to any user-agent block) and must use an absolute URL
- Wildcards: `*` matches any sequence of characters; `$` anchors to end of URL (Google/Bing support these)
- Maximum recommended file size: 500 KiB (Google may stop processing beyond this)

### How Search Engines Pick Rules
- Google/Bing: the **most specific** (longest matching path) rule wins, regardless of order. In ties, `Allow` wins.
- Other crawlers: typically the **first matching rule** wins.
- Each crawler uses the **most specific user-agent block** that matches its name. If none matches, it falls back to `User-agent: *`.
- If a crawler has a specific block, it ignores the `*` block entirely — the rules are NOT merged (except Google, which merges multiple blocks for the same user-agent).

### Critical SEO Considerations
- `Disallow` does NOT mean "noindex" — Google can still index a URL if external links point to it. Use `noindex` meta tag or `X-Robots-Tag` header to prevent indexing.
- Blocking CSS/JS files prevents Google from rendering pages properly — avoid this.
- Blocking a URL with a canonical tag means Google can't see the canonical — bad for deduplication.
- Blocking parameterized URLs is good for crawl budget but bad if those pages have canonical tags.
- `Sitemap:` in robots.txt is supplementary; always submit sitemaps via Search Console too.
- `Crawl-delay` is ignored by Googlebot but respected by Bingbot and Yandex.
- robots.txt is PUBLIC — never list sensitive paths in it (security through obscurity is a bad idea).

### AI Crawler Landscape (2025-2026)
For the `references/ai-crawlers.md` file, read it before generating or auditing any robots.txt that deals with AI bots. It contains the comprehensive, up-to-date list of AI crawler user-agents, their purposes, and recommended strategies.

---

## Workflow 1: VALIDATE a robots.txt

When the user provides a robots.txt (as text, file, or URL to fetch), run validation.

### Step 1: Run the validation script

```bash
python3 /path/to/skill/scripts/validate_robots.py <<'ROBOTS_INPUT'
<paste or pipe the robots.txt content here>
ROBOTS_INPUT
```

The script checks for:
- Syntax errors (invalid directives, missing user-agent before rules, malformed lines)
- Logic errors (conflicting Allow/Disallow, overly broad blocks, duplicate rules)
- SEO warnings (blocking CSS/JS, blocking sitemap URLs, missing Sitemap directive, blocking crawlers from canonical pages)
- AI crawler coverage (whether known AI bots are addressed)
- Best practice violations (file too large, sensitive paths exposed, missing wildcard user-agent)

### Step 2: Interpret and present results

After running the script, interpret the output and explain each issue to the user in plain language. Group findings by severity:

1. **ERRORS** — Things that are broken and will cause unexpected crawler behavior
2. **WARNINGS** — Things that could hurt SEO or lead to unintended blocking
3. **INFO** — Suggestions and best practices

For each issue, explain **what** it is, **why** it matters, and **how** to fix it. Provide the corrected directive.

### Step 3: Offer a corrected version

After explaining issues, generate a corrected robots.txt and show it to the user with a diff-style explanation of what changed and why. Do NOT write the corrected file to outputs — present it inline in the conversation.

---

## Workflow 2: GENERATE a robots.txt

When the user wants to create a robots.txt from scratch, gather requirements first.

### Step 1: Gather context

Ask the user (or infer from context):
1. **What CMS/platform?** (WordPress, Shopify, Next.js, Hugo, custom, etc.)
2. **What type of site?** (ecommerce, blog, SaaS, corporate, portfolio, etc.)
3. **What should be blocked?** (admin areas, internal search, user accounts, staging, API endpoints, etc.)
4. **AI crawler policy?** (block all AI training, allow AI search but block training, allow everything, selective per-bot)
5. **Do they have a sitemap URL?**
6. **Any specific bots to handle differently?** (rate limiting Bingbot, blocking specific scrapers, etc.)

### Step 2: Generate the file

Based on the answers, generate a well-commented robots.txt following these principles:

- Always start with a header comment block explaining the file's purpose, last update date, and contact
- Group directives logically: traditional search engines first, then AI crawlers, then the wildcard fallback
- Add inline comments explaining each block's purpose
- Include `Sitemap:` directive(s) at the bottom with absolute URLs
- Use the most restrictive approach by default — it's safer to block too much and then allow than vice versa
- For ecommerce: block cart, checkout, account, internal search, faceted navigation parameters
- For WordPress: block `/wp-admin/` but allow `/wp-admin/admin-ajax.php`, block `/wp-includes/`
- For any site: block `/cgi-bin/`, `/tmp/`, login/register pages, print-view URLs, internal API endpoints
- Never block CSS, JS, or image files that are needed for rendering

Present the generated robots.txt inline in the conversation. Do NOT write to outputs. Let the user copy it themselves.

### Step 3: Validate the generated file

Run the validation script on the generated file as a sanity check. Report any issues.

---

## Workflow 3: AUDIT a robots.txt (SEO Review)

When the user wants an in-depth SEO audit of an existing robots.txt.

### Step 1: Obtain the file

If the user provides a URL, fetch `{url}/robots.txt`. If they paste text, use that directly.

### Step 2: Run the validation script

Same as Workflow 1, Step 1.

### Step 3: Deep SEO analysis

Go beyond syntax validation. Read the `references/ai-crawlers.md` file and analyze:

1. **Crawl Budget Impact**: Are there patterns that waste crawl budget? (e.g., not blocking faceted nav, internal search, paginated archives)
2. **Indexation Risk**: Are important pages accidentally blocked? Are canonical-tagged pages blocked?
3. **AI Bot Strategy**: Is there a coherent AI crawler strategy? Are they missing important AI bots? Are they blocking AI search bots when they should only block training bots?
4. **Competitive Analysis**: Based on the site type, what are they missing compared to industry best practices?
5. **Security Exposure**: Are sensitive paths being revealed in the robots.txt?
6. **Completeness**: Is the file missing common directives for the detected CMS/platform?
7. **Conflict Detection**: Do any Allow/Disallow rules conflict? Which one would win for Google vs other crawlers?

### Step 4: Generate audit report

Present findings as a structured analysis with:
- Executive summary (1-2 sentences on overall health)
- Critical issues (must-fix)
- Recommended improvements (should-fix)
- Nice-to-have optimizations
- A revised robots.txt with all recommendations applied

---

## Common Patterns Reference

### WordPress
```
User-agent: *
Disallow: /wp-admin/
Allow: /wp-admin/admin-ajax.php
Disallow: /wp-includes/
Disallow: /wp-content/plugins/
Disallow: /trackback/
Disallow: /feed/
Disallow: /comments/feed/
Disallow: /?s=
Disallow: /search/
Disallow: /author/
Disallow: /tag/*/feed/
Disallow: /category/*/feed/
```

### Shopify
```
User-agent: *
Disallow: /admin
Disallow: /cart
Disallow: /orders
Disallow: /checkouts/
Disallow: /checkout
Disallow: /carts
Disallow: /account
Disallow: /collections/*+*
Disallow: /collections/*%2B*
Disallow: /collections/*%2b*
Disallow: /blogs/*+*
Disallow: /blogs/*%2B*
Disallow: /blogs/*%2b*
Disallow: /*?*sort_by*
Disallow: /*?*q=*
Disallow: /search
Disallow: /apple-app-site-association
Disallow: /.well-known
```

### SaaS / Web Application
```
User-agent: *
Disallow: /app/
Disallow: /dashboard/
Disallow: /api/
Disallow: /internal/
Disallow: /admin/
Disallow: /login
Disallow: /register
Disallow: /account/
Disallow: /settings/
Allow: /api/docs/
```

### AI Crawler Block (Training Only — Allow AI Search)
```
# AI training crawlers - BLOCK
User-agent: GPTBot
Disallow: /

User-agent: Google-Extended
Disallow: /

User-agent: anthropic-ai
Disallow: /

User-agent: CCBot
Disallow: /

User-agent: FacebookBot
Disallow: /

User-agent: Bytespider
Disallow: /

User-agent: Applebot-Extended
Disallow: /

User-agent: Diffbot
Disallow: /

User-agent: Omgili
Disallow: /

User-agent: img2dataset
Disallow: /

# AI search/retrieval crawlers - ALLOW
User-agent: ChatGPT-User
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: YouBot
Allow: /
```

---

## Important Reminders

- All generation and validation happens inline in the conversation. Do NOT create output files for robots.txt content — the user should copy-paste it into their site's root.
- The validation script (`scripts/validate_robots.py`) is the primary tool. Always run it.
- For AI crawler questions, always read `references/ai-crawlers.md` first for the latest bot list.
- Be opinionated but explain your reasoning. If something is a best practice, say so and explain why.
- When in doubt, be conservative — it's better to accidentally block something non-critical than to accidentally expose the entire site.