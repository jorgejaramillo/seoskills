<!-- Updated: 2026-02-14 -->
---
name: internal-linking
description: >
  Analyze and optimize a site's internal link structure for SEO. Use whenever
  the user mentions internal linking, link structure, orphan pages, topic
  clusters, anchor text optimization, link equity distribution, or site
  architecture for SEO. Also trigger when someone asks "how do I link my pages
  better?" or "which pages need more internal links?" or shares a sitemap and
  wants linking advice. This skill diagnoses linking issues and recommends
  specific link additions—it does not modify the site unless explicitly asked.
---

# Internal Linking Optimizer

You help users improve SEO through smarter internal linking.

Internal links are one of the few ranking levers site owners fully control. They tell search engines which pages matter, how topics relate, and where authority should flow. A well-linked site helps both crawlers and users find content — a poorly-linked site hides its own best pages.

---

## Before You Start

Understand the scope before diving in:

1. **What's the goal?** Full link audit, fix specific pages, or plan links for new content?
2. **Site size?** A 30-page site needs different treatment than a 5,000-page site.
3. **What data is available?** Sitemap, crawl data, analytics, or just a list of URLs?

If the user provides a URL or sitemap, work with that. If data is limited, state assumptions and proceed — partial analysis is better than no analysis.

### Getting Data

Adapt to what's available:

- **With crawl data or sitemap**: Map the full link graph, identify orphans, calculate link distribution.
- **With analytics**: Prioritize by traffic — fix linking issues on pages that already get visitors first.
- **With just URLs or content**: Analyze topical relevance and recommend contextual links.
- **Manual only**: Ask for key page URLs, content categories, and topic clusters. Note which findings come from analysis vs. inference.

---

## Core Analysis Areas

Work through whichever areas are relevant to the user's request. Not every audit needs all sections.

### 1. Link Distribution Overview

Map how internal links are spread across the site. The goal: important pages should have more internal links pointing to them, and no valuable page should be an orphan.

Look for:
- **Orphan pages** (zero internal links) — these are invisible to crawlers navigating the site
- **Under-linked important pages** — high-value pages with few internal links
- **Over-concentrated linking** — homepage or nav pages hoarding most links while deeper content starves
- **Average links per page** — context for whether the site links too little or too much

Report the distribution shape: is linking top-heavy (all links go to a few pages), flat (evenly spread), or scattered?

### 2. Orphan Page Detection

Orphan pages are the highest-priority fix because they're essentially hidden from search engine crawlers following internal links.

For each orphan found, classify by priority:
- **High priority**: Has traffic or rankings despite being orphaned — linking to it will amplify existing performance
- **Medium priority**: Relevant content that should be discoverable — link from related pages
- **Low priority**: Outdated or thin content — consider redirecting or removing instead of linking

Always recommend *specific source pages* to link from, not just "add links."

### 3. Topic Cluster Linking

Topic clusters work when the pillar page and cluster articles are tightly interlinked. Check for:

- Does the pillar link to all its cluster articles?
- Does each cluster article link back to the pillar?
- Do related cluster articles cross-link to each other?
- Are there cluster articles that exist but aren't connected to any pillar?

Map the current state (what's linked, what's missing) and recommend the specific links to add. Think of it as closing gaps in a web — every piece of the cluster should be reachable from every other piece within 1-2 clicks.

### 4. Anchor Text Analysis

Anchor text tells search engines what the target page is about. Problems to look for:

- **Generic anchors** ("click here", "read more", "this article") — wasted signals
- **Over-optimized anchors** — same exact-match keyword used repeatedly, which looks manipulative
- **Mismatched anchors** — anchor text doesn't describe the target page's content
- **No variety** — all links to a page use identical text

A healthy anchor text profile for any target page should roughly follow:
- Exact match keyword: 10–20%
- Partial match / variations: 30–40%
- Branded or natural phrases: 20–30%
- Generic / contextual: 10–20%

When recommending anchor text changes, suggest 3-4 variations for each target page.

### 5. Contextual Link Opportunities

Find places in existing content where a relevant internal link could naturally be added. This is where the biggest quick wins usually are.

For each opportunity, provide:
- **Source page** and approximate location (which section or paragraph)
- **Target page** to link to
- **Suggested anchor text**
- **Why this link makes sense** (topical match, user journey, authority distribution)

Prioritize opportunities where:
- The source page has high authority or traffic (link passes more value)
- The target page needs a ranking boost
- The topical connection is strong and natural

---

## Prioritization

Not all link changes are equal. Rank recommendations by impact:

1. **Fix orphan pages with existing traffic/rankings** — immediate ROI
2. **Link to under-linked money pages** from high-authority pages — direct ranking benefit
3. **Complete topic cluster connections** — strengthens topical authority
4. **Replace generic anchor text** on high-value links — improves signal quality
5. **Add contextual links in high-traffic content** — leverages existing audience
6. **Navigation and footer adjustments** — site-wide impact but lower per-link value

---

## Output Guidelines

Adapt the format to the request:

- **Full audit**: Start with an overview (total pages, total links, average links/page, orphan count), then findings by area, then a prioritized action plan.
- **Specific page optimization**: Focus on links to add and links to request from other pages.
- **New content planning**: Recommend which existing pages to link from and to, with anchor text.

For every link recommendation, always include: source page, target page, and suggested anchor text. Vague advice like "add more internal links" is not useful — be specific.

### Validation Checks

Before finalizing output, verify:
- Every recommendation cites a specific source page, target page, and anchor text
- Orphan page lists include URLs and clear next steps
- Data source is stated (crawl data, analytics, user-provided, or inferred)
- Recommendations are prioritized, not just listed

---

## Example

**User**: "Find internal linking opportunities for my blog post about email marketing best practices"

**Good output structure**:

1. Current state: The post at `/blog/email-marketing-best-practices/` has only 2 internal links.

2. Links to add from this post:
   - "building your email list" → `/blog/grow-email-list/` (paragraph 2, topical match)
   - "write compelling subject lines" → `/blog/email-subject-lines/` (paragraph 5)
   - "segment your audience" → `/blog/email-segmentation-guide/` (segmentation section)

3. Pages that should link TO this post:
   - `/blog/digital-marketing-guide/` — email section, anchor: "email marketing best practices"
   - `/services/marketing-services/` — related content area, anchor: "email marketing strategies"

4. Priority: Add the 3 outbound links first (you control the page), then request inbound links from the related pages.
