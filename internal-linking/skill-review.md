# Internal Linking Optimizer — Skill Review

## Issues Found

### 1. No YAML Frontmatter
The skill lacks the required `---` frontmatter with `name` and `description` fields. This means it won't trigger properly — the description in frontmatter is the primary mechanism Claude uses to decide when to load a skill.

### 2. Way Too Long (~400+ lines)
The skill-creator guide recommends keeping SKILL.md under 500 lines, but more importantly, **most of this skill is output templates, not instructions**. There are massive tables that are essentially copy-paste scaffolding. This wastes context window and makes the model rigid — it'll try to fill every table even when it doesn't make sense for the user's request.

### 3. Templates Over Thinking
The original skill is ~80% output templates and ~20% actual guidance. This inverts the right ratio. A good skill explains *what to think about and why*, not *exactly what markdown to paste*. LLMs are smart — give them the reasoning and let them format appropriately for each situation.

### 4. No Scope Gate
The skill jumps straight into analysis without asking what the user actually needs. Internal linking for a 20-page site is very different from a 10,000-page site. There's no triage step.

### 5. Connector Placeholders Are Confusing
The `~~web crawler` and `~~analytics` notation isn't standard. The skill should just describe what data it needs and how to get it, adapting to what's available.

### 6. Validation Checkpoints at the End Are Good
The input/output validation section is useful — worth keeping in a leaner form.

### 7. No Prioritization Framework
The skill treats all recommendations equally. It should help the user focus on highest-impact linking changes first.

## What to Keep
- The core analysis areas (orphan pages, anchor text, topic clusters, link opportunities)
- The example at the end (good, concrete)
- Validation checkpoints concept
- Implementation best practices (anchor text distribution guidelines)

## What to Cut
- All the giant output template tables (let the model format based on context)
- Redundant section headers
- The overly detailed navigation analysis section (rarely the main ask)

## What to Add
- Proper YAML frontmatter with pushy description
- Scope gate / triage step
- Prioritization logic (impact-based)
- Explanation of *why* each analysis matters for SEO
