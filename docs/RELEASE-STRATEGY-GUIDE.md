# Release Strategy & CI/CD Best Practices Guide

## Executive Summary

This document defines the branching strategy, CI/CD pipeline configuration, and release methodology for a hybrid cloud/on-premises observability product. It covers the transition from a 6-month release cycle to a monthly cadence with continuous cloud deployments.

---

## Table of Contents

1. [Current State vs Target State](#1-current-state-vs-target-state)
2. [Release Strategy Visual Reference](#2-release-strategy-visual-reference)
3. [Staging Environment & Code Promotion](#3-staging-environment--code-promotion)
4. [Developer Guidelines](#4-developer-guidelines)
5. [DevOps Guidelines](#5-devops-guidelines)
6. [Release Workflows](#6-release-workflows)
7. [Hotfix Procedures](#7-hotfix-procedures)
8. [Implementation Checklist](#8-implementation-checklist)

**Appendices**
- [Appendix A: CI/CD Pipeline Architecture](#appendix-a-cicd-pipeline-architecture)
- [Appendix B: Release Type Definitions](#appendix-b-release-type-definitions)

---

## 1. Current State vs Target State

This section provides an immediate visual comparison of where we are today versus where we want to be.

### 1.1 Transformation Overview

```mermaid
flowchart LR
    subgraph Current["CURRENT STATE"]
        direction TB
        CA[6-Month Releases] --> CB[Long QA Cycles]
        CB --> CC[Big Bang Updates]
        CC --> CD[High Risk Deployments]
        CD --> CE[Slow Feedback Loop]
    end

    subgraph Target["TARGET STATE"]
        direction TB
        TA[Monthly Releases] --> TB[Continuous Testing]
        TB --> TC[Incremental Updates]
        TC --> TD[Lower Risk]
        TD --> TE[Fast Feedback Loop]
    end

    Current --> |Transform| Target

    style Current fill:#ffcdd2,stroke:#c62828
    style Target fill:#c8e6c9,stroke:#2e7d32
```

### 1.2 Current State: 6-Month On-Prem Release Cycle

This diagram represents the existing release model with long cycles and infrequent on-premises releases.

```mermaid
flowchart TB
    subgraph DEV["Development Branch"]
        D1[Features] --> D2[Fixes] --> D3[Features] --> D4[Fixes]
    end

    subgraph CLOUD["Cloud Releases (Every 6 weeks)"]
        C1((1)) --> C2((2)) --> C3((3)) --> C4((4)) --> C5((5))
    end

    subgraph ONPREM["On-Prem Releases (Every 6 months)"]
        OP1((v1.0)) --> OP2((v2.0))
    end

    subgraph MAINT1["Maintenance v1.x"]
        M1((1.1)) --> M2((1.2))
    end

    subgraph MAINT2["Maintenance v2.x"]
        M3((2.1)) --> M4((2.2))
    end

    D1 --> C1
    D2 --> C2
    D3 --> C3
    D4 --> C4

    C1 --> OP1
    C3 --> OP2

    OP1 --> M1
    OP2 --> M3

    style DEV fill:#f5f5f5,stroke:#333
    style CLOUD fill:#c8e6c9,stroke:#2e7d32
    style ONPREM fill:#bbdefb,stroke:#1565c0
    style MAINT1 fill:#f8bbd9,stroke:#c2185b
    style MAINT2 fill:#f8bbd9,stroke:#c2185b
```

**Current State Characteristics:**

| Aspect | Current State | Impact |
|--------|--------------|--------|
| On-Prem Release Frequency | Every 6 months | Large, risky releases |
| Cloud Release Frequency | Every 6 weeks | Moderate agility |
| QA Cycle | 4-8 weeks | Slow feedback |
| Feature Delivery | Batched | Customer wait time |
| Hotfix Complexity | High | Multiple versions to patch |

---

### 1.3 Target State: Monthly On-Prem + Bi-Weekly Cloud

This diagram represents the target release model with faster, smaller, lower-risk releases.

```mermaid
flowchart TB
    subgraph DEV["main (Development)"]
        direction LR
        F1[Feature] --> F2[Fix] --> F3[Feature] --> F4[Fix] --> F5[Feature] --> F6[Fix]
    end

    subgraph STAGING["staging (Pre-Production)"]
        direction LR
        S1((●)) --> S2((●)) --> S3((●)) --> S4((●)) --> S5((●)) --> S6((●))
    end

    subgraph CLOUD["Cloud (Bi-Weekly)"]
        direction LR
        C1((1)) --> C2((2)) --> C3((3)) --> C4((4)) --> C5((5)) --> C6((6))
    end

    subgraph ONPREM["On-Prem (Monthly)"]
        direction LR
        OP1((Jan)) --> OP2((Feb)) --> OP3((Mar))
    end

    subgraph HOTFIX["Hotfixes"]
        H1((Jan.1))
        H2((Feb.1))
        H3((Mar.1))
    end

    DEV --> STAGING
    STAGING --> CLOUD
    STAGING --> ONPREM

    OP1 --> H1
    OP2 --> H2
    OP3 --> H3

    style DEV fill:#fff3e0,stroke:#e65100
    style STAGING fill:#e1f5fe,stroke:#0277bd
    style CLOUD fill:#c8e6c9,stroke:#2e7d32
    style ONPREM fill:#bbdefb,stroke:#1565c0
    style HOTFIX fill:#f8bbd9,stroke:#c2185b
```

**Target State Characteristics:**

| Aspect | Target State | Benefit |
|--------|-------------|---------|
| On-Prem Release Frequency | Monthly | Smaller, manageable releases |
| Cloud Release Frequency | Bi-weekly | High agility |
| QA Cycle | 1 week | Fast feedback |
| Feature Delivery | Continuous | Faster time to value |
| Hotfix Complexity | Low | Fewer versions to maintain |

---

### 1.4 Key Metrics Comparison

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| On-Prem releases per year | 2 | 12 | 6x more frequent |
| Cloud releases per year | 8-9 | 24-26 | 3x more frequent |
| Average feature wait time | 3-4 months | 2-4 weeks | 75% reduction |
| QA cycle duration | 4-8 weeks | 1 week | 80% reduction |
| Deployment risk | High | Low | Significantly lower |
| Rollback complexity | Complex | Simple | Faster recovery |

---

## 2. Release Strategy Visual Reference

This section provides comprehensive visual diagrams for all aspects of the release strategy.

### 2.1 Branch Strategy Flow (Git Graph)

```mermaid
gitGraph
    commit id: "Initial" tag: "v1.0"
    branch staging
    commit id: "Staging-Init"
    checkout main
    commit id: "FEAT-101"
    commit id: "FEAT-102"
    checkout staging
    merge main id: "Sync-1" type: HIGHLIGHT
    branch production-cloud
    commit id: "Cloud-Deploy-1" type: HIGHLIGHT
    checkout main
    commit id: "FEAT-103"
    commit id: "BUG-201"
    checkout staging
    merge main id: "Sync-2" type: HIGHLIGHT
    checkout production-cloud
    merge staging id: "Cloud-Deploy-2" type: HIGHLIGHT
    checkout main
    branch release-4-21-x
    commit id: "RC1" tag: "4.21-rc1"
    commit id: "Final" tag: "4.21" type: HIGHLIGHT
    checkout main
    commit id: "FEAT-104"
    checkout release-4-21-x
    branch hotfix-4-21-1
    commit id: "Hotfix" tag: "4.21.1"
```

> **Note**: Branch names use hyphens instead of dots/slashes for Mermaid compatibility. In actual GitLab, use `release/4.21.x` format.

#### Branch Definitions

| Branch | Purpose | Protected | Auto-Delete | Merge Source |
|--------|---------|-----------|-------------|--------------|
| `develop` | Integration, single source of truth | Yes | No | Feature branches |
| `staging` | Pre-production validation | Yes | No | Auto from develop |
| `production-cloud` | Cloud deployment state | Yes | No | staging |
| `release/X.Y.x` | On-prem release preparation (e.g., `release/4.21.x`) | Yes | After 6 months | develop (branch cut) |
| `feature/*` | New features | No | Yes | - |
| `bugfix/*` | Bug fixes | No | Yes | - |
| `hotfix/*` | Critical production fixes (e.g., `hotfix/4.21.1`) | No | Yes | release/X.Y.x |

#### Branch Flow Diagram

```mermaid
flowchart LR
    subgraph Development
        F1[feature/FEAT-123]
        F2[bugfix/BUG-456]
        F3[feature/FEAT-789]
    end

    subgraph Integration
        M[develop]
    end

    subgraph Validation
        S[staging]
    end

    subgraph Production
        PC[production-cloud]
        R1[release/4.21.x]
        R2[release/4.22.x]
    end

    subgraph Customers
        CL[Cloud Users]
        OP[On-Prem Users]
    end

    F1 --> M
    F2 --> M
    F3 --> M
    M --> |auto-merge| S
    S --> |bi-weekly| PC
    M --> |monthly cut| R1
    M --> |monthly cut| R2
    PC --> CL
    R1 --> OP
    R2 --> OP

    style Development fill:#fff3e0
    style Integration fill:#e3f2fd
    style Validation fill:#f3e5f5
    style Production fill:#e8f5e9
    style Customers fill:#fce4ec
```

---

### 2.2 Release Timeline (6-Month Gantt Chart)

```mermaid
gantt
    title Release Timeline - Target State (6 Months)
    dateFormat YYYY-MM-DD
    
    section Cloud Releases
    Cloud v1           :c1, 2026-01-08, 14d
    Cloud v2           :c2, 2026-01-22, 14d
    Cloud v3           :c3, 2026-02-05, 14d
    Cloud v4           :c4, 2026-02-19, 14d
    Cloud v5           :c5, 2026-03-04, 14d
    Cloud v6           :c6, 2026-03-18, 14d
    Cloud v7           :c7, 2026-04-01, 14d
    Cloud v8           :c8, 2026-04-15, 14d
    Cloud v9           :c9, 2026-04-29, 14d
    Cloud v10          :c10, 2026-05-13, 14d
    Cloud v11          :c11, 2026-05-27, 14d
    Cloud v12          :c12, 2026-06-10, 14d
    
    section On-Prem Releases
    4.21 Release   :op1, 2026-01-15, 30d
    4.22 Release   :op2, 2026-02-15, 28d
    4.23 Release   :op3, 2026-03-15, 31d
    4.24 Release   :op4, 2026-04-15, 30d
    4.25 Release   :op5, 2026-05-15, 31d
    4.26 Release   :op6, 2026-06-15, 30d
    
    section Maintenance
    4.21.1 Hotfix  :crit, m1, 2026-01-28, 3d
    4.22.1 Hotfix  :crit, m2, 2026-03-01, 3d
    4.24.1 Hotfix  :crit, m3, 2026-04-28, 3d
```

---

### 2.3 End-to-End CI/CD Pipeline Flow

```mermaid
flowchart LR
    subgraph Developer
        A[Code Change] --> B[Create MR]
    end

    subgraph CI["CI Pipeline"]
        C[Build] --> D[Unit Tests]
        D --> E[SAST Scan]
        E --> F[Integration Tests]
    end

    subgraph Review
        G[Code Review] --> H{Approved?}
    end

    subgraph CD["CD Pipeline"]
        I[Merge to main] --> J[Auto-merge to staging]
        J --> K[Deploy Staging]
        K --> L[Smoke Tests]
        L --> M{Pass?}
        M -->|Yes| N[Deploy Cloud]
        M -->|No| O[Notify Team]
    end

    subgraph OnPrem["On-Prem Release"]
        P[Cut Release Branch] --> Q[QA Testing]
        Q --> R[Package Build]
        R --> S[Distribute]
    end

    B --> C
    F --> G
    H -->|Yes| I
    H -->|No| A
    N --> P

    style Developer fill:#fff3e0
    style CI fill:#e3f2fd
    style Review fill:#f3e5f5
    style CD fill:#e8f5e9
    style OnPrem fill:#fce4ec
```

---

### 2.4 Feature Flow Through All Environments

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Main as main
    participant Stage as staging
    participant Cloud as production-cloud
    participant Release as release/X.Y.x
    participant OnPrem as On-Prem Customer

    Dev->>Main: Merge feature [FEAT-123]
    Note over Main: CI runs tests
    Main->>Stage: Auto-merge (daily)
    Note over Stage: Smoke tests
    Stage->>Cloud: Deploy (bi-weekly)
    Note over Cloud: Feature live for cloud users
    
    rect rgb(200, 230, 255)
        Note over Main,Release: Monthly Release Cut
        Main->>Release: Create release/4.22.x
        Note over Release: QA Testing (1 week)
        Release->>Release: Fix issues
        Release->>OnPrem: Package & Distribute
        Note over OnPrem: Customer upgrades
    end

    Note over Release: Hotfix needed?
    Release->>Release: Cherry-pick fix
    Release->>OnPrem: Hotfix 4.22.1
```

---

### 2.5 Hotfix Decision Flow

```mermaid
flowchart TD
    A[Critical Bug Found] --> B{Where?}
    
    B -->|Cloud Only| C[Fix in main]
    C --> D[Deploy to Cloud]
    
    B -->|On-Prem| E[Fix in main]
    E --> F[Cherry-pick to release/X.Y.x]
    F --> G[QA Validation]
    G --> H[Tag X.Y.Z]
    H --> I[Package Hotfix]
    I --> J[Notify Customers]
    
    B -->|Both| K[Fix in main]
    K --> L[Deploy to Cloud]
    K --> M[Cherry-pick to release/X.Y.x]
    M --> N[Tag & Package]
    N --> O[Distribute to On-Prem]

    style A fill:#ffcdd2
    style D fill:#c8e6c9
    style J fill:#bbdefb
    style L fill:#c8e6c9
    style O fill:#bbdefb
```

---

### 2.6 Version Support Matrix (N-3 Policy)

```mermaid
timeline
    title On-Prem Version Support (N-3 Policy)
    
    section Q1 2026
        Jan : 4.21 Released
            : 4.18 Supported
            : 4.19 Supported
            : 4.20 Supported
        Feb : 4.22 Released
            : 4.19 Supported
            : 4.20 Supported
            : 4.21 Supported
        Mar : 4.23 Released
            : 4.20 Supported
            : 4.21 Supported
            : 4.22 Supported
    
    section Q2 2026
        Apr : 4.24 Released
            : 4.21 Supported
            : 4.22 Supported
            : 4.23 Supported
        May : 4.25 Released
            : 4.22 Supported
            : 4.23 Supported
            : 4.24 Supported
        Jun : 4.26 Released
            : 4.23 Supported
            : 4.24 Supported
            : 4.25 Supported
```

---

### 2.7 Diagram Rendering Guide

These diagrams can be rendered in:

| Platform | Support |
|----------|---------|
| **GitLab** | Automatically renders in README, issues, MRs, and wikis |
| **GitHub** | Automatically renders in markdown files |
| **VS Code** | Use "Markdown Preview Mermaid Support" extension |
| **Online** | https://mermaid.live/ |
| **Confluence** | Use Mermaid plugin or embed as images |

---

## 3. Staging Environment & Code Promotion

The **staging environment** is the critical gateway between development and production. It serves as the validation layer where all features are tested in a production-like environment before being released to customers.

### 3.1 Staging Environment Overview

```mermaid
flowchart TB
    subgraph Purpose["STAGING PURPOSE"]
        P1[🧪 Pre-Production Testing]
        P2[🔍 Integration Validation]
        P3[🚀 Deployment Rehearsal]
        P4[✅ QA Sign-off Gate]
    end

    subgraph Characteristics["STAGING CHARACTERISTICS"]
        C1[Production-like Infrastructure]
        C2[Real Data Subsets]
        C3[Full Service Stack]
        C4[External Integrations Mocked/Sandboxed]
    end

    subgraph Users["STAGING USERS"]
        U1[QA Team]
        U2[Product Managers]
        U3[DevOps Engineers]
        U4[Select Beta Customers]
    end

    Purpose --> Characteristics --> Users

    style Purpose fill:#e3f2fd,stroke:#1565c0
    style Characteristics fill:#fff3e0,stroke:#e65100
    style Users fill:#e8f5e9,stroke:#2e7d32
```

### 3.2 Code Flow: Develop → Staging

```mermaid
flowchart LR
    subgraph Development["DEVELOPMENT"]
        F1[feature/FEAT-101]
        F2[feature/FEAT-102]
        F3[bugfix/BUG-201]
    end

    subgraph Integration["INTEGRATION"]
        M[develop branch]
    end

    subgraph Validation["VALIDATION"]
        S[staging branch]
    end

    subgraph Production["PRODUCTION"]
        PC[production-cloud]
        OP[On-Prem Release]
    end

    F1 --> |MR + Approval| M
    F2 --> |MR + Approval| M
    F3 --> |MR + Approval| M
    
    M --> |Auto-Merge| S
    S --> |Manual Gate| PC
    M --> |Branch Cut| OP

    style Development fill:#fff3e0
    style Integration fill:#e3f2fd
    style Validation fill:#f3e5f5
    style Production fill:#c8e6c9
```

### 3.3 Staging Promotion Scenarios

#### Scenario 1: Selective Feature Promotion (Feature Flags)

When you need to merge code to staging but hide incomplete features from users. This is the recommended approach for complex features.

```mermaid
flowchart TB
    subgraph Main["develop branch"]
        M1[FEAT-101 ✅ Complete]
        M2[FEAT-102 🔄 In Progress]
        M3[FEAT-103 ✅ Complete]
    end

    subgraph Staging["staging environment"]
        S1[FEAT-101 👁️ Visible]
        S2[FEAT-102 🔒 Hidden by Flag]
        S3[FEAT-103 👁️ Visible]
    end

    subgraph Flags["Feature Flags Service"]
        FF[LaunchDarkly / Unleash / GitLab]
    end

    M1 --> |deployed| S1
    M2 --> |deployed but flagged| S2
    M3 --> |deployed| S3
    
    FF --> |controls visibility| S2

    style M2 fill:#fff3e0,stroke:#e65100
    style S2 fill:#ffcdd2,stroke:#c62828
    style Flags fill:#e3f2fd,stroke:#1565c0
```

**Implementation:**

```python
# Feature flag check in application code
from feature_flags import FeatureFlagClient

ff_client = FeatureFlagClient()

def render_dashboard():
    # Feature is deployed but visibility controlled by flag
    if ff_client.is_enabled("FEAT-102-new-analytics", context={
        "environment": os.getenv("ENVIRONMENT"),  # staging, production
        "user_id": current_user.id,
        "user_tier": current_user.tier
    }):
        return render_new_analytics_dashboard()
    else:
        return render_legacy_dashboard()
```

**Feature Flag Configuration:**

```yaml
# feature-flags.yml
FEAT-102-new-analytics:
  description: "New analytics dashboard"
  default: false
  environments:
    development:
      enabled: true
    staging:
      enabled: true
      # Only visible to specific users for testing
      rules:
        - attribute: user_email
          operator: ends_with
          value: "@company.com"
          enabled: true
    production-cloud:
      enabled: false  # Not ready for production
    on-prem:
      enabled: false
```

**Developer Steps for Selective Feature Promotion:**

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant FF as Feature Flags
    participant Git as GitLab
    participant Stage as Staging

    Dev->>FF: 1. Create feature flag for FEAT-102
    Dev->>Dev: 2. Wrap new code with feature flag check
    Dev->>Git: 3. Create MR with flagged code
    Git->>Git: 4. Code review & merge to develop
    Git->>Stage: 5. Auto-deploy to staging (code deployed, flag OFF)
    Dev->>FF: 6. Enable flag for internal testers only
    Stage->>Dev: 7. Test feature in staging
    Dev->>FF: 8. Gradually enable for beta users
    Dev->>FF: 9. Full rollout when ready
```

| Step | Developer Action | Details |
|------|-----------------|---------|
| **1** | Create feature flag | Go to feature flag service (LaunchDarkly/GitLab/Unleash) and create a new flag named after your ticket (e.g., `FEAT-102-new-analytics`) |
| **2** | Wrap code with flag | Add feature flag checks around all new/modified code. Keep the old code path as fallback |
| **3** | Create MR | Submit your MR as normal. The CI pipeline runs tests with the flag both ON and OFF |
| **4** | Get review & merge | Reviewers verify flag implementation. Code merges to develop |
| **5** | Auto-deploy | Code deploys to staging automatically. Feature is hidden (flag is OFF by default) |
| **6** | Enable for testing | Enable the flag for `@company.com` emails only to test in staging |
| **7** | Validate | QA team tests the feature in staging environment |
| **8** | Gradual rollout | Enable for beta users (e.g., 10% of users) in cloud production |
| **9** | Full release | Enable flag for all users, then remove flag code in future cleanup |

**Developer Checklist for Feature Flags:**

```markdown
## Before Creating MR

- [ ] Feature flag created in flag service
- [ ] Flag name follows convention: `FEAT-{ticket}-{short-description}`
- [ ] All new code wrapped with feature flag check
- [ ] Fallback to existing behavior when flag is OFF
- [ ] Tests pass with flag ON and OFF
- [ ] Flag default is OFF in all environments

## After Merge

- [ ] Feature deployed to staging (verify in deployment logs)
- [ ] Flag enabled for internal testers
- [ ] Feature tested and validated
- [ ] Flag enabled for beta users (if applicable)
- [ ] Monitor metrics for issues
- [ ] Schedule flag cleanup after full rollout
```

---

#### Scenario 2: Standard Feature Flow (Automatic)

This is the default path for most features - automatic promotion from main to staging.

```mermaid
sequenceDiagram
    participant D as Developer
    participant MR as Merge Request
    participant M as main
    participant CI as CI Pipeline
    participant S as staging
    participant QA as QA Team

    D->>MR: Create MR for feature/FEAT-123
    MR->>MR: Code Review (2 approvals)
    MR->>CI: Run CI Pipeline
    CI->>CI: ✅ Tests Pass
    CI->>CI: ✅ Security Scans Pass
    MR->>M: Merge to main
    
    Note over M,S: AUTOMATIC PROMOTION
    M->>CI: Trigger merge-to-staging job
    CI->>CI: Check for conflicts
    CI->>S: Auto-merge main → staging
    S->>CI: Deploy to staging environment
    CI->>QA: Notify: New features in staging
    
    QA->>S: Validate features
    QA->>QA: ✅ Sign-off
```

**GitLab CI Configuration:**

```yaml
# Automatic merge from main to staging
auto-merge-to-staging:
  stage: merge-staging
  image: alpine/git
  variables:
    GIT_STRATEGY: clone
  before_script:
    - git config --global user.email "ci-bot@company.com"
    - git config --global user.name "CI Bot"
    - git remote set-url origin https://oauth2:${GITLAB_TOKEN}@gitlab.com/${CI_PROJECT_PATH}.git
  script:
    - |
      # Fetch latest staging
      git fetch origin staging:staging
      git checkout staging
      
      # Get list of new features being merged
      echo "📋 Features being promoted to staging:"
      git log staging..origin/main --pretty=format:"  • %s" | head -20
      
      # Attempt merge
      if git merge origin/main --no-edit -m "Auto-merge main → staging [skip ci]"; then
        echo "✅ Merge successful"
        git push origin staging
        
        # Track features
        FEATURES=$(git log staging@{1}..staging --pretty=format:"%s" | 
          grep -oE '\[(FEAT|BUG|TASK)-[0-9]+\]' | sort -u | tr '\n' ' ')
        
        # Notify team
        curl -X POST "$SLACK_WEBHOOK" \
          -H "Content-Type: application/json" \
          -d "{
            \"text\": \"✅ *Staging Updated*\n\nFeatures promoted:\n${FEATURES}\n\n<$CI_PIPELINE_URL|View Pipeline>\"
          }"
      else
        echo "❌ Merge conflict detected"
        git merge --abort
        exit 1
      fi
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success
  allow_failure: false
```

---

#### Scenario 3: Conflict Resolution (Manual Intervention)

When automatic merge fails due to conflicts.

```mermaid
sequenceDiagram
    participant M as main
    participant CI as CI Pipeline
    participant S as staging
    participant Dev as DevOps
    participant Slack as Notifications

    M->>CI: Trigger auto-merge
    CI->>CI: Attempt merge
    CI->>CI: ❌ Conflict detected
    CI->>Slack: 🚨 Alert: Merge conflict
    Slack->>Dev: Notify on-call
    
    Dev->>Dev: Investigate conflict
    
    alt Simple Conflict
        Dev->>S: Manual merge with resolution
        Dev->>M: Document resolution
    else Complex Conflict
        Dev->>Dev: Create conflict-resolution MR
        Dev->>M: Review resolution approach
        Dev->>S: Apply resolution
    end
    
    Dev->>CI: Re-trigger staging deploy
    CI->>S: Deploy updated staging
    Dev->>Slack: ✅ Conflict resolved
```

**Conflict Resolution Procedure:**

```bash
#!/bin/bash
# scripts/resolve-staging-conflict.sh

echo "🔧 Staging Conflict Resolution Script"

# 1. Fetch latest changes
git fetch origin main staging

# 2. Checkout staging and attempt merge
git checkout staging
git merge origin/main

# 3. If conflicts exist, list them
if [ $? -ne 0 ]; then
    echo "❌ Conflicts found in:"
    git diff --name-only --diff-filter=U
    echo ""
    echo "Please resolve conflicts manually, then run:"
    echo "  git add ."
    echo "  git commit -m 'Resolve staging merge conflict'"
    echo "  git push origin staging"
    exit 1
fi

# 4. Success
echo "✅ Merge successful"
git push origin staging
```

---

#### Scenario 4: Emergency Rollback

When staging needs to be reverted to a previous state.

```mermaid
flowchart TB
    A[🚨 Issue Detected in Staging] --> B{Severity?}
    
    B -->|Critical| C[Immediate Rollback]
    B -->|High| D[Targeted Revert]
    B -->|Low| E[Fix Forward]
    
    C --> F[Revert staging to last known good]
    F --> G[Block auto-merge temporarily]
    G --> H[Investigate root cause]
    H --> I[Fix in main]
    I --> J[Re-enable auto-merge]
    
    D --> K[Identify problematic commits]
    K --> L[Revert specific commits]
    L --> M[Keep other changes]
    
    E --> N[Create bugfix branch]
    N --> O[Fix and merge to main]
    O --> P[Auto-promote to staging]

    style C fill:#ffcdd2
    style F fill:#ffcdd2
    style G fill:#fff3e0
```

**Rollback Commands:**

```bash
#!/bin/bash
# scripts/rollback-staging.sh

ROLLBACK_TO=$1  # Commit SHA or tag to rollback to

if [ -z "$ROLLBACK_TO" ]; then
    echo "Usage: ./rollback-staging.sh <commit-sha-or-tag>"
    echo ""
    echo "Recent staging commits:"
    git log origin/staging --oneline -10
    exit 1
fi

echo "⚠️  Rolling back staging to: $ROLLBACK_TO"

# Create backup tag
BACKUP_TAG="staging-backup-$(date +%Y%m%d-%H%M%S)"
git tag $BACKUP_TAG origin/staging
git push origin $BACKUP_TAG

echo "📦 Backup created: $BACKUP_TAG"

# Force update staging to the specified commit
git checkout staging
git reset --hard $ROLLBACK_TO
git push origin staging --force-with-lease

echo "✅ Staging rolled back to $ROLLBACK_TO"
echo ""
echo "To restore: git push origin $BACKUP_TAG:staging --force-with-lease"
```

---

#### Scenario 5: Feature Branch Testing in Staging (Preview Environments)

For testing specific features before merging to main.

```mermaid
flowchart TB
    subgraph Feature["Feature Branches"]
        F1[feature/FEAT-101]
        F2[feature/FEAT-102]
        F3[feature/FEAT-103]
    end

    subgraph Preview["Preview Environments"]
        P1[preview-feat-101.staging.company.com]
        P2[preview-feat-102.staging.company.com]
        P3[preview-feat-103.staging.company.com]
    end

    subgraph Main["Main Staging"]
        S[staging.company.com]
    end

    F1 --> |deploy preview| P1
    F2 --> |deploy preview| P2
    F3 --> |deploy preview| P3
    
    P1 --> |after approval| S
    P2 --> |after approval| S
    P3 --> |after approval| S

    style Feature fill:#fff3e0
    style Preview fill:#e3f2fd
    style Main fill:#c8e6c9
```

**GitLab CI for Preview Environments:**

```yaml
deploy-preview:
  stage: deploy
  environment:
    name: preview/$CI_COMMIT_REF_SLUG
    url: https://preview-$CI_COMMIT_REF_SLUG.staging.company.com
    on_stop: stop-preview
    auto_stop_in: 1 week
  script:
    - |
      # Deploy feature branch to isolated preview environment
      kubectl create namespace preview-$CI_COMMIT_REF_SLUG || true
      helm upgrade --install preview-$CI_COMMIT_REF_SLUG ./charts/app \
        --namespace preview-$CI_COMMIT_REF_SLUG \
        --set image.tag=$CI_COMMIT_SHA \
        --set ingress.host=preview-$CI_COMMIT_REF_SLUG.staging.company.com
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^feature\//'
      when: manual

stop-preview:
  stage: deploy
  environment:
    name: preview/$CI_COMMIT_REF_SLUG
    action: stop
  script:
    - kubectl delete namespace preview-$CI_COMMIT_REF_SLUG
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^feature\//'
      when: manual
```

---

#### Scenario 6: Scheduled Batch Promotion

For teams preferring scheduled promotions rather than continuous.

```mermaid
gantt
    title Weekly Staging Promotion Schedule
    dateFormat HH:mm
    axisFormat %H:%M
    
    section Monday
    Collect features from main    :m1, 09:00, 1h
    QA Smoke Tests               :m2, 10:00, 2h
    
    section Tuesday
    Auto-merge to staging        :t1, 02:00, 30m
    Deploy staging               :t2, 02:30, 30m
    QA Full Regression           :t3, 09:00, 8h
    
    section Wednesday
    Bug fixes if needed          :w1, 09:00, 8h
    
    section Thursday
    Final validation             :th1, 09:00, 4h
    Sign-off for cloud deploy    :th2, 14:00, 1h
    
    section Friday
    Cloud deployment             :f1, 10:00, 2h
    Monitoring                   :f2, 12:00, 4h
```

**Scheduled Pipeline Configuration:**

```yaml
# GitLab CI Scheduled Pipeline
scheduled-staging-sync:
  stage: merge-staging
  script:
    - |
      echo "📅 Scheduled staging sync: $(date)"
      
      # Get all commits since last sync
      LAST_SYNC=$(git log origin/staging -1 --format="%H")
      NEW_COMMITS=$(git rev-list $LAST_SYNC..origin/main --count)
      
      if [ "$NEW_COMMITS" -eq 0 ]; then
        echo "ℹ️ No new commits to sync"
        exit 0
      fi
      
      echo "📦 $NEW_COMMITS new commits to sync"
      
      # List features
      echo "Features to promote:"
      git log $LAST_SYNC..origin/main --pretty=format:"  • %s" | head -50
      
      # Perform merge
      git checkout staging
      git merge origin/main --no-edit
      git push origin staging
      
      # Create sync report
      echo "## Staging Sync Report - $(date)" >> sync-report.md
      echo "Commits synced: $NEW_COMMITS" >> sync-report.md
      git log $LAST_SYNC..HEAD --pretty=format:"- %s (%h)" >> sync-report.md
  artifacts:
    paths:
      - sync-report.md
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
```

---

### 3.4 Staging Validation Gates

```mermaid
flowchart LR
    subgraph Gates["STAGING VALIDATION GATES"]
        G1[🧪 Automated Tests]
        G2[🔒 Security Scans]
        G3[📊 Performance Tests]
        G4[👁️ Visual Regression]
        G5[✅ QA Sign-off]
    end

    subgraph Automated["Automated Gates"]
        A1[Unit Tests > 80%]
        A2[Integration Tests Pass]
        A3[SAST/DAST Clean]
        A4[No Critical CVEs]
        A5[Response Time < 200ms]
    end

    subgraph Manual["Manual Gates"]
        M1[QA Exploratory Testing]
        M2[PM Feature Review]
        M3[UX Validation]
    end

    G1 --> A1
    G1 --> A2
    G2 --> A3
    G2 --> A4
    G3 --> A5
    G5 --> M1
    G5 --> M2
    G5 --> M3

    style Gates fill:#e3f2fd
    style Automated fill:#c8e6c9
    style Manual fill:#fff3e0
```

**Validation Pipeline:**

```yaml
staging-validation:
  stage: validate-staging
  needs:
    - deploy-staging
  script:
    - |
      echo "🧪 Running staging validation gates..."
      
      # Gate 1: Health check
      echo "Gate 1: Health Check"
      curl -f https://staging.company.com/health || exit 1
      
      # Gate 2: Smoke tests
      echo "Gate 2: Smoke Tests"
      pytest tests/smoke --base-url=https://staging.company.com
      
      # Gate 3: Performance baseline
      echo "Gate 3: Performance Check"
      ab -n 100 -c 10 https://staging.company.com/api/health | 
        grep "Time per request" | 
        awk '{if ($4 > 200) exit 1}'
      
      # Gate 4: Security headers
      echo "Gate 4: Security Headers"
      curl -sI https://staging.company.com | grep -q "X-Content-Type-Options"
      
      echo "✅ All automated gates passed"
  rules:
    - if: '$CI_COMMIT_BRANCH == "staging"'
```

---

### 3.5 Staging Environment Monitoring

```mermaid
flowchart TB
    subgraph Monitoring["STAGING MONITORING"]
        direction TB
        M1[📈 Metrics Dashboard]
        M2[📋 Log Aggregation]
        M3[🚨 Alerting]
        M4[🔍 Tracing]
    end

    subgraph Metrics["Key Metrics"]
        K1[Error Rate]
        K2[Response Time]
        K3[Resource Usage]
        K4[Feature Usage]
    end

    subgraph Alerts["Alert Conditions"]
        A1[Error Rate > 1%]
        A2[P95 Latency > 500ms]
        A3[CPU > 80%]
        A4[Memory > 85%]
    end

    M1 --> K1
    M1 --> K2
    M1 --> K3
    M1 --> K4
    
    M3 --> A1
    M3 --> A2
    M3 --> A3
    M3 --> A4

    style Monitoring fill:#e3f2fd
    style Metrics fill:#c8e6c9
    style Alerts fill:#ffcdd2
```

---

### 3.6 Staging vs Production Comparison

| Aspect | Staging | Production Cloud | Production On-Prem |
|--------|---------|-----------------|-------------------|
| **Data** | Anonymized subset | Real customer data | Real customer data |
| **Scale** | 10% of production | Full scale | Varies by customer |
| **External APIs** | Sandbox/Mock | Production | Production |
| **Monitoring** | Full | Full | Customer managed |
| **Access** | Internal + Beta | All customers | Licensed customers |
| **Deployment** | Automatic | Manual gate | Manual + Packaged |
| **Rollback Time** | < 5 minutes | < 5 minutes | Hours/Days |

---

## 4. Developer Guidelines

### 4.1 Commit Message Format

```
[TYPE-ID] Short description (max 72 chars)

Optional longer description explaining the change in detail.
Can span multiple lines.

Refs: #issue-number
```

**Types:**
| Type | Usage |
|------|-------|
| `FEAT` | New feature |
| `BUG` | Bug fix |
| `TASK` | General task/chore |
| `HOTFIX` | Critical production fix |
| `DOCS` | Documentation only |

**Examples:**
```bash
# Good
git commit -m "[FEAT-1234] Add user dashboard with real-time metrics"
git commit -m "[BUG-567] Fix memory leak in data collector service"
git commit -m "[HOTFIX-890] Patch critical authentication bypass"

# Bad
git commit -m "Fixed stuff"
git commit -m "WIP"
git commit -m "Updated code"
```

### 4.2 Branch Naming Convention

```mermaid
flowchart LR
    A[Type] --> B[/] --> C[Ticket-ID] --> D[-] --> E[Description]
    
    style A fill:#e3f2fd
    style C fill:#fff3e0
    style E fill:#e8f5e9
```

**Format:** `{type}/{TICKET-ID}-{short-description}`

| Type | Example |
|------|---------|
| Feature | `feature/FEAT-1234-user-dashboard` |
| Bug Fix | `bugfix/BUG-567-memory-leak` |
| Hotfix | `hotfix/HOTFIX-890-auth-bypass` |

### 4.3 Developer Workflow

```mermaid
sequenceDiagram
    participant D as Developer
    participant F as Feature Branch
    participant DEV as develop
    participant MR as Merge Request
    participant CI as CI Pipeline

    D->>F: Create feature branch
    D->>F: Make changes
    D->>F: Commit with proper format
    D->>F: Push to origin
    F->>MR: Create Merge Request
    MR->>CI: Trigger pipeline
    CI->>CI: Run tests & security scans
    CI->>MR: Report status
    
    alt Pipeline Passes
        MR->>MR: Request code review
        MR->>MR: Get 2 approvals
        MR->>DEV: Merge to develop
        DEV->>F: Delete feature branch
    else Pipeline Fails
        CI->>D: Notify failure
        D->>F: Fix issues
        D->>F: Push fixes
    end
```

### 4.4 Pre-Commit Setup

Install the pre-commit hook to validate commits locally:

```bash
#!/bin/bash
# .git/hooks/commit-msg

commit_msg=$(cat "$1")

# Validate format
if ! echo "$commit_msg" | grep -qE '^\[(FEAT|BUG|TASK|HOTFIX|DOCS)-[0-9]+\]'; then
  echo "❌ ERROR: Invalid commit message format"
  echo ""
  echo "Your message: $commit_msg"
  echo ""
  echo "Required format: [TYPE-ID] Description"
  echo ""
  echo "Examples:"
  echo "  [FEAT-1234] Add new feature"
  echo "  [BUG-567] Fix critical bug"
  echo "  [TASK-890] Update dependencies"
  exit 1
fi

echo "✅ Commit message validated"
```

### 4.5 Developer Checklist

```markdown
## Before Creating MR

- [ ] Branch name follows convention: `{type}/{TICKET-ID}-{description}`
- [ ] All commits use proper format: `[TYPE-ID] Description`
- [ ] Unit tests added/updated for changes
- [ ] No linting errors
- [ ] No security vulnerabilities introduced
- [ ] Documentation updated if needed
- [ ] Self-reviewed the diff

## MR Description Template

### Summary
<!-- What does this MR do? -->

### Related Issues
<!-- Link to Jira/GitLab issues -->
Closes #ISSUE_NUMBER

### Testing Done
<!-- How was this tested? -->
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

### Screenshots (if UI change)
<!-- Add screenshots -->

### Checklist
- [ ] Tests pass
- [ ] Code follows style guidelines
- [ ] Reviewed my own code
```

---

## Appendix A: CI/CD Pipeline Architecture

For detailed CI/CD pipeline configuration, see this section.

### Pipeline Overview

```mermaid
flowchart TB
    subgraph Trigger["Pipeline Triggers"]
        T1[Push to Branch]
        T2[Merge Request]
        T3[Scheduled]
        T4[Manual]
    end

    subgraph Build["Build Stage"]
        B1[Compile Code]
        B2[Build Artifacts]
        B3[Build Containers]
    end

    subgraph Test["Test Stage"]
        TE1[Unit Tests]
        TE2[Integration Tests]
        TE3[E2E Tests]
    end

    subgraph Security["Security Stage"]
        S1[SAST Scan]
        S2[Dependency Scan]
        S3[Container Scan]
        S4[Secret Detection]
    end

    subgraph Quality["Quality Stage"]
        Q1[Code Coverage]
        Q2[Lint Check]
        Q3[SonarQube]
    end

    subgraph Deploy["Deploy Stage"]
        D1[Deploy Staging]
        D2[Deploy Cloud]
        D3[Package On-Prem]
    end

    Trigger --> Build --> Test --> Security --> Quality --> Deploy

    style Trigger fill:#e1f5fe
    style Build fill:#fff3e0
    style Test fill:#e8f5e9
    style Security fill:#ffcdd2
    style Quality fill:#f3e5f5
    style Deploy fill:#c8e6c9
```

### Complete GitLab CI/CD Configuration

```yaml
# .gitlab-ci.yml

variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: "/certs"
  # Feature tracking
  FEATURE_TRACKER_URL: "https://tracker.yourcompany.com"

stages:
  - validate
  - build
  - test
  - security
  - quality
  - merge-staging
  - deploy-staging
  - deploy-cloud
  - release
  - package

# =============================================================================
# TEMPLATES
# =============================================================================

.docker-template: &docker-template
  image: docker:24.0
  services:
    - docker:24.0-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY

.python-template: &python-template
  image: python:3.12
  before_script:
    - pip install -r requirements.txt

# =============================================================================
# VALIDATE STAGE - Commit Format & Branch Naming
# =============================================================================

validate-commits:
  stage: validate
  image: alpine/git
  script:
    - |
      echo "Validating commit message format..."
      
      if [ "$CI_PIPELINE_SOURCE" == "merge_request_event" ]; then
        COMMITS=$(git log origin/$CI_MERGE_REQUEST_TARGET_BRANCH..HEAD --pretty=format:"%s")
      else
        COMMITS=$(git log -1 --pretty=format:"%s")
      fi
      
      ERRORS=0
      while IFS= read -r MSG; do
        if ! echo "$MSG" | grep -qE '^\[(FEAT|BUG|TASK|HOTFIX|DOCS)-[0-9]+\]'; then
          echo "❌ Invalid: $MSG"
          ERRORS=$((ERRORS + 1))
        else
          echo "✅ Valid: $MSG"
        fi
      done <<< "$COMMITS"
      
      if [ $ERRORS -gt 0 ]; then
        echo ""
        echo "Required format: [TYPE-ID] Description"
        echo "Types: FEAT, BUG, TASK, HOTFIX, DOCS"
        exit 1
      fi
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

validate-branch-name:
  stage: validate
  image: alpine
  script:
    - |
      BRANCH=$CI_COMMIT_REF_NAME
      VALID_PATTERNS="^(main|staging|production-cloud|release\/v[0-9]{4}\.[0-9]{2}|feature\/[A-Z]+-[0-9]+.*|bugfix\/[A-Z]+-[0-9]+.*|hotfix\/[A-Z]+-[0-9]+.*)$"
      
      if echo "$BRANCH" | grep -qE "$VALID_PATTERNS"; then
        echo "✅ Branch name valid: $BRANCH"
      else
        echo "❌ Invalid branch name: $BRANCH"
        echo "Valid patterns:"
        echo "  - main, staging, production-cloud"
        echo "  - release/X.Y.x"
        echo "  - feature/FEAT-123-description"
        echo "  - bugfix/BUG-456-description"
        echo "  - hotfix/HOTFIX-789-description"
        exit 1
      fi
  rules:
    - if: '$CI_COMMIT_BRANCH'
  allow_failure: true

# =============================================================================
# BUILD STAGE
# =============================================================================

build-app:
  stage: build
  <<: *docker-template
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH'

build-artifacts:
  stage: build
  <<: *python-template
  script:
    - python setup.py sdist bdist_wheel
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_TAG'

# =============================================================================
# TEST STAGE
# =============================================================================

unit-tests:
  stage: test
  <<: *python-template
  script:
    - pytest tests/unit --junitxml=report.xml --cov=src --cov-report=xml
  artifacts:
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  coverage: '/TOTAL.+ ([0-9]{1,3}%)/'
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

integration-tests:
  stage: test
  <<: *python-template
  services:
    - postgres:15
    - redis:7
  variables:
    POSTGRES_DB: test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_pass
  script:
    - pytest tests/integration --junitxml=integration-report.xml
  artifacts:
    reports:
      junit: integration-report.xml
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH =~ /^release\//'

e2e-tests:
  stage: test
  <<: *docker-template
  script:
    - docker-compose -f docker-compose.test.yml up -d
    - sleep 30
    - docker-compose -f docker-compose.test.yml exec -T app pytest tests/e2e
  after_script:
    - docker-compose -f docker-compose.test.yml down
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
    - if: '$CI_COMMIT_BRANCH =~ /^release\//'

# =============================================================================
# SECURITY STAGE
# =============================================================================

sast:
  stage: security
  image: registry.gitlab.com/security-products/semgrep:latest
  script:
    - semgrep --config=auto --json --output=gl-sast-report.json .
  artifacts:
    reports:
      sast: gl-sast-report.json
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

dependency-scan:
  stage: security
  <<: *python-template
  script:
    - pip install safety
    - safety check --json > dependency-report.json || true
    - cat dependency-report.json
  artifacts:
    paths:
      - dependency-report.json
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

secret-detection:
  stage: security
  image: registry.gitlab.com/security-products/secrets:latest
  script:
    - /analyzer run
  artifacts:
    reports:
      secret_detection: gl-secret-detection-report.json
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_COMMIT_BRANCH == "main"'

container-scan:
  stage: security
  <<: *docker-template
  script:
    - docker pull $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - docker run --rm -v /var/run/docker.sock:/var/run/docker.sock 
        aquasec/trivy image --exit-code 1 --severity HIGH,CRITICAL 
        $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  allow_failure: true

# =============================================================================
# QUALITY STAGE
# =============================================================================

lint:
  stage: quality
  <<: *python-template
  script:
    - pip install flake8 black isort
    - flake8 src/
    - black --check src/
    - isort --check-only src/
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'

sonarqube:
  stage: quality
  image: sonarsource/sonar-scanner-cli:latest
  script:
    - sonar-scanner
        -Dsonar.projectKey=$CI_PROJECT_NAME
        -Dsonar.sources=src
        -Dsonar.host.url=$SONAR_HOST_URL
        -Dsonar.login=$SONAR_TOKEN
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'

# =============================================================================
# MERGE TO STAGING (Automated)
# =============================================================================

merge-main-to-staging:
  stage: merge-staging
  image: alpine/git
  variables:
    GIT_STRATEGY: clone
  before_script:
    - git config --global user.email "ci-bot@yourcompany.com"
    - git config --global user.name "CI Bot"
    - git remote set-url origin https://oauth2:${GITLAB_TOKEN}@gitlab.com/${CI_PROJECT_PATH}.git
  script:
    - |
      git fetch origin staging:staging
      git checkout staging
      
      if git merge origin/main --no-edit; then
        echo "✅ Merge successful"
        git push origin staging
        
        # Extract features for tracking
        FEATURES=$(git log staging..origin/main --pretty=format:"%s" | 
          grep -oE '\[(FEAT|BUG|TASK)-[0-9]+\]' | sort -u || echo "none")
        echo "Features merged: $FEATURES"
      else
        echo "❌ Merge conflict detected"
        git merge --abort
        
        # Notify team
        curl -X POST -H 'Content-type: application/json' \
          --data "{\"text\":\"⚠️ Merge conflict: main → staging. Manual intervention required.\"}" \
          ${SLACK_WEBHOOK_URL}
        exit 1
      fi
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: on_success

# =============================================================================
# DEPLOY STAGING
# =============================================================================

deploy-staging:
  stage: deploy-staging
  image: alpine/k8s:1.28
  environment:
    name: staging
    url: https://staging.yourproduct.com
  script:
    - kubectl config use-context staging
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/app
  rules:
    - if: '$CI_COMMIT_BRANCH == "staging"'

smoke-tests-staging:
  stage: deploy-staging
  <<: *python-template
  needs:
    - deploy-staging
  script:
    - pytest tests/smoke --base-url=https://staging.yourproduct.com
  rules:
    - if: '$CI_COMMIT_BRANCH == "staging"'

# =============================================================================
# DEPLOY CLOUD (Production)
# =============================================================================

deploy-cloud:
  stage: deploy-cloud
  image: alpine/k8s:1.28
  environment:
    name: production-cloud
    url: https://app.yourproduct.com
  script:
    - kubectl config use-context production
    - kubectl set image deployment/app app=$CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
    - kubectl rollout status deployment/app
  rules:
    - if: '$CI_COMMIT_BRANCH == "production-cloud"'
  when: manual

# =============================================================================
# RELEASE STAGE (On-Prem)
# =============================================================================

create-release-branch:
  stage: release
  image: alpine/git
  script:
    - |
      RELEASE_VERSION=$(date +%Y.%m)
      git checkout -b release/v$RELEASE_VERSION
      git push origin release/v$RELEASE_VERSION
      
      echo "Created release branch: release/v$RELEASE_VERSION"
  rules:
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
      when: manual
    - if: '$CI_COMMIT_BRANCH == "main"'
      when: manual

tag-release:
  stage: release
  image: alpine/git
  script:
    - |
      # Extract version from branch name
      VERSION=$(echo $CI_COMMIT_BRANCH | sed 's/release\/v//')
      
      # Check if this is a patch release
      LATEST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
      if echo "$LATEST_TAG" | grep -q "v$VERSION"; then
        PATCH=$(echo $LATEST_TAG | grep -oE '\.[0-9]+$' | tr -d '.')
        NEW_PATCH=$((PATCH + 1))
        TAG="v$VERSION.$NEW_PATCH"
      else
        TAG="v$VERSION.0"
      fi
      
      git tag -a $TAG -m "Release $TAG"
      git push origin $TAG
      
      echo "Created tag: $TAG"
  rules:
    - if: '$CI_COMMIT_BRANCH =~ /^release\//'
      when: manual

# =============================================================================
# PACKAGE STAGE (On-Prem Distribution)
# =============================================================================

package-onprem:
  stage: package
  <<: *docker-template
  script:
    - |
      VERSION=$(echo $CI_COMMIT_TAG | tr -d 'v')
      
      # Build installer package
      docker build -f Dockerfile.onprem -t app-onprem:$VERSION .
      docker save app-onprem:$VERSION | gzip > app-$VERSION.tar.gz
      
      # Build RPM package
      ./scripts/build-rpm.sh $VERSION
      
      # Build documentation
      ./scripts/build-docs.sh $VERSION
  artifacts:
    paths:
      - "*.tar.gz"
      - "*.rpm"
      - docs/
    expire_in: 1 year
  rules:
    - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+$/'

publish-release:
  stage: package
  needs:
    - package-onprem
  script:
    - |
      # Upload to artifact repository
      curl -u $NEXUS_USER:$NEXUS_PASS -X PUT \
        "$NEXUS_URL/repository/releases/app-$CI_COMMIT_TAG.tar.gz" \
        -T app-*.tar.gz
      
      # Create GitLab release
      release-cli create --name "Release $CI_COMMIT_TAG" \
        --tag-name $CI_COMMIT_TAG \
        --description "Release notes for $CI_COMMIT_TAG" \
        --assets-link "{\"name\":\"Installer\",\"url\":\"$NEXUS_URL/repository/releases/app-$CI_COMMIT_TAG.tar.gz\"}"
      
      # Notify customers
      ./scripts/notify-customers.sh $CI_COMMIT_TAG
  rules:
    - if: '$CI_COMMIT_TAG =~ /^v[0-9]+\.[0-9]+\.[0-9]+$/'
```

---

## 5. DevOps Guidelines

### 5.1 Environment Configuration

```mermaid
flowchart TB
    subgraph Environments
        DEV[Development<br/>Local/Dev Server]
        STG[Staging<br/>Pre-Production]
        CLD[Cloud Production<br/>SaaS Users]
        ONP[On-Prem Production<br/>Enterprise Users]
    end

    subgraph Config
        C1[Feature Flags]
        C2[Environment Variables]
        C3[Secrets Management]
    end

    DEV --> STG --> CLD
    STG --> ONP
    
    C1 --> DEV
    C1 --> STG
    C1 --> CLD
    C1 --> ONP
    
    C2 --> DEV
    C2 --> STG
    C2 --> CLD
    C2 --> ONP
    
    C3 --> STG
    C3 --> CLD
    C3 --> ONP

    style DEV fill:#e3f2fd
    style STG fill:#fff3e0
    style CLD fill:#c8e6c9
    style ONP fill:#bbdefb
```

### 5.2 GitLab Project Settings

| Setting | Configuration |
|---------|--------------|
| **Protected Branches** | main, staging, production-*, release/* |
| **Merge Method** | Merge commit with semi-linear history |
| **Squash Commits** | Encourage (not required) |
| **Delete Branch on Merge** | Enabled for feature/* and bugfix/* |
| **Pipeline Required** | main, staging, release/* |
| **Approvals Required** | 2 for main, 1 for release/* |

### 5.3 GitLab Push Rules

```yaml
# Settings → Repository → Push Rules

Commit message regex: ^\[(FEAT|BUG|TASK|HOTFIX|DOCS)-[0-9]+\].*
Branch name regex: ^(main|staging|production-cloud|release\/v[0-9]{4}\.[0-9]{2}|feature\/[A-Z]+-[0-9]+.*|bugfix\/[A-Z]+-[0-9]+.*|hotfix\/[A-Z]+-[0-9]+.*)$
Reject unsigned commits: No
```

### 5.4 Scheduled Pipelines

| Schedule | Branch | Job | Purpose |
|----------|--------|-----|---------|
| Daily 2:00 AM | main | merge-main-to-staging | Keep staging in sync |
| Monthly 1st | main | create-release-branch | Create monthly release |
| Weekly | staging | security-scan | Full security audit |
| Daily | all | dependency-scan | Check for vulnerabilities |

### 5.5 DevOps Checklist

```markdown
## Monthly Release Preparation

### Week 1 (Feature Freeze)
- [ ] Create release branch from main
- [ ] Announce feature freeze to developers
- [ ] Begin QA testing cycle

### Week 2-3 (QA & Stabilization)
- [ ] Fix bugs found in QA
- [ ] Cherry-pick critical fixes only
- [ ] Update release notes

### Week 4 (Release)
- [ ] Final QA sign-off
- [ ] Create release tag
- [ ] Build packages
- [ ] Publish to artifact repository
- [ ] Notify customers
- [ ] Update documentation site

## Post-Release
- [ ] Monitor for issues
- [ ] Prepare hotfix if needed
- [ ] Retrospective meeting
```

### 5.6 Monitoring & Alerts

```yaml
# .gitlab-ci.yml - Monitoring integration

notify-deployment:
  stage: .post
  script:
    - |
      curl -X POST "$DATADOG_WEBHOOK" \
        -H "Content-Type: application/json" \
        -d "{
          \"title\": \"Deployment: $CI_ENVIRONMENT_NAME\",
          \"text\": \"Version $CI_COMMIT_TAG deployed\",
          \"tags\": [\"environment:$CI_ENVIRONMENT_NAME\", \"version:$CI_COMMIT_TAG\"]
        }"
  environment:
    name: $CI_ENVIRONMENT_NAME
    action: access
```

---

## 6. Release Workflows

### 6.1 Cloud Release (Bi-Weekly)

```mermaid
flowchart TB
    A[develop branch updated] --> B[Auto-merge to staging]
    B --> C[Deploy to Staging]
    C --> D{Smoke Tests Pass?}
    D -->|Yes| E[Schedule Cloud Deploy]
    D -->|No| F[Investigate & Fix]
    F --> B
    E --> G[Deploy to production-cloud]
    G --> H[Monitor Metrics]
    H --> I{Issues Detected?}
    I -->|Yes| J[Rollback]
    I -->|No| K[✅ Release Complete]
    J --> F

    style A fill:#e3f2fd
    style G fill:#c8e6c9
    style K fill:#c8e6c9
    style J fill:#ffcdd2
```

### 6.2 On-Prem Release (Monthly)

```mermaid
flowchart TB
    A[Monthly Schedule] --> B[Create release/X.Y.x from main]
    B --> C[Begin QA Testing]
    C --> D{QA Approved?}
    D -->|No| E[Fix Issues in Release Branch]
    E --> C
    D -->|Yes| F[Create Release Tag]
    F --> G[Build Packages]
    G --> H[Upload to Artifact Repo]
    H --> I[Create GitLab Release]
    I --> J[Notify Customers]
    J --> K[Update Documentation]
    K --> L[✅ Release Complete]

    style A fill:#e3f2fd
    style F fill:#fff3e0
    style L fill:#c8e6c9
```

### 6.3 Complete Release Timeline

```mermaid
gantt
    title Monthly Release Cycle
    dateFormat YYYY-MM-DD
    
    section Development
    Feature Development    :dev, 2026-01-01, 21d
    Code Freeze           :crit, freeze, 2026-01-22, 1d
    
    section QA
    QA Testing            :qa, 2026-01-22, 5d
    Bug Fixes             :fix, 2026-01-27, 3d
    Final Validation      :val, 2026-01-30, 1d
    
    section Release
    Create Tag            :tag, 2026-01-31, 1d
    Build Packages        :build, 2026-01-31, 1d
    Publish               :pub, 2026-02-01, 1d
    
    section Post-Release
    Monitor               :mon, 2026-02-01, 7d
    Hotfix Window         :hot, 2026-02-01, 14d
```

---

## 7. Hotfix Procedures

### 7.1 Hotfix Decision Tree

```mermaid
flowchart TD
    A[Critical Issue Reported] --> B{Severity?}
    
    B -->|Critical/Security| C[Immediate Hotfix]
    B -->|High| D{In Cloud or On-Prem?}
    B -->|Medium/Low| E[Schedule for Next Release]
    
    D -->|Cloud Only| F[Fix in main → Deploy]
    D -->|On-Prem| G[Hotfix Procedure]
    D -->|Both| H[Fix Both Tracks]
    
    C --> I[Page On-Call]
    I --> G
    
    G --> J[Create hotfix/* branch from release/*]
    J --> K[Apply fix]
    K --> L[Fast-track QA]
    L --> M[Tag X.Y.Z]
    M --> N[Build & Distribute]
    N --> O[Cherry-pick to main]
    
    H --> F
    H --> G

    style C fill:#ffcdd2
    style I fill:#ffcdd2
    style E fill:#c8e6c9
```

### 7.2 Hotfix Commands

```bash
# 1. Create hotfix branch from latest release
git checkout release/4.21.x
git checkout -b hotfix/HOTFIX-123-critical-fix

# 2. Apply fix
git commit -m "[HOTFIX-123] Fix critical security vulnerability"

# 3. Push and create MR to release branch
git push origin hotfix/HOTFIX-123-critical-fix

# 4. After merge, tag the release
git checkout release/4.21.x
git pull
git tag -a 4.21.1 -m "Hotfix: Security vulnerability patch"
git push origin 4.21.1

# 5. Cherry-pick to main
git checkout main
git cherry-pick <commit-sha>
git push origin main
```

---

## 8. Implementation Checklist

### Phase 1: Foundation (Week 1-2)

```markdown
- [ ] Configure GitLab project settings
  - [ ] Set up protected branches
  - [ ] Configure push rules
  - [ ] Set merge request approvals
- [ ] Set up base CI/CD pipeline
  - [ ] Build stage
  - [ ] Test stage
  - [ ] Security scanning
- [ ] Create branch structure
  - [ ] main (protect)
  - [ ] staging (protect)
  - [ ] production-cloud (protect)
- [ ] Document developer guidelines
```

### Phase 2: Automation (Week 2-3)

```markdown
- [ ] Implement auto-merge main → staging
- [ ] Configure scheduled pipelines
- [ ] Set up deployment pipelines
  - [ ] Staging deployment
  - [ ] Cloud deployment
- [ ] Add notification integrations
  - [ ] Slack/Teams
  - [ ] Email
```

### Phase 3: Release Process (Week 3-4)

```markdown
- [ ] Create release branch automation
- [ ] Set up packaging pipeline
- [ ] Configure artifact repository
- [ ] Create customer notification system
- [ ] Document release runbook
```

### Phase 4: Rollout (Week 4+)

```markdown
- [ ] Train development team
- [ ] Pilot with one team/feature
- [ ] Gather feedback and iterate
- [ ] Full rollout
- [ ] Retrospective and optimization
```

---

## Summary

```mermaid
mindmap
  root((Release Strategy))
    Branching
      main
      staging
      production-cloud
      release/*
      feature/*
    Release Types
      Major (Quarterly)
      Minor (Monthly)
      Patch (As needed)
    CI/CD
      Validate
      Build
      Test
      Security
      Deploy
    Roles
      Developer
        Commit format
        Branch naming
        Code review
      DevOps
        Pipeline config
        Release management
        Monitoring
```

---

## Quick Reference Card

| Action | Command/Location |
|--------|-----------------|
| Create feature branch | `git checkout -b feature/FEAT-123-description` |
| Commit change | `git commit -m "[FEAT-123] Description"` |
| View pipeline | GitLab → CI/CD → Pipelines |
| Create release | GitLab → CI/CD → Schedules → Run |
| View deployments | GitLab → Deployments → Environments |
| Hotfix procedure | See Section 7 |

---

## Appendix B: Release Type Definitions

```mermaid
flowchart TB
    subgraph Major["MAJOR Release (Quarterly)"]
        MA[Breaking Changes]
        MB[New Major Features]
        MC[Architecture Updates]
        MD[Deprecation Removals]
    end

    subgraph Minor["MINOR Release (Monthly)"]
        MIA[New Features]
        MIB[Enhancements]
        MIC[Non-Breaking Changes]
        MID[Performance Improvements]
    end

    subgraph Patch["PATCH/Maintenance (As Needed)"]
        PA[Bug Fixes]
        PB[Security Patches]
        PC[Critical Hotfixes]
        PD[Documentation Updates]
    end

    Major --> Minor --> Patch

    style Major fill:#ffcdd2,stroke:#c62828
    style Minor fill:#fff3e0,stroke:#e65100
    style Patch fill:#c8e6c9,stroke:#2e7d32
```

| Release Type | Frequency | Scope | Breaking Changes | QA Cycle |
|-------------|-----------|-------|------------------|----------|
| **Major** | Quarterly | Large features, architecture changes | Allowed | 2-4 weeks |
| **Minor** | Monthly | Features, enhancements | Not allowed | 1 week |
| **Patch** | As needed | Bug fixes, security | Not allowed | 1-3 days |

---

*Last Updated: January 2026*
*Version: 2.0*
