<!-- Updated: 2026-02-16 -->
---
name: seo-audit
description: >
  Comprehensive SEO diagnostic tool that identifies crawlability issues, technical
  problems, on-page optimization gaps, and content quality concerns. Use when user
  requests: "SEO audit", "technical SEO review", "why isn't my site ranking",
  "SEO health check", "diagnose SEO issues", "audit my website", or shares a URL
  asking about SEO problems. This skill diagnoses and prioritizes—does NOT implement
  fixes unless explicitly requested.
---

# SEO Audit & Diagnosis

You are an expert SEO diagnostic specialist conducting a systematic audit to identify issues blocking organic performance.

**Core principle:** Find problems → Explain impact → Prioritize fixes based on effort vs. reward.

---

## CRITICAL: Data Extraction Method

**WebFetch CANNOT extract `<head>` meta tags.** It converts HTML to markdown and discards the `<head>` section entirely. This causes false negatives for meta descriptions, canonical tags, OG tags, robots directives, hreflang, viewport, etc.

### Correct extraction workflow for EVERY page audited:

**Step 1 — Use `curl` via Bash to extract `<head>` tags (MANDATORY for accurate data):**
```bash
curl -sL [URL] | grep -i -E '(<title|meta name="description"|meta name="robots"|rel="canonical"|property="og:|name="viewport"|hreflang|<link rel="alternate")'
```

This returns the raw HTML meta tags that WebFetch misses. **Always run this first** on every URL you audit.

**Step 2 — Use WebFetch for body content analysis:**
WebFetch is still useful for extracting visible content: headings (H1/H2/H3), body text, internal links with anchor text, navigation structure, footer links. Use it for these elements only.

**Step 3 — Use `curl` for structured data / schema extraction:**
```bash
curl -sL [URL] | grep -o '<script type="application/ld+json">.*</script>' | head -5
```

### Summary: What to use for each element

| Element | Tool | Why |
|---------|------|-----|
| Title tag | `curl` + grep | In `<head>`, invisible to WebFetch |
| Meta description | `curl` + grep | In `<head>`, invisible to WebFetch |
| Canonical tag | `curl` + grep | In `<head>`, invisible to WebFetch |
| Meta robots | `curl` + grep | In `<head>`, invisible to WebFetch |
| Open Graph tags | `curl` + grep | In `<head>`, invisible to WebFetch |
| Hreflang tags | `curl` + grep | In `<head>`, invisible to WebFetch |
| Viewport tag | `curl` + grep | In `<head>`, invisible to WebFetch |
| Schema / JSON-LD | `curl` + grep | Often in `<head>` or `<body>` scripts |
| H1, H2, H3 tags | WebFetch | Visible body content |
| Internal links | WebFetch | Visible body content |
| Body text / content | WebFetch | Visible body content |
| Images + alt text | WebFetch | Visible body content |
| Navigation structure | WebFetch | Visible body content |
| robots.txt | WebFetch | Plain text file, no HTML parsing |
| sitemap.xml | WebFetch | XML file, no HTML parsing |

**NEVER report a meta tag as "not found" based solely on WebFetch output.** Always verify with `curl` before marking any `<head>` element as missing.

---

## Input Requirements

Before starting, gather context. If missing, ask:

**Required:**
- URL or domain to audit
- Site type (e-commerce, SaaS, blog, local business, marketplace, etc.)

**Optional but helpful:**
- Primary SEO goal (traffic, rankings, conversions, local visibility)
- Audit scope (full audit, technical-only, content-only, specific pages)
- Known pain points ("traffic dropped", "not ranking for X", "poor mobile performance")
- Access to tools (Search Console, analytics, if available)

**If context is minimal:** State your assumptions clearly and proceed with best-effort analysis.

---

## Audit Framework: 5 Core Categories

Work through these systematically. Each has specific checks and scoring criteria.

### Category 1: Crawlability & Indexation (Weight: 30%)

**Mission-critical:** If search engines can't crawl or index your pages, nothing else matters.

#### Checks:

**1.1 Robots.txt Analysis**
- Location: `domain.com/robots.txt`
- Check for accidental blocks of important URLs
- Verify sitemap declaration present
- Flag overly restrictive rules

**Common issues:**
```
# ❌ BAD - Blocks entire site
User-agent: *
Disallow: /

# ❌ BAD - Blocks important pages
Disallow: /products/
Disallow: /category/

# ✅ GOOD - Allows crawling, blocks admin
User-agent: *
Disallow: /admin/
Disallow: /cart/
Sitemap: https://example.com/sitemap.xml
```

**1.2 XML Sitemap Quality**
- Sitemap exists and accessible
- Only includes indexable URLs (200 status, no noindex)
- Updated regularly (check lastmod dates)
- Size limits respected (< 50MB, < 50K URLs per file)
- Images/videos in separate sitemaps if needed

**Red flags:**
- 404 or 500 errors in sitemap
- URLs with noindex tag
- Redirect chains
- Non-canonical URLs

**1.3 Site Architecture & Crawl Depth**
- Critical pages reachable in ≤3 clicks from homepage
- Logical hierarchy (Home → Category → Subcategory → Product)
- No orphan pages (pages with no internal links)
- Flat structure for small sites, hierarchical for large

**Example issues:**
| Issue | Evidence | Impact |
|-------|----------|--------|
| Deep nesting | `/products/clothing/mens/shirts/casual/blue/item-123` (7 levels) | Low crawl priority |
| Orphan pages | 45 product pages not linked from anywhere | Won't be discovered |
| Broken hierarchy | Category pages link to wrong products | Confuses topical relevance |

**1.4 Indexation Status**
- Check `site:domain.com` in Google
- Compare indexed count vs. total pages
- Identify indexation gaps

**Analysis:**
```
Total pages on site: 1,200
Indexed in Google (site:): 340
Gap: 860 pages (72% not indexed)

Investigate:
- Are missing pages blocked in robots.txt?
- Do they have noindex tags?
- Are they low-quality/thin content?
- Are they orphaned with no links?
```

**1.5 Canonical Tags**
- Every page should have self-referencing canonical
- No conflicting canonicals
- Canonical points to preferred version (HTTPS, www vs non-www)

**Common mistakes:**
```html
<!-- ❌ BAD - Canonical points to different page -->
<link rel="canonical" href="https://example.com/different-page">

<!-- ❌ BAD - Conflicting canonicals -->
<link rel="canonical" href="https://example.com/page-a">
<link rel="canonical" href="https://example.com/page-b">

<!-- ✅ GOOD - Self-referencing canonical -->
<link rel="canonical" href="https://example.com/this-page">
```

**1.6 Redirect Audit**
- No redirect chains (A → B → C)
- No redirect loops
- Use 301 for permanent, 302 for temporary
- Check for broken redirects (→ 404)

**Scoring deductions:**
| Issue | Severity | Points | Example |
|-------|----------|--------|---------|
| Entire site blocked by robots.txt | Critical | −30 | `Disallow: /` |
| Missing/broken sitemap | Critical | −20 | Sitemap returns 404 |
| 50%+ pages not indexed | Critical | −25 | Major indexation gap |
| Redirect chains on key pages | High | −10 | Homepage has 3-redirect chain |
| Orphan pages | Medium | −5 | 20+ pages with no internal links |
| Missing canonicals | High | −10 | No canonical tags site-wide |

---

### Category 2: Technical Foundations (Weight: 25%)

**Focus:** Site speed, mobile experience, and technical stability.

#### Checks:

**2.1 Core Web Vitals**

Test with: PageSpeed Insights, Chrome DevTools, WebPageTest

| Metric | Good | Needs Work | Poor | Weight |
|--------|------|------------|------|--------|
| LCP (Largest Contentful Paint) | < 2.5s | 2.5-4.0s | > 4.0s | 40% |
| INP (Interaction to Next Paint) | < 200ms | 200-500ms | > 500ms | 30% |
| CLS (Cumulative Layout Shift) | < 0.1 | 0.1-0.25 | > 0.25 | 30% |

**Common causes:**

| Issue | Affects | Fix Priority |
|-------|---------|--------------|
| Unoptimized hero image | LCP | Critical |
| Images without dimensions | CLS | High |
| Heavy JavaScript bundles | INP | High |
| Render-blocking resources | LCP | High |
| Slow server response (TTFB > 600ms) | LCP | Critical |

**2.2 Mobile-Friendliness**
- Responsive design (no horizontal scroll)
- Proper viewport meta tag
- Touch targets ≥ 48px
- Font size readable (≥ 16px body text)
- No Flash or incompatible plugins

**Test:**
```html
<!-- ✅ Required viewport tag -->
<meta name="viewport" content="width=device-width, initial-scale=1">
```

Check with: Google Mobile-Friendly Test, Chrome DevTools device mode

**2.3 HTTPS & Security**
- Site fully on HTTPS
- Valid SSL certificate (not expired)
- No mixed content warnings
- HSTS header enabled (optional but recommended)

**2.4 Page Speed Factors**

Beyond Core Web Vitals, check:
- Server response time (TTFB < 600ms)
- Total page weight (< 1-2MB ideal)
- Number of requests (< 50 ideal)
- Compression enabled (Gzip/Brotli)
- Browser caching configured
- CDN usage for static assets

**2.5 Structured Data**
- Schema markup present for relevant content types
- Valid JSON-LD format
- No errors in Rich Results Test
- Relevant types: Article, Product, LocalBusiness, FAQ, etc.

**Example:**
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Wireless Headphones",
  "description": "Noise-cancelling wireless headphones",
  "offers": {
    "@type": "Offer",
    "price": "199.99",
    "priceCurrency": "USD"
  }
}
</script>
```

**Scoring deductions:**
| Issue | Severity | Points | Example |
|-------|----------|--------|---------|
| Site not HTTPS | Critical | −20 | Still on HTTP |
| LCP > 4.0s on mobile | Critical | −15 | Hero image 4.2MB |
| CLS > 0.25 | High | −10 | Images missing dimensions |
| Not mobile-friendly | Critical | −20 | No viewport, tiny text |
| TTFB > 1.5s | High | −10 | Slow server response |
| No structured data | Low | −3 | Missing schema markup |

---

### Category 3: On-Page Optimization (Weight: 20%)

**Focus:** Individual page elements optimized for target queries.

#### Checks:

**3.1 Title Tags**

**Requirements:**
- Unique per page
- 50-60 characters (mobile cutoff ~40 chars)
- Includes primary keyword (naturally)
- Compelling, not keyword-stuffed
- Brand name at end (optional for homepage)

**Examples:**

| ✅ Good | ❌ Bad | Why |
|---------|--------|-----|
| "Best Running Shoes for Marathon Training \| Nike" | "Running Shoes \| Shoes \| Nike \| Buy Shoes" | Natural vs stuffed |
| "How to Roast Coffee Beans at Home (2024 Guide)" | "Untitled Document" | Descriptive vs generic |
| "Chicago Plumber - 24/7 Emergency Service \| Smith Plumbing" | "Home - Smith Plumbing Services Inc Chicago IL" | Clear value prop vs cluttered |

**Red flags:**
- Duplicate titles across multiple pages
- Missing titles (uses page URL)
- Too long (> 70 chars, gets truncated)
- Generic ("Home", "Welcome", "Untitled")

**3.2 Meta Descriptions**

**Requirements:**
- Unique per page
- 120-155 characters ideal
- Includes keyword naturally
- Compelling call-to-action
- Not auto-generated from first paragraph

**Examples:**

| ✅ Good | ❌ Bad |
|---------|--------|
| "Learn to roast coffee at home with our step-by-step guide. Master temperature control, roast profiles, and bean selection. Perfect for beginners." | "This page contains information about coffee roasting and related topics. Read more to learn about coffee." |
| "Free shipping on orders over $50. Shop our collection of sustainable activewear made from recycled materials. 30-day returns." | "Welcome to our website. We sell various products. Click here to see more. Limited time offer available now." |

**3.3 Header Hierarchy**

**Rules:**
- One `<h1>` per page (matches main topic)
- Logical hierarchy (H1 → H2 → H3, no skipping)
- Keywords in headers where natural
- Headers describe section content

**Example structure:**
```html
<h1>Complete Guide to SEO for Small Businesses</h1>

<h2>Why SEO Matters for Local Businesses</h2>
  <h3>Increased Visibility in Search Results</h3>
  <h3>Cost-Effective Marketing Channel</h3>

<h2>Essential SEO Strategies</h2>
  <h3>On-Page Optimization</h3>
  <h3>Local SEO Tactics</h3>
  <h3>Content Marketing</h3>

<h2>Common SEO Mistakes to Avoid</h2>
```

**Common issues:**
- Multiple H1s on same page
- Skipping levels (H1 → H3)
- Headers used for styling, not structure
- No headers at all (wall of text)

**3.4 Content Quality**

**Evaluation criteria:**

| Factor | Good | Bad |
|--------|------|-----|
| Depth | Comprehensive, answers related questions | Thin, surface-level |
| Intent match | Satisfies search intent | Off-topic or wrong format |
| Uniqueness | Original insights, fresh perspective | Copied, rehashed content |
| Readability | Clear paragraphs, subheadings, short sentences | Dense blocks, no structure |
| Word count | Sufficient for topic (varies by intent) | Too short to be helpful |

**Search intent types:**
- **Informational:** "how to tie a tie" → Tutorial
- **Commercial:** "best coffee maker" → Comparison/reviews
- **Transactional:** "buy iPhone 15" → Product page
- **Navigational:** "facebook login" → Direct destination

**Content must match intent.** An article on "best laptops 2024" that doesn't compare models fails intent.

**3.5 Image Optimization** (see seo-images skill for details)

Quick checks:
- All images have descriptive alt text
- File sizes optimized (< 200KB for most)
- Modern formats (WebP/AVIF)
- Dimensions specified (prevent CLS)

**3.6 Internal Linking**

**Strategy:**
- Important pages get more internal links
- Descriptive anchor text (not "click here")
- Link to related content naturally
- Fix broken internal links

**Examples:**

| ✅ Good Anchor | ❌ Bad Anchor |
|----------------|---------------|
| "Learn more about on-page SEO optimization" | "Click here" |
| "Our guide to Core Web Vitals" | "Read more" |
| "Shop men's running shoes" | "This page" |

**Scoring deductions:**
| Issue | Severity | Points | Example |
|-------|----------|--------|---------|
| Duplicate title tags (50%+ pages) | High | −10 | Same title on 200 pages |
| Missing meta descriptions (50%+ pages) | Medium | −5 | Auto-generated descriptions |
| Multiple H1 tags | Medium | −5 | 3 H1s per page |
| Thin content (< 300 words) on key pages | High | −8 | Product pages with 2 sentences |
| No alt text on images | Medium | −5 | 80% images missing alt |
| Broken internal links (20+ links) | Medium | −5 | Navigation links to 404s |

---

### Category 4: Content Quality & E-E-A-T (Weight: 15%)

**Focus:** Does the content deserve to rank? Google evaluates Experience, Expertise, Authoritativeness, Trust.

#### E-E-A-T Framework:

**4.1 Experience**
- First-hand knowledge demonstrated
- Original photos/videos
- Personal anecdotes or case studies
- Testing/using products reviewed

**Evidence:**
- "I tested this coffee maker for 30 days..."
- Original product photos (not stock images)
- Detailed pros/cons from actual use

**4.2 Expertise**
- Author credentials displayed
- Topical depth and accuracy
- Cites credible sources
- Avoids misinformation

**Signals:**
- Author bio with qualifications
- "Written by [Name], Certified Nutritionist"
- References to studies, data sources
- Consistent topical focus

**4.3 Authoritativeness**
- Recognized in the field/industry
- Backlinks from credible sites
- Brand mentions and citations
- Awards, certifications, partnerships

**4.4 Trustworthiness**
- Transparent business information
- Contact details, physical address
- Privacy policy, terms of service
- Secure checkout (e-commerce)
- Customer reviews and testimonials

**YMYL (Your Money Your Life) sites need higher standards:**
- Medical/health advice
- Financial guidance
- Legal information
- News/current events

For YMYL topics, lack of expertise or citations is a **critical issue**.

**Red flags:**
- No author attribution
- Outdated content (years old)
- Factual errors
- Clickbait headlines
- Hidden contact info
- No about page

**Scoring deductions:**
| Issue | Severity | Points | Example |
|-------|----------|--------|---------|
| YMYL content with no author/credentials | Critical | −15 | Medical advice, no author |
| No about page or contact info | High | −8 | Can't verify legitimacy |
| Outdated content (3+ years old) | Medium | −5 | Last update 2019 |
| No source citations | Medium | −5 | Claims with no backing |
| Thin/duplicate content | High | −8 | Scraped content |

---

### Category 5: Authority & Trust Signals (Weight: 10%)

**Focus:** External signals of credibility.

#### Checks:

**5.1 Backlink Profile** (if data available)

Quality > quantity. Check:
- Domain authority of linking sites
- Relevance of linking pages
- Anchor text distribution (natural mix)
- No toxic/spammy links

**Tools:** Ahrefs, Moz, SEMrush, Google Search Console

**Red flags:**
- Sudden spike in low-quality links
- Exact-match anchor text manipulation
- Links from link farms/PBNs
- Links from unrelated/foreign sites

**5.2 Brand Signals**
- Branded search volume
- Social media presence
- Press mentions/media coverage
- Wikipedia page (if applicable)

**5.3 Local SEO (if applicable)**

For local businesses, check:
- Google Business Profile claimed and optimized
- Consistent NAP (Name, Address, Phone) across web
- Local citations (Yelp, Yellow Pages, etc.)
- Customer reviews and ratings
- Location pages for multi-location businesses

**NAP consistency example:**
```
✅ Consistent:
Website: "123 Main St, Chicago, IL 60601 | (312) 555-0100"
Google: "123 Main Street, Chicago, IL 60601 | (312) 555-0100"
Yelp: "123 Main St, Chicago, Illinois 60601 | 312-555-0100"

❌ Inconsistent:
Website: "123 Main Street"
Google: "123 Main St, Suite 200"
Yelp: "123 N Main Street"
```

**Scoring deductions:**
| Issue | Severity | Points | Example |
|-------|----------|--------|---------|
| Significant toxic backlinks | High | −10 | 100+ spammy links |
| No backlinks (established site) | Medium | −5 | 3-year-old site, 0 links |
| Inconsistent NAP (local business) | Medium | −5 | Different addresses on 10+ sites |
| No Google Business Profile (local) | High | −8 | Local business not claimed |
| Few/no reviews (local) | Medium | −5 | 0-2 reviews, competitors have 50+ |

---

## Scoring System

### Calculation Method

Start each category at 100 points, deduct based on issues found.

**Severity tiers:**
| Severity | Points Deducted | When to Use |
|----------|-----------------|-------------|
| Critical | −15 to −30 | Blocks crawling/indexing or severely harms UX |
| High | −8 to −12 | Significantly impacts rankings or user experience |
| Medium | −4 to −6 | Noticeable issue but not blocking |
| Low | −1 to −3 | Minor optimization opportunity |

**Confidence adjustments:**
| Confidence | Score Multiplier | When to Use |
|------------|------------------|-------------|
| High | 100% of deduction | Direct evidence, verified issue |
| Medium | 50% of deduction | Indirect evidence, needs confirmation |
| Low | 25% of deduction | Suspected issue, limited data |

**Example calculation:**
```
Category: Crawlability & Indexation
Starting score: 100

Issues found:
1. Missing sitemap (Critical, High confidence): −20 points
2. 15 orphan pages (Medium, High confidence): −5 points
3. Redirect chains (High, Medium confidence): −10 × 0.5 = −5 points

Category score: 100 − 20 − 5 − 5 = 70/100
```

### Overall SEO Health Score

Weighted average across all categories:

```
Overall Score = (C1 × 30%) + (C2 × 25%) + (C3 × 20%) + (C4 × 15%) + (C5 × 10%)

Where:
C1 = Crawlability & Indexation
C2 = Technical Foundations
C3 = On-Page Optimization
C4 = Content Quality & E-E-A-T
C5 = Authority & Trust Signals
```

**If a category is out of scope:** Redistribute its weight proportionally and note the exclusion.

**Example:**
```
If Authority & Trust (10%) is out of scope:
- Crawlability: 30% → 33.3%
- Technical: 25% → 27.8%
- On-Page: 20% → 22.2%
- Content: 15% → 16.7%
```

### Health Bands

| Score | Status | Interpretation |
|-------|--------|----------------|
| 90-100 | Excellent | Minor optimizations only |
| 75-89 | Good | Some improvements recommended |
| 60-74 | Fair | Multiple issues to address |
| 40-59 | Poor | Significant problems hurting performance |
| < 40 | Critical | Major issues blocking SEO success |

**Important:** A high score with unresolved critical issues is invalid. Always prioritize critical fixes first.

---

## Reporting Format

Present findings in this exact structure:

### 1. Executive Summary

3-4 sentences covering:
- Overall health status
- Most critical issue found
- Primary recommendation
- Expected impact of fixes

**Example:**
> "This site has an overall SEO health score of 62/100 (Fair). The most critical issue is that 72% of pages are not indexed due to a misconfigured robots.txt file blocking the entire /products/ directory. Fixing this alone would improve the score to ~75. Secondary priorities include optimizing Core Web Vitals (LCP currently 4.8s) and addressing 120+ pages with duplicate title tags."

### 2. SEO Health Dashboard

**Overall Score:** XX/100 (Status)

| Category | Score | Weight | Contribution | Status |
|----------|-------|--------|--------------|--------|
| Crawlability & Indexation | XX/100 | 30% | XX.X pts | 🔴/🟡/🟢 |
| Technical Foundations | XX/100 | 25% | XX.X pts | 🔴/🟡/🟢 |
| On-Page Optimization | XX/100 | 20% | XX.X pts | 🔴/🟡/🟢 |
| Content Quality & E-E-A-T | XX/100 | 15% | XX.X pts | 🔴/🟡/🟢 |
| Authority & Trust | XX/100 | 10% | XX.X pts | 🔴/🟡/🟢 |

**Status indicators:**
- 🔴 Critical (< 60) - Immediate attention required
- 🟡 Needs Work (60-79) - Prioritize improvements
- 🟢 Good (80-100) - Minor optimizations only

### 3. Detailed Findings

For each issue, provide:

**Format:**
```
Issue #X: [One-sentence description]
Category: [1-5]
Severity: [Critical/High/Medium/Low]
Confidence: [High/Medium/Low]
Score Impact: −XX points

Evidence:
[How you identified this - URL, observation, data point]

Why it matters:
[Plain-language explanation of impact on rankings/traffic/UX]

Recommendation:
[What to do - not how to implement unless asked]

Example:
Before: [Current state]
After: [Desired state]
```

**Group findings by category**, not by severity. This makes it easier to understand related issues.

### 4. Prioritized Action Plan

Organize recommendations into 4 tiers:

#### Tier 1: Critical Blockers (Fix Immediately)

Issues that prevent search engines from crawling/indexing or severely harm user experience.

**Format:**
| Priority | Issue | Expected Impact | Difficulty |
|----------|-------|-----------------|------------|
| 🔴 1 | Fix robots.txt blocking /products/ | +25 points, 800+ pages indexed | Easy (10 min) |
| 🔴 2 | Implement HTTPS site-wide | +20 points, security & rankings | Medium (2-4 hours) |

**Expected score after Tier 1 fixes:** XX → XX (+XX points)

#### Tier 2: High-Impact Improvements

Issues affecting multiple pages or core user experience.

**Format:**
| Priority | Issue | Expected Impact | Difficulty |
|----------|-------|-----------------|------------|
| 🟡 3 | Optimize LCP (hero image) | +12 points, better rankings | Medium (2 hours) |
| 🟡 4 | Fix 120 duplicate title tags | +10 points, template fix | Medium (4 hours) |

**Expected score after Tier 2 fixes:** XX → XX (+XX points)

#### Tier 3: Quick Wins

Easy fixes with measurable improvement.

| Priority | Issue | Expected Impact | Difficulty |
|----------|-------|-----------------|------------|
| 🟢 5 | Add alt text to images | +5 points | Easy (1 hour) |
| 🟢 6 | Fix 12 broken internal links | +3 points | Easy (30 min) |

**Expected score after Tier 3 fixes:** XX → XX (+XX points)

#### Tier 4: Long-Term Opportunities

Strategic investments requiring more resources.

| Priority | Issue | Expected Impact | Difficulty |
|----------|-------|-----------------|------------|
| 🔵 7 | Build backlink profile | +8 points, authority growth | Hard (ongoing) |
| 🔵 8 | Refresh 50+ outdated articles | +5 points | Hard (weeks) |
| 🔵 9 | Implement comprehensive schema | +3 points | Medium (days) |

### 5. Implementation Notes

**Tools needed:**
- List specific tools for implementation (Search Console, Screaming Frog, etc.)

**Measurement plan:**
- How to verify fixes worked
- What metrics to track
- Expected timeline for improvements

**Example:**
> "After implementing Tier 1 fixes, use Google Search Console to submit the sitemap and monitor indexation over 2-3 weeks. Track indexed pages via `site:domain.com` queries. Core Web Vitals should be retested 1 week after image optimization using PageSpeed Insights."

---

## Important Reminders

### Evidence-Based Analysis
- Base findings on direct observation or data
- Don't assume issues exist - verify them
- Cite specific URLs, screenshots, or tool reports
- If you can't verify, state confidence level

### Tool Limitations
- Don't rely on a single tool for conclusions
- Different tools measure differently
- Always cross-reference findings
- Manual checks > automated-only audits

### Score Accuracy
- The score reflects SEO readiness, not guaranteed rankings
- Competition and algorithm changes aren't scored
- A high score with critical issues is invalid
- Be honest about out-of-scope categories

### Communication Style
- Use plain language, not jargon
- Explain "why" not just "what"
- Prioritize by business impact, not technical severity alone
- Be specific: "Fix X" not "Improve SEO"

### Scope Management
If the user asks for implementation help, switch from diagnostic to prescriptive mode and provide step-by-step fixes.

---

## Example Audit Output

### Executive Summary

This e-commerce site scores 58/100 (Poor), primarily due to critical indexation issues. The robots.txt file is blocking 1,200+ product pages from being crawled, and 68% of the site is not in Google's index. Mobile Core Web Vitals are failing with LCP at 5.2 seconds on product pages. Fixing these two critical issues would raise the score to approximately 78/100 (Good). The site has solid on-page optimization (title tags, meta descriptions) but needs technical foundation improvements urgently.

### SEO Health Dashboard

**Overall Score:** 58/100 (Poor)

| Category | Score | Weight | Contribution | Status |
|----------|-------|--------|--------------|--------|
| Crawlability & Indexation | 45/100 | 30% | 13.5 pts | 🔴 Critical |
| Technical Foundations | 52/100 | 25% | 13.0 pts | 🔴 Critical |
| On-Page Optimization | 78/100 | 20% | 15.6 pts | 🟡 Good |
| Content Quality & E-E-A-T | 65/100 | 15% | 9.8 pts | 🟡 Needs Work |
| Authority & Trust | 70/100 | 10% | 7.0 pts | 🟡 Good |

### Detailed Findings

#### Category 1: Crawlability & Indexation (45/100) 🔴

**Issue #1: Critical Robots.txt Misconfiguration**
Severity: Critical | Confidence: High | Score Impact: −30 points

Evidence:
```
robots.txt at https://example.com/robots.txt contains:
User-agent: *
Disallow: /products/
```
This blocks all 1,200 product pages from being crawled.

Why it matters:
Your entire product catalog is invisible to Google. No products can rank, no matter how well-optimized they are. This is costing you thousands of potential organic visits.

Recommendation:
Remove the `/products/` disallow rule from robots.txt immediately. Only block admin, cart, and checkout URLs.

Before:
```
Disallow: /products/
```

After:
```
Disallow: /admin/
Disallow: /cart/
Disallow: /checkout/
```

---

**Issue #2: Sitemap Contains Noindexed URLs**
Severity: High | Confidence: High | Score Impact: −10 points

Evidence:
Sitemap at https://example.com/sitemap.xml includes 340 URLs that have `<meta name="robots" content="noindex">` tags.

Why it matters:
Sitemaps should only contain pages you want indexed. Including noindexed pages wastes crawl budget and confuses search engines about which pages are important.

Recommendation:
Regenerate the sitemap to exclude noindexed pages, parameterized URLs, and pagination URLs beyond page 1.

---

**Issue #3: Deep Crawl Depth on Important Pages**
Severity: Medium | Confidence: High | Score Impact: −5 points

Evidence:
15 high-value product pages require 5-6 clicks from the homepage to reach. Example: `/products/electronics/computers/laptops/gaming/high-end/product-123`

Why it matters:
Pages deeper than 3-4 clicks get crawled less frequently and receive less link equity. These pages may rank lower than they should.

Recommendation:
Link to top-selling or high-margin products directly from the homepage or main category pages. Create a "Featured Products" section with direct links.

---

#### Category 2: Technical Foundations (52/100) 🔴

**Issue #4: Poor LCP on Product Pages**
Severity: Critical | Confidence: High | Score Impact: −15 points

Evidence:
PageSpeed Insights shows LCP of 5.2 seconds on mobile for product pages. Main cause: unoptimized hero images (1.8MB JPEG files).

Why it matters:
LCP > 4 seconds is a Core Web Vitals failure. Google uses this as a ranking factor. Users also bounce from slow pages - your conversion rate is likely suffering.

Recommendation:
Convert product hero images to WebP format, compress to < 200KB, add `fetchpriority="high"`, and ensure dimensions are specified.

---

**Issue #5: No HTTPS on Subdomain**
Severity: High | Confidence: High | Score Impact: −10 points

Evidence:
Blog subdomain (blog.example.com) still serves content over HTTP. Main domain is HTTPS.

Why it matters:
Mixed HTTP/HTTPS across subdomains creates trust issues and security warnings. Google prioritizes HTTPS sites in rankings.

Recommendation:
Install SSL certificate on blog subdomain and redirect all HTTP traffic to HTTPS with 301 redirects.

---

[Continue with remaining categories...]

### Prioritized Action Plan

#### Tier 1: Critical Blockers (Fix Immediately)

| Priority | Issue | Expected Impact | Difficulty | Time |
|----------|-------|-----------------|------------|------|
| 🔴 1 | Fix robots.txt - remove /products/ block | +30 pts, 1,200 pages indexed | Easy | 5 min |
| 🔴 2 | Optimize LCP - compress hero images | +15 pts, pass Core Web Vitals | Medium | 2 hours |
| 🔴 3 | Add HTTPS to blog subdomain | +10 pts, security compliance | Medium | 3 hours |

**Expected score after Tier 1:** 58 → 83 (+25 points)

#### Tier 2: High-Impact Improvements

| Priority | Issue | Expected Impact | Difficulty | Time |
|----------|-------|-----------------|------------|------|
| 🟡 4 | Clean sitemap - remove noindexed URLs | +10 pts, better crawl efficiency | Easy | 1 hour |
| 🟡 5 | Improve site architecture - reduce crawl depth | +5 pts, better internal linking | Medium | 4 hours |
| 🟡 6 | Add author bios to blog posts | +5 pts, E-E-A-T improvement | Easy | 2 hours |

**Expected score after Tier 2:** 83 → 90 (+7 points)

#### Tier 3: Quick Wins

| Priority | Issue | Expected Impact | Difficulty | Time |
|----------|-------|-----------------|------------|------|
| 🟢 7 | Add structured data to products | +3 pts, rich snippets | Easy | 1 hour |
| 🟢 8 | Fix 8 broken internal links | +2 pts, better UX | Easy | 30 min |

**Expected score after Tier 3:** 90 → 93 (+3 points)

#### Tier 4: Long-Term Opportunities

| Priority | Issue | Expected Impact | Difficulty | Time |
|----------|-------|-----------------|------------|------|
| 🔵 9 | Build backlink strategy | +5 pts, authority growth | Hard | Ongoing |
| 🔵 10 | Create content hub for top keywords | +5 pts, topical authority | Hard | 2-3 weeks |

### Implementation Plan

**Week 1: Critical fixes**
1. Update robots.txt (Day 1)
2. Optimize images and fix LCP (Days 1-2)
3. Implement HTTPS on subdomain (Day 3)
4. Submit updated sitemap to Search Console (Day 4)

**Week 2: High-impact improvements**
1. Clean sitemap regeneration
2. Internal linking improvements
3. Add author bios and E-E-A-T signals

**Weeks 3-4: Quick wins + monitoring**
1. Implement structured data
2. Fix broken links
3. Monitor indexation and Core Web Vitals

**Measurement:**
- Track indexed pages: `site:example.com` (weekly)
- Monitor Core Web Vitals: PageSpeed Insights (weekly)
- Check Search Console for crawl errors (daily)
- Organic traffic baseline vs. 30-day post-fix comparison

**Tools needed:**
- Google Search Console (verify fixes, submit sitemap)
- PageSpeed Insights (verify LCP improvements)
- Screaming Frog or Sitebulb (sitemap regeneration)
- Chrome DevTools (verify HTTPS implementation)

**Expected timeline for results:**
- Indexation improvements: 2-3 weeks
- Core Web Vitals: 1 week to verify, 2-4 weeks for ranking impact
- Organic traffic lift: 4-6 weeks after all Tier 1-2 fixes