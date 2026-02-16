<!-- Updated: 2026-02-14 -->
---
name: seo-images
description: >
  Image optimization analysis for SEO and performance. Checks alt text, file
  sizes, formats, responsive images, lazy loading, and CLS prevention. Use when
  user says "image optimization", "alt text", "image SEO", "image size",
  "optimize images", "image performance", or "image audit".
---

# Image Optimization Analysis

Analyze images on a webpage or site for SEO and performance optimization. Provide actionable recommendations sorted by impact.

## Input

Expects one of:
- URL to analyze (fetches and parses HTML)
- HTML file or content
- List of image URLs to audit

## Analysis Checklist

### 1. Alt Text Quality

Every `<img>` must have descriptive alt text (except decorative images with `role="presentation"` or `alt=""`).

**Quality criteria:**
- Describes image content, not filename
- Natural keyword inclusion (no stuffing)
- Length: 10-125 characters
- Context-appropriate

**Examples:**

| ✅ Good | ❌ Bad | Why |
|---------|--------|-----|
| "Chocolate labrador puppy playing with tennis ball in backyard" | "IMG_2847.jpg" | Descriptive vs filename |
| "Graph showing 40% increase in organic traffic from Q3 to Q4" | "graph chart data analytics metrics" | Natural vs keyword stuffing |
| "Black leather office chair with ergonomic lumbar support" | "Click here to see more" | Descriptive vs call-to-action |
| "Sunset over Golden Gate Bridge, San Francisco" | "Photo" | Specific vs generic |

**Decorative images** (dividers, backgrounds, spacers):
```html
<img src="divider.png" role="presentation" alt="">
```

### 2. File Size Optimization

**Tiered thresholds by image type:**

| Image Category | Target | Warning | Critical | Examples |
|----------------|--------|---------|----------|----------|
| Thumbnails / Icons | < 50KB | > 100KB | > 200KB | Product thumbnails, author avatars, category icons |
| Content images | < 100KB | > 200KB | > 500KB | Blog photos, product images, gallery items |
| Hero / Banner images | < 200KB | > 300KB | > 700KB | Above-fold hero images, full-width banners |
| Background images | < 150KB | > 250KB | > 600KB | Section backgrounds, pattern fills |

**Flag images exceeding thresholds and estimate compression savings.**

### 3. Modern Format Usage

**Recommended format hierarchy:**

| Format | Browser Support | Compression | Use Case | File Size Comparison |
|--------|-----------------|-------------|----------|---------------------|
| AVIF | 93.8% | Best | Photos, complex images | 50% smaller than JPEG |
| WebP | 95.3% | Excellent | Default for most images | 25-35% smaller than JPEG |
| JPEG | 100% | Good | Fallback for photos | Baseline |
| PNG | 100% | Lossless | Graphics with transparency | Larger than WebP |
| SVG | 100% | Vector | Icons, logos, simple graphics | Scales without quality loss |

**Preferred `<picture>` element pattern:**

```html
<picture>
  <source srcset="hero-image.avif" type="image/avif">
  <source srcset="hero-image.webp" type="image/webp">
  <img src="hero-image.jpg" alt="Modern living room with minimalist furniture" 
       width="1200" height="675" loading="lazy" decoding="async">
</picture>
```

**Flag:**
- JPEGs/PNGs that should be WebP/AVIF
- Missing fallback formats in `<picture>` elements
- Estimate conversion savings

### 4. Responsive Images Implementation

Check for proper `srcset` and `sizes` attributes to serve appropriately sized images.

**Example:**
```html
<img
  src="product-800.webp"
  srcset="product-400.webp 400w, 
          product-800.webp 800w, 
          product-1200.webp 1200w,
          product-1600.webp 1600w"
  sizes="(max-width: 640px) 100vw,
         (max-width: 1024px) 50vw,
         33vw"
  alt="Wireless noise-cancelling headphones in matte black"
  width="800"
  height="600"
  loading="lazy"
>
```

**Flag images without:**
- `srcset` for images > 400px wide
- `sizes` attribute matching layout breakpoints
- Device pixel ratio variants (1x, 2x for retina)

### 5. Lazy Loading Strategy

**Critical rules:**
- ✅ `loading="lazy"` on below-fold images
- ❌ NEVER lazy-load LCP (Largest Contentful Paint) images
- ❌ NEVER lazy-load above-fold images
- ✅ Native lazy loading preferred over JavaScript libraries

**Examples:**

```html
<!-- ❌ BAD - Lazy loading hero image hurts LCP -->
<img src="hero.webp" loading="lazy" alt="...">

<!-- ✅ GOOD - Hero image loads immediately -->
<img src="hero.webp" fetchpriority="high" alt="..." width="1200" height="630">

<!-- ✅ GOOD - Below-fold image lazy loads -->
<img src="testimonial.webp" loading="lazy" decoding="async" alt="..." width="400" height="400">
```

**Flag:**
- Hero/above-fold images with `loading="lazy"` (critical error)
- Below-fold images without `loading="lazy"` (missed optimization)

### 6. LCP Image Optimization

**For hero/banner images:**

```html
<img src="hero-banner.webp" 
     fetchpriority="high" 
     alt="Professional kitchen remodeling services in Seattle"
     width="1920" 
     height="1080">
```

**Critical:**
- Add `fetchpriority="high"` to LCP image
- NO `loading="lazy"` on LCP image
- Use optimal format (WebP/AVIF with JPEG fallback)
- Include explicit dimensions

### 7. Async Decoding for Non-Critical Images

Prevent image decoding from blocking main thread:

```html
<img src="gallery-item-3.webp" 
     alt="Finished basement renovation with home theater setup" 
     width="600" 
     height="400" 
     loading="lazy" 
     decoding="async">
```

Add `decoding="async"` to all images except LCP image.

### 8. CLS Prevention

**Every image needs dimensions to prevent layout shift:**

```html
<!-- ✅ GOOD - Explicit dimensions -->
<img src="author-photo.webp" width="80" height="80" alt="Sarah Chen, Content Director">

<!-- ✅ GOOD - CSS aspect ratio -->
<img src="featured-image.webp" style="aspect-ratio: 16/9" alt="...">

<!-- ✅ GOOD - Responsive with intrinsic aspect ratio -->
<img src="hero.webp" 
     width="1200" 
     height="675" 
     style="width: 100%; height: auto;" 
     alt="...">

<!-- ❌ BAD - No dimensions -->
<img src="blog-image.webp" alt="...">
```

**Flag all images without:**
- `width` and `height` attributes, OR
- CSS `aspect-ratio` property

### 9. SEO-Friendly File Naming

**Naming conventions:**
- Descriptive, hyphenated, lowercase
- Include relevant keywords
- No special characters or spaces
- Extension matches actual format

**Examples:**

| ✅ Good | ❌ Bad |
|---------|--------|
| `blue-nike-running-shoes-mens.webp` | `IMG_1234.jpg` |
| `kitchen-remodel-before-after.webp` | `image-final-v2.png` |
| `seo-traffic-growth-chart-2024.webp` | `Screen Shot 2024-01-15.png` |
| `chocolate-cake-recipe-close-up.webp` | `DSC_0456.JPG` |

**Flag:**
- Generic names (IMG_, DSC_, image_, photo_)
- Uppercase extensions
- Dates or version numbers in filenames
- Spaces or special characters

### 10. CDN and Delivery Optimization

**Check for:**
- Images served from CDN (different domain)
- Cache headers (`Cache-Control`, `Expires`)
- Compression headers (`Content-Encoding: gzip`)
- Geographic distribution

**Example CDN usage:**
```html
<!-- ✅ Served from CDN -->
<img src="https://cdn.example.com/images/product-photo.webp" alt="...">

<!-- ❌ Served from origin -->
<img src="https://www.example.com/uploads/product-photo.jpg" alt="...">
```

## Output Format

### Executive Summary

```
Image Audit Summary for: [URL/Page Name]
Analyzed: [XX] total images
Scan Date: [Date]

Critical Issues: X
Warnings: X
Estimated Savings: XXX KB (XX%)
```

### Metrics Dashboard

| Metric | Status | Count | Details |
|--------|--------|-------|---------|
| Total Images | ℹ️ | XX | - |
| Missing Alt Text | ❌ | XX | SEO issue |
| Poor Alt Quality | ⚠️ | XX | Generic/stuffed keywords |
| Oversized Images | ⚠️ | XX | > category threshold |
| Legacy Formats | ⚠️ | XX | JPEG/PNG → WebP/AVIF |
| Missing Dimensions | ❌ | XX | CLS risk |
| LCP Image Issues | ❌ | XX | Performance killer |
| Missing Lazy Loading | ⚠️ | XX | Below-fold images |
| Improper Lazy Loading | ❌ | XX | Above-fold images |
| No Responsive Images | ⚠️ | XX | Missing srcset |
| Poor File Names | ⚠️ | XX | Generic/non-descriptive |
| No CDN Usage | ⚠️ | XX | Delivery not optimized |

### Priority Optimization List

Sort by estimated impact (file size savings × page views):

| Priority | Image | Current | Issues | Recommendation | Est. Savings |
|----------|-------|---------|--------|----------------|--------------|
| 🔴 Critical | hero-banner.jpg (LCP) | 850KB JPEG | Lazy loaded, wrong format, oversized | Convert to WebP, add fetchpriority="high", remove lazy loading | 650KB + LCP improvement |
| 🔴 Critical | product-gallery-1.png | 1.2MB PNG | No dimensions, wrong format | Convert to WebP, add width/height | 900KB + prevent CLS |
| 🟡 High | testimonial-photos/*.jpg (12 images) | 200-400KB each | Legacy format, no lazy loading | Batch convert to WebP, add lazy loading | 2.1MB total |
| 🟡 High | blog-featured-*.jpg | 300-600KB JPEG | Missing srcset, oversized | Create responsive variants, optimize | 1.5MB total |
| 🟢 Medium | icon-*.png (24 images) | 15-50KB each | Could be SVG or smaller WebP | Convert to SVG or compress to WebP | 800KB total |

### Detailed Recommendations

**1. Critical: Fix LCP Image (Immediate Action)**

Current:
```html
<img src="hero-banner.jpg" loading="lazy" alt="Kitchen remodeling">
```

Optimized:
```html
<picture>
  <source srcset="hero-banner.avif" type="image/avif">
  <source srcset="hero-banner.webp" type="image/webp">
  <img src="hero-banner.jpg" 
       fetchpriority="high" 
       alt="Modern kitchen renovation with quartz countertops and stainless appliances"
       width="1920" 
       height="1080">
</picture>
```

**Impact:** Improved LCP score, 76% smaller file (850KB → 200KB)

**2. Convert Legacy Formats (High Impact)**

- Convert XX JPEG images to WebP: ~XX% savings (~XXX KB)
- Convert XX PNG images to WebP: ~XX% savings (~XXX KB)
- Total estimated savings: XXX KB

**3. Implement Responsive Images**

Add `srcset` and `sizes` to XX large images:
- Prevents mobile users from downloading desktop-sized images
- Estimated mobile data savings: XXX KB per page load

**4. Fix Alt Text Issues**

XX images need alt text improvements:

| Image | Current Alt | Issue | Suggested Alt |
|-------|-------------|-------|---------------|
| product-1.jpg | "image" | Too generic | "Stainless steel espresso machine with built-in grinder" |
| team-photo.jpg | "our team teamwork collaboration" | Keyword stuffing | "Marketing team collaborating in conference room" |
| logo.png | "click here" | Not descriptive | "Acme Construction logo" |

**5. Add Lazy Loading**

XX below-fold images should lazy load:
```html
<!-- Add to images below fold -->
loading="lazy" decoding="async"
```

**6. Fix CLS Issues**

XX images missing dimensions:
```html
<!-- Add explicit dimensions -->
width="800" height="600"
```

**7. Rename Files**

XX images have poor filenames:
- `IMG_2847.jpg` → `customer-testimonial-sarah-chen.webp`
- `Screen-Shot-2024.png` → `quarterly-revenue-growth-chart.webp`

### Estimated Performance Impact

**Before optimization:**
- Total image weight: XXX KB
- LCP: X.X seconds
- CLS: 0.XX

**After optimization:**
- Total image weight: XXX KB (XX% reduction)
- Estimated LCP improvement: -X.X seconds
- Estimated CLS improvement: -0.XX

**Page Speed Impact:**
- Mobile: XX% faster
- Desktop: XX% faster
- First Contentful Paint: -XX ms
- Total Blocking Time: -XX ms

## Implementation Checklist

- [ ] Convert hero/LCP image to WebP/AVIF with `fetchpriority="high"`
- [ ] Remove `loading="lazy"` from above-fold images
- [ ] Convert remaining JPEGs/PNGs to WebP
- [ ] Add dimensions (width/height) to all images
- [ ] Implement `srcset` for images > 400px wide
- [ ] Add `loading="lazy"` to below-fold images
- [ ] Add `decoding="async"` to non-LCP images
- [ ] Fix all missing/poor alt text
- [ ] Rename files with descriptive names
- [ ] Configure CDN if not already in use
- [ ] Set up automated image optimization pipeline

## Tools & Resources

**Recommended tools:**
- **Compression:** Squoosh.app, TinyPNG, ImageOptim
- **Format conversion:** cwebp (WebP), avifenc (AVIF)
- **Responsive images:** Cloudinary, Imgix, sharp (Node.js)
- **Testing:** Lighthouse, WebPageTest, Chrome DevTools
- **Bulk processing:** ImageMagick, sharp, Squoosh CLI

**Automation:**
- Set up build pipeline to auto-convert images
- Implement CDN with automatic format optimization
- Use responsive image generation in CMS