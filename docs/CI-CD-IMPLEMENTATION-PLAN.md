# Weather Kitchen Backend - CI/CD Implementation Plan

**Document Version**: 1.0 - Initial Plan
**Created**: February 16, 2026
**Status**: Ready for Implementation
**Overall Progress**: 0/18 tasks (0%)
**Last Updated**: February 16, 2026

---

## Overview

Comprehensive CI/CD pipeline for the Weather Kitchen FastAPI backend, integrating with ArgoCD and a separate GitOps repository for declarative deployments. The pipeline enforces security, quality, and performance standards across all phases of backend development.

### Key Characteristics

- **PR-based CI**: Runs on every push (lint, test, security, coverage)
- **Release Workflow**: Manual semantic versioning with auto-generated release notes
- **Container Registry**: AWS ECR with multi-tag strategy
- **GitOps Integration**: Automatic PR creation in separate Kubernetes repository
- **Pre-deployment Checks**: Coverage >80%, security scan, migration validation
- **Deployment Waves**: ConfigMaps/Secrets (Wave 0), Application (Wave 1)
- **Database Safety**: Alembic migrations run on container startup
- **Progressive Rollout**: Support for canary/blue-green via ArgoCD

---

## Architecture Overview

### Workflow Chain

```
1. Developer Push to Feature Branch
   ↓
2. GitHub PR Created
   ↓
3. PR CI Workflow Triggered
   ├─ Ruff Lint Check
   ├─ pytest (unit + integration + security)
   ├─ Coverage Report (>80% required)
   ├─ Bandit Security Scan
   ├─ Docker Build Validation
   └─ GitHub PR Status Updated
   ↓
4. Merge to Main Branch
   ↓
5. Manual Release Workflow (workflow_dispatch)
   ├─ Calculate/validate new version
   ├─ Generate release notes from commits
   ├─ Build Docker images (multi-tag)
   ├─ Push to ECR with retry logic
   ├─ Create GitHub release
   ├─ Create/merge GitOps PR
   └─ Output new version for deployment
   ↓
6. GitOps Repository Updated
   ├─ Deployment manifest updated with new image version
   ├─ PR created with detailed description
   ├─ Optional auto-merge triggers ArgoCD sync
   └─ ArgoCD detects changes and deploys
   ↓
7. Deployment Execution
   ├─ Wave 0: ConfigMaps, Secrets created/updated
   ├─ Wave 1: Deployment rolls out new image
   ├─ Alembic migrations run on container startup
   ├─ Health checks verify deployment
   └─ ArgoCD marks sync as successful
```

### GitHub Actions Workflows

```
.github/workflows/
├── pr-ci.yml                      # PR-based CI (lint, test, security, coverage)
├── backend-release-and-deploy.yml # Release + ECR + GitOps workflow
└── README.md                       # Workflow documentation
```

---

## Phase 1: PR-based CI Foundation

**Goal**: Establish automated quality gates on every PR
**Estimated Time**: 1 week
**Tasks**: 6

### Subphase 1A: CI Workflow Setup

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 1 | Create PR CI workflow (scaffold) | `.github/workflows/pr-ci.yml` | ⬜ | Basic structure, triggers on PR/push to main |
| 2 | Add Ruff linting step | `pr-ci.yml` | ⬜ | `ruff check app/ tests/` with zero-error enforcement |
| 3 | Add pytest step (unit + integration) | `pr-ci.yml` | ⬜ | `pytest tests/unit tests/integration --tb=short` |
| 4 | Add coverage report step | `pr-ci.yml` | ⬜ | `pytest --cov=app` with >80% threshold, fail if below |
| 5 | Add Bandit security scan | `pr-ci.yml` | ⬜ | `bandit -r app/ -f json` with HIGH/CRITICAL failure |
| 6 | Add Docker build validation | `pr-ci.yml` | ⬜ | `docker build -f backend/Dockerfile .` (build only, no push) |

### Subphase 1B: GitHub PR Status Integration

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 7 | Configure PR status checks | `pr-ci.yml` | ⬜ | Mark required: lint, test, coverage, security, docker-build |
| 8 | Add code coverage comment | `pr-ci.yml` | ⬜ | Comment on PR with coverage % and trend (+/-) |
| 9 | Add workflow summary | `pr-ci.yml` | ⬜ | Post step summary with all check results and links |

### Phase 1 Acceptance Criteria

- [ ] PR CI runs on every push to any branch
- [ ] All 6 check types execute in parallel (< 10 min total)
- [ ] Ruff lint failures block merge (required status check)
- [ ] Coverage <80% blocks merge (required status check)
- [ ] Bandit HIGH/CRITICAL security issues block merge
- [ ] Docker build must succeed (or workflow fails gracefully)
- [ ] Coverage comment posted on every PR
- [ ] Workflow summary shows all results and pass/fail status

---

## Phase 2: Release & Versioning Workflow

**Goal**: Automated semantic versioning and GitHub release creation
**Estimated Time**: 1-2 weeks
**Tasks**: 8

### Subphase 2A: Release Workflow Core

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 1 | Create release workflow (scaffold) | `.github/workflows/backend-release-and-deploy.yml` | ⬜ | workflow_dispatch trigger with input parameters |
| 2 | Add version calculation logic | `backend-release-and-deploy.yml` | ⬜ | Support patch/minor/major/custom versions; validate semver format |
| 3 | Add release notes generation | `backend-release-and-deploy.yml` | ⬜ | Auto-generate from git log or use manual input; include changelog format |
| 4 | Add secret validation step | `backend-release-and-deploy.yml` | ⬜ | Check AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, ECR_REPOSITORY configured |
| 5 | Add tag creation & push | `backend-release-and-deploy.yml` | ⬜ | Create annotated tag, push to origin, fail if tag exists |
| 6 | Add GitHub release creation | `backend-release-and-deploy.yml` | ⬜ | Create GitHub release with tag, version, and release notes |

### Subphase 2B: Release Workflow Inputs & Outputs

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 7 | Document workflow inputs | `backend-release-and-deploy.yml` | ⬜ | release_type, version (custom), release_notes, skip_deploy, update_gitops, auto_merge |
| 8 | Define workflow outputs | `backend-release-and-deploy.yml` | ⬜ | new_version (v1.2.3), version_number (1.2.3), ecr_registry, image_pushed boolean |

### Phase 2 Acceptance Criteria

- [ ] Release workflow can be triggered manually with inputs
- [ ] Version calculation works for patch/minor/major/custom
- [ ] Custom version input validated (semver format X.Y.Z)
- [ ] Release notes auto-generated from commit history or manual input
- [ ] Tag created and pushed to origin
- [ ] GitHub release created with correct version and notes
- [ ] Workflow outputs available for downstream jobs
- [ ] Dry-run capability (skip_deploy = true)

---

## Phase 3: Docker Build & ECR Deployment

**Goal**: Build and push Docker images with multi-tag strategy
**Estimated Time**: 1-2 weeks
**Tasks**: 9

### Subphase 3A: Docker Build Pipeline

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 1 | Add Docker Buildx setup | `backend-release-and-deploy.yml` | ⬜ | docker/setup-buildx-action for multi-platform builds |
| 2 | Add Docker build step | `backend-release-and-deploy.yml` | ⬜ | Build image with cache-from GHA, cache-to GHA max, linux/amd64 platform |
| 3 | Add multi-tag strategy | `backend-release-and-deploy.yml` | ⬜ | Tags: full version, major.minor, major, latest, sha-{commit} |
| 4 | Add BUILD_ARGS to Dockerfile | `backend-release-and-deploy.yml` | ⬜ | BUILD_VERSION, BUILD_DATE for image metadata |
| 5 | Update Dockerfile (if needed) | `backend/Dockerfile` | ⬜ | Verify multi-stage build, non-root user, health check endpoint |

### Subphase 3B: ECR Push with Retry Logic

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 6 | Configure AWS credentials | `backend-release-and-deploy.yml` | ⬜ | aws-actions/configure-aws-credentials with OIDC or static keys |
| 7 | ECR login step | `backend-release-and-deploy.yml` | ⬜ | aws-actions/amazon-ecr-login with mask-password=true |
| 8 | Add push step with retry logic | `backend-release-and-deploy.yml` | ⬜ | Custom shell function: retry 3x with 10s delay on failure |
| 9 | Add image digest output | `backend-release-and-deploy.yml` | ⬜ | Capture and output image digest for audit trail |

### Phase 3 Acceptance Criteria

- [ ] Docker image builds successfully with cache strategy
- [ ] Multi-tag strategy applied (version, major.minor, major, latest, sha)
- [ ] Image pushed to ECR with all tags
- [ ] Push failures retried 3x before failing workflow
- [ ] Image digest captured for audit trail
- [ ] BUILD_VERSION and BUILD_DATE included in image metadata
- [ ] Conditional: if skip_deploy=true, build step still executes but push skipped
- [ ] AWS secret validation prevents failed pushes due to misconfiguration

---

## Phase 4: GitOps Repository Integration

**Goal**: Automatic deployment manifest updates in GitOps repository
**Estimated Time**: 1-2 weeks
**Tasks**: 10

### Subphase 4A: GitOps Repository Checkout & Setup

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 1 | Add GitOps PAT validation | `backend-release-and-deploy.yml` | ⬜ | Check GITOPS_PAT secret configured; skip job if missing (warning) |
| 2 | Add GitOps repo checkout | `backend-release-and-deploy.yml` | ⬜ | Checkout separate repository (e.g., arigsela/kubernetes) with PAT |
| 3 | Install yq tool | `backend-release-and-deploy.yml` | ⬜ | Download and install yq for YAML manipulation |
| 4 | Add deployment manifest path config | `backend-release-and-deploy.yml` | ⬜ | Parameterize manifest path (e.g., base-apps/weather-kitchen-backend/deployments.yaml) |

### Subphase 4B: Manifest Update Logic

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 5 | Create image tag update function | `backend-release-and-deploy.yml` | ⬜ | Custom function: extract base image, update tag, verify change |
| 6 | Add manifest update step | `backend-release-and-deploy.yml` | ⬜ | Update image tag in deployment spec using sed/yq |
| 7 | Add verification step | `backend-release-and-deploy.yml` | ⬜ | Verify image tag updated correctly, fail if mismatch |
| 8 | Handle multiple manifests | `backend-release-and-deploy.yml` | ⬜ | Support multiple deployment targets (e.g., staging, production) |

### Subphase 4C: GitOps PR Creation & Merge

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 9 | Add PR creation step | `backend-release-and-deploy.yml` | ⬜ | Use peter-evans/create-pull-request with detailed description |
| 10 | Add optional auto-merge | `backend-release-and-deploy.yml` | ⬜ | If auto_merge=true, enable auto-merge on PR (use gh pr merge) |

### Phase 4 Acceptance Criteria

- [ ] GitOps repository checked out with PAT authentication
- [ ] Deployment manifest located and validated
- [ ] Image tag updated in manifest without affecting other fields
- [ ] yq or sed used to safely manipulate YAML
- [ ] PR created with:
  - Clear title (e.g., "chore: update weather-kitchen-backend to v1.2.3")
  - Comprehensive description with version, release URL, workflow link
  - Deployment checklist for manual verification
  - Labels: deployment, automated, weather-kitchen-backend
  - Assignee set to project owner
- [ ] Auto-merge capability works when enabled
- [ ] If GitOps update fails, main release workflow still succeeds (warning)
- [ ] PR body includes deployment wave strategy notes

---

## Phase 5: Pre-Deployment Safety Checks

**Goal**: Validate deployment readiness with quality & security gates
**Estimated Time**: 1 week
**Tasks**: 8

### Subphase 5A: Pre-Deploy Validation Steps (in PR CI & Release)

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 1 | Verify coverage >80% (in PR CI) | `pr-ci.yml` | ⬜ | Coverage step already in Phase 1; add explicit gate |
| 2 | Verify Bandit scan passes (in PR CI) | `pr-ci.yml` | ⬜ | Fail workflow if HIGH/CRITICAL security issues found |
| 3 | Test Alembic migration integrity | `pr-ci.yml` | ⬜ | Run `alembic upgrade head` on test DB; verify schema |
| 4 | Test migration downgrade (Phase 5) | `pr-ci.yml` | ⬜ | For each new migration: run upgrade then downgrade, verify reversible |
| 5 | Add database connectivity test | `pr-ci.yml` | ⬜ | Verify health check endpoint can connect to DB (test DB for CI) |

### Subphase 5B: Deployment Pre-Checks in Release Workflow

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 6 | Add pre-release validation | `backend-release-and-deploy.yml` | ⬜ | Before creating release: verify all PR CI checks passed on main |
| 7 | Add Docker image layer security scan (Phase 5) | `backend-release-and-deploy.yml` | ⬜ | Optional: scan built image with Grype or Trivy for CVEs |
| 8 | Add deployment readiness checklist | `backend-release-and-deploy.yml` | ⬜ | Post workflow summary with deployment readiness verification |

### Phase 5 Acceptance Criteria

- [ ] Coverage <80% fails PR CI workflow
- [ ] Bandit HIGH/CRITICAL issues fail PR CI workflow
- [ ] Alembic migrations verify reversible (up/down)
- [ ] Database connectivity tests pass
- [ ] Release workflow validates main branch CI passed
- [ ] Optional: Docker image scanned for CVEs
- [ ] Pre-deployment checklist shows in workflow summary
- [ ] Release blocked if pre-deployment checks fail

---

## Phase 6: Deployment Strategy & Monitoring

**Goal**: Define ArgoCD deployment waves, rollout strategy, and monitoring
**Estimated Time**: 1 week
**Tasks**: 8

### Subphase 6A: ArgoCD Application Configuration

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 1 | Design ArgoCD Application manifest | `k8s-monitor/base-apps/weather-kitchen-backend/app.yaml` (GitOps repo) | ⬜ | Define namespace, source (Git), destination (cluster), sync policy |
| 2 | Configure sync waves for deployments | `k8s-monitor/base-apps/weather-kitchen-backend/deployments.yaml` | ⬜ | Wave 0: ConfigMaps, Secrets; Wave 1: Deployment |
| 3 | Add health assessment rules | `k8s-monitor/base-apps/weather-kitchen-backend/app.yaml` | ⬜ | Custom health checks: Deployment ready, endpoints exist |
| 4 | Configure automatic rollout strategy | `k8s-monitor/base-apps/weather-kitchen-backend/deployments.yaml` | ⬜ | Strategy: RollingUpdate, maxUnavailable=0, maxSurge=1 (blue-green style) |

### Subphase 6B: Migration Strategy & Database Safety

| # | Task | File(s) | Status | Details |
|---|------|---------|--------|---------|
| 5 | Document Alembic migration on startup | `backend/README.md`, `scripts/start.sh` | ⬜ | Migration runs before app starts: `alembic upgrade head` |
| 6 | Add migration job (optional) | `k8s-monitor/base-apps/weather-kitchen-backend/migrations-job.yaml` (GitOps repo) | ⬜ | Optional: pre-deployment Job for migrations (Wave 0.5) |
| 7 | Add readiness probe check | `k8s-monitor/base-apps/weather-kitchen-backend/deployments.yaml` | ⬜ | Probe hits `/health` endpoint (DB connectivity verification) |
| 8 | Document rollback procedure | `docs/DEPLOYMENT.md` | ⬜ | Manual: revert deployment image tag, ArgoCD syncs automatically |

### Phase 6 Acceptance Criteria

- [ ] ArgoCD Application manifest configured with sync waves
- [ ] Wave 0: ConfigMaps/Secrets created/updated before application
- [ ] Wave 1: Deployment image updated and rolled out
- [ ] Alembic migrations run on container startup (before app)
- [ ] Readiness probe validates database connectivity
- [ ] Rolling update strategy prevents downtime (maxUnavailable=0)
- [ ] Rollback procedure documented and tested
- [ ] Database rollback procedure documented (if needed)
- [ ] Post-deployment health check in workflow (optional)

---

## Workflow Files Specification

### `.github/workflows/pr-ci.yml` - Pull Request CI

**Purpose**: Runs on every push to validate code quality, tests, and security
**Triggers**:
- `pull_request: [opened, synchronize, reopened]`
- `push: [branches: [main]]`

**Environment & Permissions**:
```yaml
env:
  COVERAGE_THRESHOLD: 80
  RUFF_CACHE_DIR: ${{ runner.temp }}/.ruff_cache
  PYTEST_CACHE_DIR: ${{ runner.temp }}/.pytest_cache

permissions:
  contents: read
  pull-requests: write
  checks: write
```

**Jobs**:
1. `lint`: Ruff check (< 2 min)
2. `test`: pytest unit + integration + security (< 8 min)
3. `coverage`: Coverage report with PR comment (< 1 min)
4. `security`: Bandit scan (< 1 min)
5. `docker-build`: Docker build validation (< 3 min)

**Key Steps**:
- Checkout with full history (for diff detection)
- Cache: pip packages, ruff cache, pytest cache
- Python setup: 3.12
- Generate coverage HTML report
- Comment on PR with coverage %
- Bandit JSON output for parsing
- Docker build with cache-from GHA

**Post-Merge Actions**:
- Update PR status checks
- Block merge if any check fails (required)

---

### `.github/workflows/backend-release-and-deploy.yml` - Release & Deploy

**Purpose**: Creates versioned releases and deploys to ECR + GitOps repo
**Trigger**: `workflow_dispatch` (manual)

**Inputs**:
```yaml
release_type:
  type: choice
  options: [patch, minor, major, custom]
version:
  type: string
  description: "Required if release_type=custom (format: X.Y.Z)"
release_notes:
  type: string
  description: "Optional; auto-generated from commits if empty"
skip_deploy:
  type: boolean
  default: false
  description: "Skip ECR deployment (for testing)"
update_gitops:
  type: boolean
  default: true
  description: "Update GitOps repository"
auto_merge:
  type: boolean
  default: false
  description: "Auto-merge GitOps PR"
```

**Secrets Required**:
```yaml
AWS_REGION
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
ECR_REPOSITORY
GITOPS_PAT              # GitHub token for GitOps repo
```

**Jobs**:
1. `release-and-deploy`: Build, push, create release (30 min timeout)
   - Outputs: new_version, version_number, ecr_registry, image_pushed
2. `gitops-update`: Update GitOps repo + create PR (conditional, 10 min timeout)

**Deployment Safety**:
- Skip ECR push if AWS secrets missing (warning)
- Skip GitOps update if GITOPS_PAT missing (warning)
- Validate version format (X.Y.Z) for custom releases
- Fail if tag already exists
- Retry push 3x before failing

---

## Integration Points

### With Backend Implementation Plan

**Phase 1 Dependencies**:
- `.github/workflows/backend-ci.yml` scaffold completed (Task in Phase 1, Subphase 1C)
- pyproject.toml dependencies pinned and tested

**Phase 6 Dependencies**:
- Docker image build and push logic aligned (Phase 6, Subphase 6A)
- Bandit security scanning integrated (Phase 6, Subphase 6B)
- Coverage reporting requirements confirmed (>80%)

### With GitOps Repository

**Expected Structure** (arigsela/kubernetes):
```
base-apps/
└── weather-kitchen-backend/
    ├── kustomization.yaml
    ├── deployments.yaml      # Updated by workflow
    ├── services.yaml
    ├── configmap.yaml
    ├── secrets.yaml          # Encrypted with sealed-secrets
    ├── hpa.yaml              # Horizontal Pod Autoscaler (optional)
    └── app.yaml              # ArgoCD Application manifest
```

**Workflow Manifest Update**:
- Updates image tag in: `.spec.template.spec.containers[0].image`
- Creates PR: `update-weather-kitchen-backend-{version}`
- PR body includes deployment checklist and wave strategy

### With ArgoCD

**Sync Waves**:
```yaml
# Wave 0: Pre-deployment resources
apiVersion: v1
kind: ConfigMap
metadata:
  argocd.argoproj.io/compare-result: unknown
  annotations:
    argocd.argoproj.io/sync-wave: "0"

# Wave 1: Application deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  annotations:
    argocd.argoproj.io/sync-wave: "1"
```

---

## Pre-Implementation Checklist

### Repository Configuration

- [ ] GitHub repository secrets configured:
  - `AWS_REGION` (e.g., us-east-2)
  - `AWS_ACCESS_KEY_ID` (with ECR push permissions)
  - `AWS_SECRET_ACCESS_KEY`
  - `ECR_REPOSITORY` (e.g., weather-kitchen-backend)
  - `GITOPS_PAT` (GitHub token with write:repo permissions for GitOps repo)

- [ ] AWS IAM permissions verified:
  - `ecr:GetAuthorizationToken`
  - `ecr:BatchGetImage`
  - `ecr:GetDownloadUrlForLayer`
  - `ecr:PutImage`
  - `ecr:InitiateLayerUpload`
  - `ecr:UploadLayerPart`
  - `ecr:CompleteLayerUpload`

- [ ] GitHub branch protection configured:
  - Require PR review (optional)
  - Require status checks: lint, test, coverage, security, docker-build
  - Dismiss stale reviews on push (optional)
  - Allow force pushes: NO
  - Allow deletions: NO

### Docker & Dockerfile

- [ ] Backend Dockerfile verified:
  - Multi-stage build (build stage + runtime stage)
  - Non-root user (appuser)
  - Health check endpoint: `HEALTHCHECK CMD curl http://localhost:8000/health`
  - No hardcoded secrets or credentials
  - .dockerignore excludes: `.env`, `.git`, `tests/`, `__pycache__`

### GitOps Repository

- [ ] GitOps repository structure created
- [ ] ArgoCD Application manifest template prepared
- [ ] Deployment manifest template with configurable image tag
- [ ] Sync wave annotations added to manifests
- [ ] Branch protection rules enforced (main branch)

### Testing

- [ ] PR CI workflow tested locally (act tool or manual trigger)
- [ ] Release workflow tested with skip_deploy=true
- [ ] GitOps PR creation tested with dummy version
- [ ] Migration testing (Alembic up/down) verified
- [ ] Coverage thresholds validated with test data

### Documentation

- [ ] `docs/CI-CD-WORKFLOW.md` created (user guide)
- [ ] `docs/DEPLOYMENT.md` updated with wave strategy
- [ ] `backend/README.md` includes quick start with env vars
- [ ] GitHub wiki updated with release process

---

## Implementation Sequence

### Week 1: PR CI Foundation (Phase 1)

1. Create `.github/workflows/pr-ci.yml` scaffold
2. Add Ruff linting step
3. Add pytest steps (unit + integration + security)
4. Add coverage report with >80% threshold
5. Add Bandit security scan
6. Add Docker build validation
7. Test on feature branch PR

### Week 2: Release Workflow (Phase 2-3)

1. Create `.github/workflows/backend-release-and-deploy.yml` scaffold
2. Add version calculation logic
3. Add release notes generation
4. Add Docker build & push to ECR
5. Add GitHub release creation
6. Test with skip_deploy=true

### Week 3: GitOps Integration (Phase 4)

1. Configure GitOps repository structure
2. Add GitOps checkout & yq setup
3. Add deployment manifest update logic
4. Add PR creation with peter-evans/create-pull-request
5. Add optional auto-merge
6. Test PR creation in GitOps repo

### Week 4: Safety & Deployment (Phase 5-6)

1. Add migration validation tests
2. Add database connectivity checks
3. Add pre-deployment validation steps
4. Document ArgoCD sync wave strategy
5. Test full end-to-end workflow (manual release)
6. Document rollback procedure

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| PR CI Runtime | < 10 min | GitHub Actions workflow summary |
| Coverage Threshold Enforcement | >80% | Workflow fails if coverage below |
| Security Test Coverage | 50+ tests | pytest security/ test count |
| Bandit Scan | 0 HIGH/CRITICAL | Bandit JSON output review |
| Release Workflow Runtime | < 30 min | Workflow execution time |
| ECR Push Success Rate | 100% (with retries) | Successful image push in 1-3 attempts |
| GitOps PR Creation | Automated | PR created and mergeable in GitOps repo |
| Deployment Validation | Pre-flight checks pass | Readiness probe + health check success |
| Migration Reversibility | 100% | All migrations pass up + down |
| Zero Deployment Downtime | RollingUpdate strategy | maxUnavailable=0, maxSurge=1 |

---

## Risk Mitigation

### Risk: AWS Credentials Misconfigured

**Impact**: ECR push fails, release incomplete
**Mitigation**:
- Pre-flight secret validation in workflow
- Warning instead of error if secrets missing (allow dry-run releases)
- Detailed error messages with debugging information
- Documentation with setup guide

### Risk: GitOps Manifest Update Fails

**Impact**: Image tag not updated, ArgoCD deploys old version
**Mitigation**:
- Verify image tag change before continuing
- Separate job failure doesn't block release workflow
- PR creation validation and fallback
- Manual GitOps update procedure documented

### Risk: Alembic Migration Breaks Production

**Impact**: Application startup fails, Pod CrashLoopBackOff
**Mitigation**:
- All migrations must be reversible (tested in PR CI)
- Migration test step in PR CI workflow
- Readiness probe delays service registration until app ready
- Rollback procedure documented (revert image tag)
- Pre-deployment migration validation in release workflow

### Risk: Version Tag Already Exists

**Impact**: Release workflow fails when tagging
**Mitigation**:
- Check if tag exists before attempting creation
- Provide clear error message
- User must fix version and retry manually
- Prevent accidental overwrite of existing releases

### Risk: Coverage Threshold Too High

**Impact**: Legitimate PRs blocked
**Mitigation**:
- >80% target is community standard
- Reviewers can override in exceptional cases
- Threshold adjustable in workflow (environment variable)
- Document rationale in CLAUDE.md

---

## Deployment Workflow Diagram

```
┌─────────────────────────┐
│   Developer Commits     │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│  Push to Feature Branch │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────┐
│          PR CI Workflow Triggered                   │
│  - Ruff lint                                        │
│  - pytest (unit + integration + security)           │
│  - Coverage >80%                                    │
│  - Bandit security scan                             │
│  - Docker build validation                          │
└────────────┬────────────────────────────────────────┘
             │
          PASS?
           / \
          /   \
        YES   NO ──→ Feedback to Developer
         │         PR Status: FAILED
         │         (Fix issues, re-push)
         │
         ▼
┌─────────────────────────┐
│  PR Approved & Merged   │
│  to Main Branch         │
└────────────┬────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Manual Release Trigger (workflow_dispatch)  │
│  Input: release_type, version (optional)     │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Release & Deploy Workflow                   │
│  1. Calculate version (patch/minor/major)    │
│  2. Generate release notes                   │
│  3. Create Git tag                           │
│  4. Build Docker images (multi-tag)          │
│  5. Push to ECR (with retry)                 │
│  6. Create GitHub release                    │
└────────────┬─────────────────────────────────┘
             │
          SUCCESS?
           / \
          /   \
        YES   NO ──→ Manual Intervention
         │          (Fix issue, retry)
         │
         ▼
┌──────────────────────────────────────────────┐
│  GitOps Update Job (Parallel)                │
│  1. Checkout GitOps repo                     │
│  2. Update deployment image tag              │
│  3. Create PR in GitOps repo                 │
│  4. Optional: Auto-merge                     │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  ArgoCD Detects Changes                      │
│  (via GitOps repo sync)                      │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Wave 0: ConfigMaps & Secrets Updated        │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Wave 1: Deployment Rolls Out                │
│  1. New Pod starts with new image            │
│  2. Alembic migrations run on startup        │
│  3. Readiness probe validates connectivity   │
│  4. Old Pod terminates after new is ready    │
└────────────┬─────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────┐
│  Deployment Complete                         │
│  - All health checks passing                 │
│  - Traffic routed to new version             │
│  - Monitoring dashboards updated             │
└──────────────────────────────────────────────┘
```

---

## Commands & Quick Reference

### Local Workflow Testing

```bash
# Test PR CI workflow with act (GitHub Actions emulator)
act pull_request --job lint
act pull_request --job test
act pull_request --job coverage

# Test Docker build locally
docker build -f backend/Dockerfile -t weather-kitchen-api:test .

# Verify Ruff linting
cd backend
python -m ruff check app/ tests/

# Verify pytest & coverage
pytest tests/ --cov=app --cov-report=term-missing
```

### Release Workflow Manual Trigger

```bash
# Via GitHub CLI (requires gh auth login)
gh workflow run backend-release-and-deploy.yml \
  -f release_type=minor \
  -f update_gitops=true \
  -f auto_merge=false

# Or visit: https://github.com/arigsela/weather-kitchen/actions/workflows/backend-release-and-deploy.yml
# And click "Run workflow" with parameters
```

### GitOps Repo Manual Update (fallback)

```bash
# If automatic GitOps update fails:
cd ~/kubernetes

# Install yq if needed
sudo wget -qO /usr/bin/yq https://github.com/mikefarah/yq/releases/latest/download/yq_linux_amd64
sudo chmod +x /usr/bin/yq

# Update deployment image manually
NEW_VERSION="1.2.3"
yq eval ".spec.template.spec.containers[0].image |= \"weather-kitchen-api:$NEW_VERSION\"" \
  base-apps/weather-kitchen-backend/deployments.yaml

# Create PR manually or push directly to main (if auto-merge enabled in ArgoCD)
```

---

## Next Steps

1. **Immediate**: Create `.github/workflows/pr-ci.yml` (Phase 1)
2. **Week 2**: Create `.github/workflows/backend-release-and-deploy.yml` (Phase 2-3)
3. **Week 3**: Configure GitOps repository integration (Phase 4)
4. **Week 4**: Document ArgoCD deployment strategy (Phase 5-6)
5. **Ongoing**: Update as backend implementation progresses

---

**Document Status**: Ready for Implementation
**Last Updated**: February 16, 2026
**Current Progress**: 0/18 tasks (0%)
**Next Phase**: Phase 1 - PR CI Foundation (Phase 1 of Backend Plan)
