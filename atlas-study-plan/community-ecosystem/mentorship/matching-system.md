# Mentorship Matching System
## Building Transformative Mentor-Mentee Relationships

### Philosophy

Great mentorship isn't about finding someone who knows everything—it's about finding someone who cares about your growth and has navigated similar challenges. The best mentors remember what it was like to be where you are now.

**Core Principle**: Match on growth trajectory, not just current position.

### Mentorship Program Structure

## THREE-TIER MENTORSHIP MODEL

### Tier 1: Peer Mentorship (1-2 Years Ahead)
**Mentor Profile**: Recently completed Atlas, now applying knowledge
**Best For**: Tactical guidance, study strategies, motivation
**Time Commitment**: 2 hours/month
**Duration**: One phase (4 weeks) to full program (16 weeks)

**Value Proposition**:
- "I just went through this" freshness
- Relatable struggles and solutions
- Immediate tactical advice
- Easy to schedule and connect

### Tier 2: Experienced Mentorship (3-7 Years Ahead)
**Mentor Profile**: Senior engineer with production distributed systems experience
**Best For**: Career guidance, technical depth, design patterns
**Time Commitment**: 3 hours/month
**Duration**: One year

**Value Proposition**:
- Real production experience
- Career progression insights
- Technical deep dives
- Industry connections

### Tier 3: Expert Mentorship (10+ Years, Architect Level)
**Mentor Profile**: Staff/Principal engineer, System Architect, CTO
**Best For**: Strategic thinking, system philosophy, career trajectory
**Time Commitment**: 1-2 hours/quarter
**Duration**: Ongoing relationship

**Value Proposition**:
- Highest-level perspective
- Strategic career guidance
- Industry influence
- Rare insights

## MATCHING ALGORITHM

### Input Data: Mentor Application

```
ATLAS MENTOR APPLICATION

Personal Information:
- Name: ___________
- Email: ___________
- LinkedIn: ___________
- Current Role: ___________
- Company: ___________
- Years of Experience: ___________
- Time Zone: [UTC offset]

Mentorship Tier:
○ Tier 1: Peer Mentor (1-2 years ahead)
○ Tier 2: Experienced Mentor (3-7 years ahead)
○ Tier 3: Expert Mentor (10+ years, architect level)

Availability:
How many hours per month can you commit?
○ 2 hours (1 mentee)
○ 4 hours (2 mentees)
○ 6 hours (3 mentees)
○ 8+ hours (4+ mentees)

Preferred meeting cadence:
□ Weekly 30-minute sessions
□ Bi-weekly 1-hour sessions
□ Monthly 2-hour sessions
□ Quarterly deep dives

Areas of Expertise (Select all that apply):
□ Microservices architecture
□ Database systems and scaling
□ Event-driven architecture
□ Observability and monitoring
□ Cloud infrastructure (AWS/GCP/Azure)
□ Cost optimization
□ Incident response
□ Team leadership
□ System design interviews
□ Career transitions

Technical Stack Expertise:
Programming languages: ___________
Databases: ___________
Cloud platforms: ___________
Tools and frameworks: ___________

Industry Experience:
□ E-commerce
□ Fintech
□ Social media
□ Streaming/media
□ Gaming
□ Healthcare
□ Enterprise SaaS
□ Infrastructure/Platform

Company Scale Experience:
□ Startup (< 50 employees)
□ Scale-up (50-500 employees)
□ Large tech (500-5000 employees)
□ Enterprise (5000+ employees)
□ FAANG/Big Tech

Mentoring Style:
○ Directive (provide specific guidance)
○ Coaching (ask questions to guide discovery)
○ Collaborative (work through problems together)
○ Mixed approach (adapt to mentee needs)

Ideal Mentee:
What type of mentee are you best suited to help?
___________

Mentoring Experience:
Have you mentored before? ___________
What worked well in past mentoring? ___________
What challenges did you face? ___________

Motivation:
Why do you want to be an Atlas mentor? ___________

Atlas Completion:
Did you complete the Atlas study plan?
○ Yes, intensive track
○ Yes, balanced track
○ Yes, extended track
○ No, but equivalent experience
```

### Input Data: Mentee Application

```
ATLAS MENTEE APPLICATION

Personal Information:
- Name: ___________
- Email: ___________
- LinkedIn: ___________
- Current Role: ___________
- Years of Experience: ___________
- Time Zone: [UTC offset]

Desired Mentorship Tier:
○ Tier 1: Peer Mentor (recently completed Atlas)
○ Tier 2: Experienced Mentor (3-7 years experience)
○ Tier 3: Expert Mentor (10+ years, architect)
○ Any tier (flexible)

Current Study Plan:
○ Intensive (16 weeks)
○ Balanced (32 weeks)
○ Extended (52 weeks)
○ Completed, now applying

Where are you in your journey?
○ Weeks 1-4 (Foundation)
○ Weeks 5-8 (Performance)
○ Weeks 9-12 (Companies & Production)
○ Weeks 13-16 (Integration)
○ Post-completion

Primary Goals (Rank 1-3):
___ Land distributed systems role at FAANG
___ Transition from frontend/backend to systems
___ Become technical lead/architect
___ Deepen current distributed systems skills
___ Pass system design interviews
___ Build production systems confidently

Specific Challenges:
What are you struggling with most?
___________

Technical Background:
Current tech stack: ___________
Comfortable with: ___________
Want to learn: ___________

Target Industry:
Where do you want to work?
□ E-commerce
□ Fintech
□ Social media
□ Streaming/media
□ Gaming
□ Healthcare
□ Enterprise SaaS
□ Infrastructure/Platform

Preferred Company Scale:
□ Startup (< 50 employees)
□ Scale-up (50-500 employees)
□ Large tech (500-5000 employees)
□ Enterprise (5000+ employees)
□ FAANG/Big Tech

Learning Style:
○ I learn best through structured guidance
○ I prefer open-ended exploration with check-ins
○ I like working through problems collaboratively
○ I need accountability and deadlines

Communication Preference:
○ Text/email only
○ Voice calls ok
○ Video calls preferred
○ In-person if local (rare)

Availability:
What's your schedule flexibility?
□ Weekday mornings
□ Weekday afternoons
□ Weekday evenings
□ Weekend mornings
□ Weekend afternoons

Meeting Cadence Preference:
○ Weekly 30-minute check-ins
○ Bi-weekly 1-hour sessions
○ Monthly 2-hour deep dives
○ Flexible based on needs

What are you hoping to get from mentorship?
___________

Previous mentorship experience:
Have you had mentors before? What worked? ___________
```

### Matching Algorithm Implementation

```python
from typing import List, Dict, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class Mentor:
    id: str
    tier: int  # 1, 2, or 3
    hours_available: int
    areas_of_expertise: List[str]
    industries: List[str]
    company_scales: List[str]
    timezone: int
    style: str  # 'directive', 'coaching', 'collaborative', 'mixed'
    current_mentees: int
    max_mentees: int

@dataclass
class Mentee:
    id: str
    desired_tier: int  # 1, 2, 3, or 0 (any)
    goals: List[Tuple[str, int]]  # Goal and rank
    challenges: str
    target_industries: List[str]
    target_company_scales: List[str]
    timezone: int
    learning_style: str
    study_phase: str  # 'foundation', 'performance', etc.

def calculate_mentor_mentee_compatibility(
    mentor: Mentor,
    mentee: Mentee
) -> float:
    """
    Calculate compatibility score between mentor and mentee.
    Range: 0.0 (incompatible) to 1.0 (perfect match)
    """
    score = 0.0
    weights = {
        'tier': 0.20,          # Must be acceptable
        'expertise': 0.25,     # High importance
        'industry': 0.15,      # Moderate importance
        'timezone': 0.15,      # Moderate importance
        'style': 0.15,         # Moderate importance
        'availability': 0.10   # Lower importance
    }

    # Tier matching
    if mentee.desired_tier == 0 or mentee.desired_tier == mentor.tier:
        score += weights['tier']
    else:
        return 0.0  # Incompatible if tier doesn't match

    # Check mentor availability
    if mentor.current_mentees >= mentor.max_mentees:
        return 0.0  # Mentor at capacity

    # Expertise alignment with mentee goals
    mentee_goal_areas = [g[0] for g in sorted(mentee.goals, key=lambda x: x[1])[:3]]
    expertise_overlap = len(set(mentee_goal_areas) & set(mentor.areas_of_expertise))
    score += weights['expertise'] * (expertise_overlap / 3.0)

    # Industry experience alignment
    if mentor.industries and mentee.target_industries:
        industry_overlap = len(set(mentor.industries) & set(mentee.target_industries))
        score += weights['industry'] * min(industry_overlap / 2.0, 1.0)
    else:
        score += weights['industry'] * 0.5  # Neutral if not specified

    # Timezone compatibility
    tz_diff = abs(mentor.timezone - mentee.timezone)
    if tz_diff <= 3:
        score += weights['timezone']
    elif tz_diff <= 6:
        score += weights['timezone'] * 0.6
    elif tz_diff <= 9:
        score += weights['timezone'] * 0.3

    # Learning style and mentoring style match
    style_compatibility = {
        ('structured', 'directive'): 1.0,
        ('structured', 'mixed'): 0.8,
        ('exploration', 'coaching'): 1.0,
        ('exploration', 'mixed'): 0.8,
        ('collaborative', 'collaborative'): 1.0,
        ('collaborative', 'mixed'): 0.9,
        ('accountability', 'directive'): 1.0,
        ('accountability', 'mixed'): 0.8,
    }
    style_score = style_compatibility.get(
        (mentee.learning_style, mentor.style),
        0.6  # Default moderate compatibility
    )
    score += weights['style'] * style_score

    # Availability (basic check that mentor has time)
    score += weights['availability']  # Already filtered by capacity

    return min(score, 1.0)

def match_mentees_to_mentors(
    mentees: List[Mentee],
    mentors: List[Mentor],
    min_score: float = 0.6
) -> Dict[str, List[Tuple[str, float]]]:
    """
    Match mentees to compatible mentors.

    Returns: Dict mapping mentee_id to list of (mentor_id, score) tuples
    """
    matches = {}

    for mentee in mentees:
        # Calculate compatibility with all available mentors
        compatible_mentors = []

        for mentor in mentors:
            if mentor.current_mentees < mentor.max_mentees:
                score = calculate_mentor_mentee_compatibility(mentor, mentee)
                if score >= min_score:
                    compatible_mentors.append((mentor.id, score))

        # Sort by compatibility score (descending)
        compatible_mentors.sort(key=lambda x: x[1], reverse=True)

        # Return top 5 matches for mentee to choose from
        matches[mentee.id] = compatible_mentors[:5]

    return matches

def optimize_matches(
    initial_matches: Dict[str, List[Tuple[str, float]]],
    mentors: Dict[str, Mentor]
) -> Dict[str, str]:
    """
    Optimize match assignments to maximize overall compatibility
    while respecting mentor capacity constraints.

    Uses greedy algorithm with backtracking.
    """
    # Convert to list of (mentee, mentor, score) sorted by score
    all_pairs = []
    for mentee_id, mentor_list in initial_matches.items():
        for mentor_id, score in mentor_list:
            all_pairs.append((mentee_id, mentor_id, score))

    all_pairs.sort(key=lambda x: x[2], reverse=True)

    # Track assignments
    assignments = {}  # mentee_id -> mentor_id
    mentor_loads = {m_id: 0 for m_id in mentors.keys()}

    # Greedy assignment
    for mentee_id, mentor_id, score in all_pairs:
        # Skip if mentee already assigned
        if mentee_id in assignments:
            continue

        # Skip if mentor at capacity
        if mentor_loads[mentor_id] >= mentors[mentor_id].max_mentees:
            continue

        # Assign
        assignments[mentee_id] = mentor_id
        mentor_loads[mentor_id] += 1

    return assignments
```

### Manual Review Process

**After Algorithm Runs**:
1. **Review Top Matches** (Score >0.8)
   - Auto-suggest these matches
   - Provide context on why they match
   - Allow mentee to accept or see alternatives

2. **Review Medium Matches** (Score 0.6-0.8)
   - Present options with pros/cons
   - Suggest trial meeting before commitment
   - Provide backup options

3. **Handle Low/No Matches** (Score <0.6)
   - Expand search criteria
   - Consider cross-tier matching
   - Waitlist for future mentors
   - Offer group mentorship alternative

## MATCHING STRATEGIES

### For Beginners
**Priority**: Peer mentors (Tier 1) who recently completed Atlas
**Why**: Fresh memory of struggles, relatable advice, high availability
**Backup**: Experienced mentor with strong teaching track record

### For Career Transitioners
**Priority**: Mentors with similar transition experience
**Why**: Practical advice on navigating change, empathy for challenges
**Backup**: Industry-specific mentors for target domain

### For Advanced Learners
**Priority**: Expert mentors (Tier 3) or multiple specialized mentors
**Why**: Need depth in specific areas, strategic career guidance
**Backup**: Community of advanced peers for collaborative learning

### For Interview Prep
**Priority**: Mentors currently at target companies (FAANG, etc.)
**Why**: Current interview knowledge, company-specific insights
**Backup**: Professional interview coaches from community

## MATCHING TIMELINE

### Week -2: Open Applications
- Mentor and mentee applications open
- Marketing campaign to recruit mentors
- Promote across community channels

### Week -1: Initial Matching
- Algorithm runs on all applications
- Manual review of edge cases
- Mentor capacity balancing

### Week 0: Match Notification
- Both parties receive match suggestion
- Introduction email with context
- 48 hours to accept or request alternative

### Week 1: First Meeting
- Scheduled within 7 days of match
- Structured first meeting agenda provided
- Relationship expectations set

### Ongoing: Matching Maintenance
- New applications matched weekly
- Quarterly re-matching option
- Support for relationship issues

## FIRST MEETING STRUCTURE

### Pre-Meeting (Both Parties)
**Mentor Preparation**:
- Review mentee application
- Research their background (LinkedIn)
- Prepare 3-5 questions about goals
- Clear personal schedule for full attention

**Mentee Preparation**:
- Review mentor background
- List 3 current challenges
- Prepare 3-5 questions for mentor
- Bring specific examples/problems

### Meeting Agenda (60 minutes)

**Part 1: Getting to Know Each Other (20 min)**
- Personal backgrounds and journeys
- Current situation and context
- Communication styles and preferences
- Availability and scheduling

**Part 2: Goal Setting (20 min)**
- Mentee shares primary goals
- Mentor shares how they can help
- Identify specific areas of focus
- Set 3-month objectives

**Part 3: Logistics and Expectations (20 min)**
- Meeting cadence (weekly, bi-weekly, monthly)
- Communication methods (email, Slack, Discord)
- Homework and preparation expectations
- Success metrics and check-ins

**Output**: Written mentorship agreement

### Mentorship Agreement Template

```
ATLAS MENTORSHIP AGREEMENT

Mentor: [Name]
Mentee: [Name]
Start Date: [Date]
Review Date: [3 months from start]

GOALS:
1. [Primary goal]
2. [Secondary goal]
3. [Tertiary goal]

MEETING SCHEDULE:
Cadence: [Weekly/Bi-weekly/Monthly]
Duration: [30/60/90 minutes]
Day/Time: [Specific or flexible]
Platform: [Zoom/Discord/Google Meet]

COMMUNICATION:
Primary: [Email/Slack/Discord]
Response time: [24 hours/48 hours/1 week]
Emergency protocol: [For urgent questions]

EXPECTATIONS:
Mentor commits to:
- [Specific commitment 1]
- [Specific commitment 2]
- [Specific commitment 3]

Mentee commits to:
- Come prepared with specific questions
- Complete agreed-upon homework
- Share progress and challenges openly
- Respect mentor's time and boundaries

SUCCESS METRICS:
How will we know this is working?
- [Metric 1]
- [Metric 2]
- [Metric 3]

REVIEW AND ADJUSTMENT:
We will review this agreement in 3 months and:
- Assess progress toward goals
- Adjust focus areas if needed
- Decide whether to continue
- Celebrate successes

SIGNATURES:
Mentor: __________ Date: __________
Mentee: __________ Date: __________
```

## MENTORSHIP QUALITY ASSURANCE

### Monthly Check-Ins (Automated Survey)

**For Mentees**:
- Are meetings happening as scheduled? Y/N
- Is your mentor helpful? (1-5 scale)
- Are you making progress toward goals? Y/N
- Any concerns to address? [Open text]

**For Mentors**:
- Is mentee engaged and prepared? (1-5 scale)
- Are you able to help effectively? Y/N
- Any support needed from program? [Open text]

### Quarterly Relationship Review

**Structured Conversation**:
1. Review original goals - progress?
2. What's working well?
3. What could improve?
4. Adjust focus for next quarter
5. Continue or conclude relationship?

### Red Flags to Watch

**Mentee Red Flags**:
- Repeatedly misses meetings without notice
- Comes unprepared consistently
- Doesn't follow through on commitments
- Makes no progress over 2+ months

**Mentor Red Flags**:
- Frequently cancels or reschedules
- Provides generic advice without personalization
- Doesn't respond to messages
- Makes mentee uncomfortable

**Intervention Process**:
1. Program coordinator reaches out privately
2. Understand root cause
3. Offer support or resources
4. Facilitate difficult conversation if needed
5. Offer re-matching if relationship not working

## SUCCESS METRICS

### Relationship Health
- **Meeting Frequency**: Target 90% of scheduled meetings occur
- **Satisfaction Scores**: Both parties rate ≥4/5
- **Duration**: 70% of relationships last >6 months
- **Completion**: 80% of mentees complete program

### Impact Metrics
- **Goal Achievement**: 75% of mentees achieve primary goal
- **Career Impact**: Track job changes, promotions within 12 months
- **Skill Growth**: Assessment score improvement
- **Confidence**: Self-reported confidence increase

### Program Growth
- **Mentor Retention**: 80% of mentors continue after first year
- **Mentee Conversion**: 50% of mentees become mentors later
- **Scaling**: Maintain quality as program grows
- **Diversity**: Represent diverse backgrounds and experiences

---

**Mentorship Philosophy**: The best mentorship is a rising tide that lifts both boats. Mentors learn by teaching, mentees grow by learning, and both gain a lasting relationship.

**🚀 [APPLY TO BE A MENTOR →](https://forms.atlas-community.org/mentor-application)**
**🎓 [FIND A MENTOR →](https://forms.atlas-community.org/mentee-application)**
**📊 [VIEW MENTOR DIRECTORY →](https://atlas-community.org/mentors)**