# Reddit Global Outage - March 14, 2023

**The 4-Hour Database Migration Failure That Silenced the Internet's Front Page**

## Incident Overview

| **Metric** | **Value** |
|------------|-----------||
| **Date** | March 14, 2023 |
| **Duration** | 4 hours |
| **Impact** | Complete platform unavailable |
| **Users Affected** | 1.7B+ monthly users |
| **Financial Impact** | $100M+ in lost engagement and ad revenue |
| **Root Cause** | Database migration failure |
| **MTTR** | 240 minutes |
| **Key Issue** | Data corruption during migration |
| **Services Down** | All subreddits, comments, voting, messaging |

```mermaid
graph TB
    subgraph "Reddit Platform"
        POSTS[Post Submission<br/>Content Creation]
        COMMENTS[Comment System<br/>Discussion Threads]
        VOTING[Voting System<br/>Upvote/Downvote]
        SUBREDDITS[Subreddits<br/>Community Management]
    end

    subgraph "Database Layer"
        MIGRATION[Database Migration<br/>Schema Update<br/>FAILED]
        POSTS_DB[(Posts Database<br/>Content Storage<br/>CORRUPTED)]
        USERS_DB[(Users Database<br/>Account Data)]
        VOTES_DB[(Votes Database<br/>Karma System)]
    end

    %% Migration failure cascade
    MIGRATION -.->|Schema migration failed<br/>14:00 PST| POSTS_DB
    POSTS_DB -.->|Data corruption<br/>Cannot read posts| POSTS
    POSTS -.->|Cannot load content<br/>Subreddits empty| COMMENTS
    COMMENTS -.->|Cannot display threads<br/>Discussion broken| VOTING

    %% Customer impact
    POSTS -.->|"Reddit is down"<br/>1.7B+ users affected| USERS[Internet Communities<br/>News Readers<br/>Meme Creators<br/>Technical Communities]

    classDef migrationStyle fill:#FF6B6B,stroke:#CC0000,color:#fff,stroke-width:3px
    classDef serviceStyle fill:#00AA00,stroke:#007700,color:#fff,stroke-width:3px
    classDef impactStyle fill:#8B0000,stroke:#660000,color:#fff,stroke-width:4px

    class MIGRATION,POSTS_DB,USERS_DB,VOTES_DB migrationStyle
    class POSTS,COMMENTS,VOTING,SUBREDDITS serviceStyle
    class USERS impactStyle
```

## The Bottom Line

**This incident showed that database migrations on platforms with billions of records require extensive testing and rollback procedures.**

**Key Takeaways:**
- Database migrations need staging environments with production-scale data
- Schema changes on billion-record tables require careful planning
- Community platforms have zero tolerance for extended downtime
- Migration rollback procedures must be tested and ready

---

*"In social platforms, database migrations don't just affect data - they affect conversations."*