# Translation Framework
## Making Atlas Accessible in 10+ Languages

### Vision

Distributed systems knowledge shouldn't be limited by language barriers. Every engineer, regardless of their native language, should have access to world-class learning resources.

**Core Principle**: Translation is not just converting words—it's adapting knowledge for cultural and technical contexts.

### Priority Languages (Phase 1: Year 1)

Based on global software engineering population, cloud infrastructure adoption, and community demand:

1. **Mandarin Chinese (中文)** - 500M+ potential users
2. **Spanish (Español)** - 460M+ potential users
3. **Hindi (हिन्दी)** - 300M+ potential users
4. **Portuguese (Português)** - 260M+ potential users (Brazil focus)
5. **Japanese (日本語)** - 125M+ potential users
6. **German (Deutsch)** - 100M+ potential users
7. **French (Français)** - 80M+ potential users
8. **Korean (한국어)** - 77M+ potential users
9. **Russian (Русский)** - 150M+ potential users
10. **Arabic (العربية)** - 100M+ potential users

**Selection Criteria**:
- Large software engineering community
- Growing cloud infrastructure market
- Active tech ecosystem
- Limited high-quality resources in native language
- Community volunteer availability

### Translation Priority Tiers

## TIER 1: CRITICAL (Translate First)

### Core Study Plan (Priority: Immediate)
- [ ] Main README (atlas-study-plan/README.md)
- [ ] Phase overviews (5 files)
- [ ] Life OS Integration
- [ ] Learning techniques guide
- [ ] Assessment framework

**Target**: Complete within Month 1 for each language
**Why**: Enables learners to start immediately

### Foundation Documentation (Priority: Month 1-2)
- [ ] Foundation concepts (20 pages)
- [ ] Getting started guides
- [ ] Common patterns overview
- [ ] Glossary of key terms

**Target**: Complete within Month 2
**Why**: Core conceptual understanding

## TIER 2: HIGH-VALUE (Translate Second)

### Company Architectures (Priority: Month 3-6)
- [ ] Top 10 companies (80 diagrams)
  - Netflix, Uber, Amazon, Google, Meta
  - Microsoft, LinkedIn, Twitter, Stripe, Spotify
- [ ] Architecture deep-dive text
- [ ] Cost breakdowns
- [ ] Scale evolution stories

**Target**: 2 companies per month per language
**Why**: Most engaging content, high community interest

### Incident Anatomies (Priority: Month 7-9)
- [ ] Top 20 incidents (most impactful)
- [ ] Incident analysis text
- [ ] Recovery procedures
- [ ] Lessons learned sections

**Target**: 10 incidents per month per language
**Why**: Practical learning from real failures

## TIER 3: COMPREHENSIVE (Translate Third)

### Remaining Content (Priority: Month 10-12)
- [ ] Remaining company architectures (160 diagrams)
- [ ] All incident reports (80 more)
- [ ] Debugging guides (100 pages)
- [ ] Performance profiles (80 pages)
- [ ] Advanced patterns and comparisons

**Target**: Ongoing, community-driven
**Why**: Completeness and depth

## TRANSLATION WORKFLOW

### Phase 1: Preparation (Before Translation)

#### Content Audit
1. **Identify Translatable Content**:
   - Markdown text: 100% translatable
   - Diagram labels: 80% translatable
   - Code comments: 50% translatable (optional)
   - Technical terms: Document standard translations

2. **Create Translation Memory**:
   - Glossary of technical terms
   - Standard phrase translations
   - Company name handling rules
   - Number and date formatting

3. **Extract Strings**:
```bash
# Extract translatable strings from markdown
python scripts/extract_i18n_strings.py \
  --input docs/ \
  --output translations/en/strings.json
```

#### Translator Recruitment

**Volunteer Translator Profile**:
- Fluent in target language (native preferred)
- Technical background (software engineering)
- Familiar with distributed systems concepts
- Available 5-10 hours/week
- Committed for 6+ months

**Recruitment Channels**:
- Atlas Discord community
- LinkedIn posts in target language
- Local tech communities
- University CS departments
- Tech meetups in target regions

**Translator Benefits**:
- Recognition on translated pages
- Translation contributor badge
- Priority access to new content
- Certificate of contribution
- Portfolio building

### Phase 2: Translation (Active Work)

#### Translation Guidelines Document

**For Each Language, Provide**:

```markdown
# Translation Guidelines: [Language Name]

## Technical Term Handling

### Terms to Translate
- Common concepts: consistency, availability, partition tolerance
- Action verbs: deploy, scale, monitor
- General nouns: server, database, cache

### Terms to Keep in English
- Proper nouns: AWS, Google Cloud, Kubernetes
- Specific technologies: PostgreSQL, Redis, Kafka
- Company names: Netflix, Uber, Amazon
- Well-known acronyms: REST, gRPC, TCP/IP

### Hybrid Approach (English + Native)
Format: "English Term (Native Translation)"
- Microservices (微服务) [Chinese]
- Load Balancer (লোড ব্যালান্সার) [Bengali]

## Formatting Conventions

### Numbers
- Use native number system: [Yes/No]
- Thousands separator: [comma/period/space]
- Decimal separator: [period/comma]

### Dates
- Format: [YYYY-MM-DD / DD/MM/YYYY / MM/DD/YYYY]
- Example: 2024-01-15

### Currency
- Primary: USD (with conversion note if helpful)
- Local equivalent: Show in parentheses

## Cultural Adaptations

### Examples
- Replace US-centric examples with local equivalents
- Use locally popular services where applicable
- Adapt analogies to local context

### Tone
- Formal vs. Informal: [Guidance]
- Personal pronouns: [You/formal/informal]
- Active vs. Passive voice: [Preference]

## Quality Standards

### Accuracy
- Technical accuracy is paramount
- When unsure, ask in #translation-help channel
- Reference authoritative sources in target language

### Consistency
- Use translation memory for standard terms
- Maintain consistent voice throughout
- Follow established patterns from previous translations

### Readability
- Optimize for native speakers, not literal translation
- Preserve examples and analogies (adapt if needed)
- Keep paragraphs concise
```

#### Translation Tools

**Recommended Platform: GitLocalize**
- Integrates with GitHub
- Shows context around strings
- Translation memory
- Review workflow
- Progress tracking

**Alternative: Custom System**
```
translations/
├── en/                          # English (source)
│   ├── study-plan/
│   │   ├── README.md
│   │   └── phases/
│   └── docs/
│       └── foundation/
├── zh/                          # Chinese
│   ├── study-plan/
│   │   ├── README.md
│   │   └── phases/
│   └── docs/
├── es/                          # Spanish
├── hi/                          # Hindi
└── ...
```

**Translation Workflow Script**:
```python
# scripts/translation_workflow.py

import os
import json
from pathlib import Path

class TranslationManager:
    def __init__(self, source_lang='en'):
        self.source_lang = source_lang
        self.translations_dir = Path('translations')

    def extract_content(self, file_path):
        """Extract translatable content from markdown."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into translatable and non-translatable sections
        sections = {
            'headers': [],
            'paragraphs': [],
            'lists': [],
            'code_comments': [],
            'diagram_labels': []
        }

        # Parser implementation...
        return sections

    def create_translation_task(self, file_path, target_lang):
        """Create translation task for a file."""
        content = self.extract_content(file_path)

        task = {
            'source_file': str(file_path),
            'target_lang': target_lang,
            'target_file': self.get_target_path(file_path, target_lang),
            'content': content,
            'status': 'pending',
            'assigned_to': None,
            'reviewed_by': None,
            'completed': False
        }

        return task

    def get_target_path(self, source_path, target_lang):
        """Get translated file path."""
        return self.translations_dir / target_lang / source_path

    def validate_translation(self, source_path, translated_path):
        """Validate translated file maintains structure."""
        validations = {
            'links_preserved': False,
            'structure_maintained': False,
            'diagrams_updated': False,
            'formatting_correct': False
        }

        # Validation logic...
        return validations

    def track_progress(self, target_lang):
        """Track translation progress for language."""
        all_files = list(Path('docs').rglob('*.md'))
        total_files = len(all_files)

        translated_files = list(
            (self.translations_dir / target_lang / 'docs').rglob('*.md')
        )
        completed = len(translated_files)

        progress = {
            'language': target_lang,
            'total_files': total_files,
            'translated': completed,
            'percentage': (completed / total_files * 100) if total_files > 0 else 0,
            'remaining': total_files - completed
        }

        return progress
```

### Phase 3: Review (Quality Assurance)

#### Two-Tier Review Process

**Tier 1: Technical Review**
- Verify technical accuracy
- Check term consistency
- Ensure examples are correct
- Validate diagram translations

**Reviewer Requirements**:
- Native speaker of target language
- 5+ years software engineering experience
- Distributed systems knowledge
- Available for 3-5 hours/week review

**Tier 2: Language Review**
- Check grammar and style
- Ensure natural flow
- Verify cultural appropriateness
- Polish for readability

**Reviewer Requirements**:
- Native speaker with strong writing skills
- Technical background helpful but not required
- Available 2-3 hours/week

#### Review Checklist

```markdown
# Translation Review Checklist

## Technical Accuracy
- [ ] All technical terms correctly translated/preserved
- [ ] Code examples remain functional
- [ ] Diagram labels are accurate
- [ ] Links work correctly
- [ ] Metrics and numbers preserved

## Language Quality
- [ ] Grammar is correct
- [ ] Style is consistent with guidelines
- [ ] Tone is appropriate
- [ ] Flows naturally for native speakers
- [ ] Cultural adaptations are suitable

## Formatting
- [ ] Markdown formatting preserved
- [ ] Headers maintain hierarchy
- [ ] Lists formatted correctly
- [ ] Code blocks render properly
- [ ] Images display correctly

## Completeness
- [ ] All sections translated (no English remnants)
- [ ] Attribution preserved
- [ ] References updated if applicable
- [ ] Meta information (title, description) translated

## Context
- [ ] Maintains original meaning
- [ ] Examples are clear
- [ ] Analogies work in target culture
- [ ] Humor/idioms adapted appropriately

**Reviewer**: [Name]
**Date**: [YYYY-MM-DD]
**Status**: [Approved / Needs Revision / Rejected]
**Comments**: [Detailed feedback]
```

### Phase 4: Publication (Deployment)

#### Multi-Language Site Structure

**Option 1: Subdirectories**
```
site.atlas-community.org/
├── en/                    # English (default)
├── zh/                    # Chinese
├── es/                    # Spanish
└── ...
```

**Option 2: Subdomains**
```
atlas-community.org        # English (default)
zh.atlas-community.org     # Chinese
es.atlas-community.org     # Spanish
```

**Option 3: Language Parameter**
```
atlas-community.org?lang=en
atlas-community.org?lang=zh
```

**Recommended**: Option 1 (subdirectories) for SEO and simplicity

#### Language Switcher Implementation

```html
<!-- Language switcher component -->
<div class="language-switcher">
  <button class="current-language">
    <img src="/flags/en.svg" alt="English">
    English
  </button>
  <div class="language-menu">
    <a href="/en/" class="language-option">
      <img src="/flags/en.svg" alt="English">
      English
    </a>
    <a href="/zh/" class="language-option">
      <img src="/flags/zh.svg" alt="中文">
      中文 (Chinese)
    </a>
    <a href="/es/" class="language-option">
      <img src="/flags/es.svg" alt="Español">
      Español (Spanish)
    </a>
    <!-- More languages -->
  </div>
</div>
```

#### SEO for Multilingual Content

**HTML Lang Attributes**:
```html
<html lang="zh">
  <head>
    <!-- Alternate language versions -->
    <link rel="alternate" hreflang="en" href="https://atlas-community.org/en/page" />
    <link rel="alternate" hreflang="zh" href="https://atlas-community.org/zh/page" />
    <link rel="alternate" hreflang="es" href="https://atlas-community.org/es/page" />
    <link rel="alternate" hreflang="x-default" href="https://atlas-community.org/en/page" />
  </head>
</html>
```

**Automatic Language Detection**:
```javascript
// Detect user's preferred language
function detectLanguage() {
  // Check localStorage
  let savedLang = localStorage.getItem('atlas_language');
  if (savedLang) return savedLang;

  // Check browser language
  let browserLang = navigator.language || navigator.userLanguage;
  browserLang = browserLang.split('-')[0]; // en-US -> en

  // Check if we support this language
  const supportedLangs = ['en', 'zh', 'es', 'hi', 'pt', 'ja', 'de', 'fr', 'ko', 'ru', 'ar'];
  if (supportedLangs.includes(browserLang)) {
    return browserLang;
  }

  // Default to English
  return 'en';
}

// Redirect to correct language version
window.onload = function() {
  let currentLang = document.documentElement.lang;
  let preferredLang = detectLanguage();

  if (currentLang !== preferredLang) {
    let currentPath = window.location.pathname;
    let newPath = currentPath.replace(`/${currentLang}/`, `/${preferredLang}/`);
    window.location.href = newPath;
  }
};
```

## CULTURAL ADAPTATION

### Technical Examples

**US-Centric Example (English)**:
"Imagine Walmart's inventory system during Black Friday..."

**Chinese Adaptation**:
"Imagine Alibaba's inventory system during Singles' Day (11.11)..."

**Spanish Adaptation (Latin America)**:
"Imagine Mercado Libre's inventory system during Hot Sale..."

### Company References

**Global Companies (Keep)**:
- Netflix, Amazon, Google, Microsoft
- These are universally recognized

**Regional Alternatives (Add)**:
- China: Alibaba, Tencent, Baidu, ByteDance
- Latin America: Mercado Libre, Nubank, Rappi
- India: Flipkart, Paytm, Swiggy, Zomato
- Japan: Rakuten, LINE, Mercari
- Southeast Asia: Grab, Gojek, Sea (Shopee)

### Measurement Units

**Keep Metric System Primary**:
- Use GB, TB (not GiB, TiB unless specifically needed)
- Use milliseconds, seconds, minutes
- Use requests per second (universal)

**Add Regional Context When Helpful**:
- Currency conversions in parentheses
- Time zone examples using local major cities
- Scale references using local services

## TRANSLATION MANAGEMENT

### Contributor Roles

**Translator**:
- Translate content from English to target language
- Follow translation guidelines
- Use translation memory for consistency
- Commit: 5-10 hours/week

**Reviewer**:
- Review translated content for accuracy
- Provide constructive feedback
- Approve or request revisions
- Commit: 3-5 hours/week

**Language Coordinator**:
- Manage translation for specific language
- Recruit and onboard translators
- Maintain language-specific guidelines
- Track progress
- Commit: 5-8 hours/week

**Translation Manager** (Staff Role):
- Oversee all language translations
- Coordinate between language teams
- Maintain translation infrastructure
- Report on progress
- Commit: 15-20 hours/week

### Recognition and Rewards

**Translator Credits**:
- Name on translated pages footer
- Contributor profile page
- Translation badge on Discord
- LinkedIn recommendation
- Portfolio material

**Top Contributor Rewards**:
- Free access to premium features (if any)
- Conference tickets
- Official Atlas translator certificate
- Priority for mentorship program
- Speaking opportunities

### Progress Tracking Dashboard

**Language-Level Metrics**:
- Total pages to translate
- Pages translated
- Pages reviewed
- Pages published
- Percentage complete
- Estimated completion date

**Translator-Level Metrics**:
- Pages translated
- Quality score (from reviews)
- Response time
- Consistency rating
- Community appreciation

## ONGOING MAINTENANCE

### Content Update Workflow

When English content updates:
1. **Detection**: Automated script detects changes
2. **Notification**: Email to language coordinators
3. **Assessment**: Coordinator reviews impact
4. **Assignment**: Translator assigned to update
5. **Review**: Expedited review process
6. **Publication**: Updated translation published

### Deprecation Policy

**If Language Translation Stalls**:
- Month 1: Coordinator notification
- Month 2: Community call for volunteers
- Month 3: Mark as "Community Maintained"
- Month 6: Mark as "Maintenance Mode" (no new updates)
- Month 12: Archive (read-only, no updates)

### Quality Audits

**Quarterly Audit Process**:
1. Random sample 10% of translated pages
2. Expert review for accuracy
3. Community feedback analysis
4. Identify improvement areas
5. Provide feedback to translators
6. Update guidelines as needed

---

**Translation Philosophy**: Every engineer deserves access to world-class learning materials in their native language. Translation is not just conversion—it's inclusion.

**🌍 [BECOME A TRANSLATOR →](https://forms.atlas-community.org/translator-application)**
**📊 [VIEW TRANSLATION PROGRESS →](https://atlas-community.org/translations/dashboard)**
**💬 [JOIN TRANSLATION TEAM →](https://discord.gg/atlas-community#translations)**