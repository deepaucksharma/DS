# Cohort Formation Algorithm
## Optimal Study Group Matching for Distributed Learning

### Philosophy

Great study groups aren't random—they're carefully composed to maximize learning, maintain momentum, and build lasting relationships. The right group turns a solitary journey into a shared adventure.

**Core Insight**: Diversity in perspective, similarity in commitment.

### Cohort Formation Principles

**1. Commitment Alignment** (Most Important)
Match people with similar time availability and dedication levels to prevent frustration and dropouts.

**2. Skill Level Diversity** (Moderate Importance)
Mix experience levels to enable peer teaching while maintaining productive discussions.

**3. Time Zone Compatibility** (High Importance)
Ensure at least 4-hour daily overlap for synchronous collaboration.

**4. Goal Alignment** (High Importance)
Group people with similar objectives (career change, skill upgrade, interview prep).

**5. Learning Style Balance** (Moderate Importance)
Mix visual, auditory, and kinesthetic learners for rich discussions.

## MATCHING ALGORITHM

### Input Data Collection

**Cohort Application Form**:
```
ATLAS STUDY GROUP APPLICATION

Personal Information:
- Name: ___________
- Email: ___________
- LinkedIn: ___________
- Time Zone: [UTC offset]
- Location: [City, Country]

Study Plan Selection:
○ Intensive (16 weeks, 40-56 hours/week)
○ Balanced (32 weeks, 21-28 hours/week)
○ Extended (52 weeks, 14 hours/week)

Time Availability (Check all that apply):
□ Weekday mornings (6AM-12PM local)
□ Weekday afternoons (12PM-6PM local)
□ Weekday evenings (6PM-12AM local)
□ Weekend mornings
□ Weekend afternoons
□ Weekend evenings

Current Experience Level:
○ Beginner (< 2 years distributed systems)
○ Intermediate (2-5 years)
○ Advanced (5+ years)
○ Expert (10+ years, production architect)

Primary Goals (Rank 1-5):
___ Pass FAANG system design interviews
___ Transition to distributed systems role
___ Upgrade current skills
___ Become technical lead/architect
___ Understand production systems deeply

Learning Style Preferences (Select top 2):
□ Reading and taking notes
□ Watching videos and demos
□ Hands-on coding and experiments
□ Group discussion and teaching
□ Solo reflection and synthesis
□ Visual diagrams and models

Technical Background:
Current role: ___________
Years of experience: ___________
Primary programming languages: ___________
Familiar technologies: ___________

Communication Preferences:
○ Prefer async (text, forums)
○ Balanced (mix of sync and async)
○ Prefer sync (video calls, live chat)

Commitment Level:
How many weeks can you commit to consistent participation?
○ 4+ weeks (trial period)
○ 8+ weeks (one phase)
○ 16+ weeks (full intensive)
○ 32+ weeks (balanced track)
○ 52+ weeks (extended track)

Availability for Weekly Meetings:
Can you commit to 1 weekly 90-minute video call?
○ Yes, definitely
○ Yes, most weeks
○ Maybe, it depends
○ No, prefer async only

Additional Information:
What are you hoping to get from a study group? ___________
Any concerns or special requirements? ___________
Have you been in study groups before? What worked/didn't? ___________
```

### Matching Algorithm (Python Implementation)

```python
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass
from datetime import time, timedelta

@dataclass
class Participant:
    id: str
    name: str
    timezone_offset: int  # UTC offset in hours
    study_plan: str  # 'intensive', 'balanced', 'extended'
    experience_level: int  # 1=beginner, 2=intermediate, 3=advanced, 4=expert
    time_blocks: List[str]  # Available time blocks
    goals: List[Tuple[str, int]]  # Goal and priority (1-5)
    learning_styles: List[str]
    commitment_weeks: int
    sync_preference: int  # 1=async, 2=balanced, 3=sync

def calculate_compatibility_score(p1: Participant, p2: Participant) -> float:
    """
    Calculate compatibility score between two participants.
    Range: 0.0 (incompatible) to 1.0 (perfect match)
    """
    score = 0.0
    weights = {
        'study_plan': 0.25,      # Must match
        'timezone': 0.20,        # High importance
        'commitment': 0.20,      # High importance
        'goals': 0.15,           # Moderate importance
        'experience': 0.10,      # Some diversity ok
        'sync_pref': 0.10        # Moderate importance
    }

    # Study plan match (must be identical)
    if p1.study_plan == p2.study_plan:
        score += weights['study_plan']
    else:
        return 0.0  # Incompatible if different plans

    # Timezone compatibility
    tz_diff = abs(p1.timezone_offset - p2.timezone_offset)
    if tz_diff <= 3:
        score += weights['timezone']
    elif tz_diff <= 6:
        score += weights['timezone'] * 0.6
    elif tz_diff <= 9:
        score += weights['timezone'] * 0.3
    # >9 hours difference: no points

    # Commitment level alignment
    commitment_diff = abs(p1.commitment_weeks - p2.commitment_weeks)
    if commitment_diff <= 4:
        score += weights['commitment']
    elif commitment_diff <= 8:
        score += weights['commitment'] * 0.7
    elif commitment_diff <= 16:
        score += weights['commitment'] * 0.4

    # Goal overlap
    p1_goals = set([g[0] for g in p1.goals[:3]])  # Top 3 goals
    p2_goals = set([g[0] for g in p2.goals[:3]])
    goal_overlap = len(p1_goals & p2_goals) / 3.0
    score += weights['goals'] * goal_overlap

    # Experience diversity (want some spread but not too much)
    exp_diff = abs(p1.experience_level - p2.experience_level)
    if exp_diff == 0:
        score += weights['experience'] * 0.7  # Same level ok
    elif exp_diff == 1:
        score += weights['experience'] * 1.0  # One level apart ideal
    elif exp_diff == 2:
        score += weights['experience'] * 0.5  # Two levels ok
    # 3 levels: no points

    # Sync preference alignment
    sync_diff = abs(p1.sync_preference - p2.sync_preference)
    if sync_diff == 0:
        score += weights['sync_pref']
    elif sync_diff == 1:
        score += weights['sync_pref'] * 0.5

    return min(score, 1.0)

def find_time_overlap(participants: List[Participant]) -> int:
    """
    Find hours of overlapping availability per week.
    Returns: integer hours per week
    """
    if not participants:
        return 0

    # Convert time blocks to binary availability matrix
    common_blocks = set(participants[0].time_blocks)
    for p in participants[1:]:
        common_blocks &= set(p.time_blocks)

    # Each block represents ~3 hours
    return len(common_blocks) * 3

def form_cohort(
    participants: List[Participant],
    target_size: int = 25,
    min_size: int = 15,
    max_size: int = 30
) -> List[List[Participant]]:
    """
    Form optimal cohorts from participant pool.

    Algorithm:
    1. Group by study plan (must match)
    2. Within each plan, cluster by timezone
    3. Optimize for commitment alignment
    4. Balance experience levels
    5. Ensure minimum viable overlap
    """
    cohorts = []

    # Group by study plan first
    by_plan = {}
    for p in participants:
        if p.study_plan not in by_plan:
            by_plan[p.study_plan] = []
        by_plan[p.study_plan].append(p)

    # Form cohorts within each plan
    for plan, plan_participants in by_plan.items():
        # Sort by timezone for easier clustering
        plan_participants.sort(key=lambda x: x.timezone_offset)

        current_cohort = []

        for participant in plan_participants:
            if not current_cohort:
                current_cohort.append(participant)
                continue

            # Check compatibility with current cohort
            avg_compatibility = np.mean([
                calculate_compatibility_score(participant, member)
                for member in current_cohort
            ])

            # Check time overlap
            test_group = current_cohort + [participant]
            overlap_hours = find_time_overlap(test_group)

            # Decide whether to add to current cohort
            should_add = (
                len(current_cohort) < max_size and
                avg_compatibility >= 0.6 and  # Minimum compatibility
                overlap_hours >= 4  # Minimum 4 hours overlap
            )

            if should_add:
                current_cohort.append(participant)
            else:
                # Start new cohort if current is viable
                if len(current_cohort) >= min_size:
                    cohorts.append(current_cohort)
                    current_cohort = [participant]
                else:
                    # Try to force add if below min size
                    current_cohort.append(participant)

        # Add final cohort
        if len(current_cohort) >= min_size:
            cohorts.append(current_cohort)
        elif cohorts and len(cohorts[-1]) + len(current_cohort) <= max_size:
            # Merge with previous cohort if possible
            cohorts[-1].extend(current_cohort)

    return cohorts

def optimize_cohort_composition(cohort: List[Participant]) -> Dict:
    """
    Analyze cohort composition and provide optimization suggestions.
    """
    analysis = {
        'size': len(cohort),
        'experience_distribution': {},
        'timezone_spread': 0,
        'goal_diversity': {},
        'time_overlap_hours': find_time_overlap(cohort),
        'avg_commitment_weeks': 0,
        'sync_async_balance': {},
        'quality_score': 0.0
    }

    # Experience distribution
    for p in cohort:
        level = ['Beginner', 'Intermediate', 'Advanced', 'Expert'][p.experience_level - 1]
        analysis['experience_distribution'][level] = \
            analysis['experience_distribution'].get(level, 0) + 1

    # Timezone spread
    timezones = [p.timezone_offset for p in cohort]
    analysis['timezone_spread'] = max(timezones) - min(timezones)

    # Goal analysis
    all_goals = []
    for p in cohort:
        all_goals.extend([g[0] for g in p.goals])
    from collections import Counter
    analysis['goal_diversity'] = dict(Counter(all_goals).most_common(5))

    # Average commitment
    analysis['avg_commitment_weeks'] = np.mean([p.commitment_weeks for p in cohort])

    # Sync/async preference
    sync_prefs = [p.sync_preference for p in cohort]
    analysis['sync_async_balance'] = {
        'async_preferred': sync_prefs.count(1),
        'balanced': sync_prefs.count(2),
        'sync_preferred': sync_prefs.count(3)
    }

    # Quality score (0-100)
    quality_factors = []

    # Size appropriateness
    quality_factors.append(min(analysis['size'] / 25.0, 1.0) * 20)

    # Experience diversity (ideal: 40% intermediate, 30% advanced, 20% beginner, 10% expert)
    exp_dist = analysis['experience_distribution']
    total = sum(exp_dist.values())
    ideal = {'Beginner': 0.2, 'Intermediate': 0.4, 'Advanced': 0.3, 'Expert': 0.1}
    exp_quality = 20 - sum([
        abs((exp_dist.get(level, 0) / total) - ideal_pct) * 20
        for level, ideal_pct in ideal.items()
    ])
    quality_factors.append(max(exp_quality, 0))

    # Time overlap (ideal: 8+ hours)
    overlap_quality = min(analysis['time_overlap_hours'] / 8.0, 1.0) * 20
    quality_factors.append(overlap_quality)

    # Timezone compatibility (ideal: ≤6 hour spread)
    tz_quality = max(0, 20 - (analysis['timezone_spread'] * 2))
    quality_factors.append(tz_quality)

    # Sync/async balance (ideal: mostly balanced or sync-preferred)
    sync_balance = analysis['sync_async_balance']
    if sync_balance.get('balanced', 0) + sync_balance.get('sync_preferred', 0) >= len(cohort) * 0.7:
        quality_factors.append(20)
    else:
        quality_factors.append(10)

    analysis['quality_score'] = sum(quality_factors)

    return analysis
```

### Manual Review and Adjustment

**After Algorithm Run**:
1. Review flagged low-compatibility pairs
2. Check for outliers (single very advanced/beginner)
3. Validate time zone groupings make sense
4. Ensure goal diversity isn't too extreme
5. Look for potential personality conflicts (if data available)

**Adjustment Criteria**:
- Move participants between cohorts if it improves both groups
- Split oversized cohorts if quality score is low
- Merge undersized cohorts if compatible
- Create specialized cohorts for outliers (e.g., all-expert group)

## COHORT TYPES

### Standard Cohorts (Most Common)
- **Size**: 20-25 members
- **Experience**: Mixed (20% beginner, 40% intermediate, 30% advanced, 10% expert)
- **Time zones**: ≤6 hour spread
- **Goals**: Diverse but overlapping

### Beginner-Friendly Cohorts
- **Size**: 15-20 members
- **Experience**: 70% beginner, 30% intermediate (mentors)
- **Focus**: Fundamentals, confidence building
- **Extra support**: Assigned mentor from advanced pool

### Advanced Cohorts
- **Size**: 15-20 members
- **Experience**: 100% advanced/expert
- **Focus**: Deep dives, research papers, novel solutions
- **Special**: Direct access to industry experts

### Career-Transition Focused
- **Size**: 20-25 members
- **Goal**: All aiming for role transitions
- **Activities**: Mock interviews, resume reviews, networking
- **Timeline**: Aligned with job search timelines

### Regional Cohorts
- **Size**: 20-30 members
- **Time zones**: ≤3 hour spread (same general region)
- **Benefits**: Easier synchronous meetings, local meetups possible
- **Examples**: North America, Europe, Asia-Pacific, Latin America

## COHORT LIFECYCLE

### Week 0: Formation and Kickoff
**Activities**:
- Introductions in private Discord channel
- Schedule first meeting via When2Meet
- Set group norms and expectations
- Assign initial study partners (pairs)

**First Meeting Agenda** (90 minutes):
1. Icebreaker: Share your "why" (30 min)
2. Review study plan and timeline (15 min)
3. Establish communication norms (15 min)
4. Form accountability pairs (15 min)
5. Schedule recurring meetings (15 min)

### Weeks 1-4: Forming Stage
**Focus**: Building trust and routines
**Activities**:
- Weekly video meetings
- Daily async check-ins
- Pair study sessions
- First collaborative diagram

**Success Metrics**:
- 80%+ attendance at meetings
- 90%+ daily check-in completion
- All pairs met at least twice
- Group comfort level rising

### Weeks 5-12: Performing Stage
**Focus**: Deep learning and collaboration
**Activities**:
- Peer teaching presentations
- Group problem-solving sessions
- Collaborative contributions
- Mid-point retrospective

**Success Metrics**:
- High engagement in discussions
- Multiple community contributions
- Strong pair accountability
- Low dropout rate (<10%)

### Weeks 13-16: Consolidating Stage
**Focus**: Integration and next steps
**Activities**:
- Mock interviews within group
- Final project presentations
- Career planning sessions
- Transition planning

**Success Metrics**:
- Assessment scores ≥850/1000
- Career progress (offers, promotions)
- Plans to continue learning
- Commitment to mentor next cohort

### Post-Completion: Alumni Network
**Transition**:
- Join alumni Discord channel
- Option to mentor new cohorts
- Participate in advanced discussions
- Attend quarterly reunions

## SUCCESS FACTORS

### What Makes Great Cohorts

**1. Psychological Safety**
- No question is too basic
- Struggles are shared openly
- Mistakes are learning opportunities
- Diverse perspectives valued

**2. Consistent Participation**
- High attendance (>80%)
- Active async engagement
- Reliable accountability
- Follow-through on commitments

**3. Balanced Contribution**
- Everyone contributes roughly equally
- No single person dominates
- Quieter members encouraged
- Teaching rotates among members

**4. Clear Structure**
- Recurring meeting times
- Defined roles (facilitator rotates)
- Standard formats
- Progress tracking

**5. Supportive Culture**
- Celebrate small wins
- Support during struggles
- Constructive feedback
- Humor and humanity

### Warning Signs of Struggling Cohorts

**Red Flags**:
- Attendance dropping below 60%
- Async participation declining
- Conflicts unresolved
- Lack of contributions
- No one volunteers to facilitate

**Interventions**:
1. Anonymous feedback survey
2. Facilitator one-on-ones
3. Group retrospective
4. Adjust meeting format
5. If needed: Offer transfers to other cohorts

## COHORT ROLES

### Rotating Facilitator (Weekly)
**Responsibilities**:
- Prepare meeting agenda
- Facilitate discussion
- Keep time
- Document decisions
- Share notes afterward

**Rotation**: Every member takes turn

### Accountability Pairs (Fixed)
**Purpose**: Daily check-ins and support
**Activities**:
- Morning goal setting
- Evening progress review
- Problem-solving help
- Encouragement

**Pairing Strategy**: Mix experience levels

### Subject Matter Champions (Voluntary)
**Purpose**: Lead deep dives on specific topics
**Examples**:
- Consensus algorithms champion
- Database systems champion
- Observability champion
- Cost optimization champion

### Community Liaison (Elected)
**Purpose**: Connect cohort to broader community
**Responsibilities**:
- Share cohort achievements
- Coordinate with other cohorts
- Facilitate guest speakers
- Represent cohort in community decisions

**Term**: One phase (4 weeks)

## TOOLS AND PLATFORMS

### Essential Tools
- **Discord**: Primary communication (private channel)
- **GitHub**: Collaborative contributions (shared project board)
- **When2Meet**: Schedule coordination
- **Google Docs**: Shared notes and agendas
- **Miro/Mural**: Visual collaboration
- **Calendly**: Office hours booking

### Optional Tools
- **Zoom**: Video meetings (if Discord insufficient)
- **Notion**: Knowledge base
- **Slack**: If preferred over Discord
- **Obsidian**: Shared knowledge graph

## METRICS AND OPTIMIZATION

### Track Key Metrics
- **Attendance Rate**: Target >80%
- **Completion Rate**: Target >70% finish full program
- **Contribution Rate**: Target >50% make at least one contribution
- **Satisfaction**: Target NPS >50
- **Career Impact**: Track job changes, promotions

### Continuous Improvement
- Monthly cohort surveys
- Post-completion retrospectives
- Cross-cohort comparisons
- Algorithm refinement based on outcomes
- Best practice documentation

---

**Cohort Philosophy**: Alone we learn faster; together we learn deeper. The right study group transforms information into understanding, and understanding into wisdom.

**🚀 [APPLY TO JOIN A COHORT →](https://forms.atlas-community.org/cohort-application)**
**📊 [VIEW COHORT ANALYTICS →](https://atlas-community.org/cohorts/analytics)**