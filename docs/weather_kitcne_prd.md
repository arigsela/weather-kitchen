# Weather Kitchen - Production Rebuild PRD

**Document Version**: 1.0
**Status**: Ready for Agent-Driven Implementation Planning
**Target Audience**: AI agents tasked with creating detailed implementation plan
**Estimated Build Time**: 8-12 weeks for full production deployment

---

## 1. VISION & OBJECTIVES

### 1.1 Vision Statement
A delightful, secure, and scalable recipe discovery app that suggests weather-appropriate meals to families. Designed for children aged 6-12 with parental oversight, featuring ingredient-based recipe matching and personalized favorites.

### 1.2 Core Objectives
1. **Security**: OWASP Top 10 compliant, COPPA/GDPR compliant for children's data
2. **Performance**: Sub-200ms API responses, 90%+ payload compression, < 10 database queries per request
3. **Reliability**: 99.9% uptime, comprehensive error handling, full audit logging
4. **Maintainability**: Clean architecture, >80% test coverage, complete documentation
5. **Scalability**: Support 100+ concurrent users, multi-family deployment

### 1.3 Non-Goals (Out of Scope)
- Real-time collaboration
- Mobile app (web responsive only)
- Social features (sharing between families)
- AI-powered recipe generation
- Nutritional information tracking

---

## 2. CURRENT STATE ANALYSIS (Critical Findings Summary)

### 2.1 Existing Codebase Assessment
- **Language/Stack**: Python 3.8+ (stdlib only), SQLite, Vanilla JavaScript
- **Current Coverage**: 0% test coverage, 12/100 documentation score
- **Security Score**: 2/10 (28 vulnerabilities identified, 5 critical)
- **Performance Score**: 3/10 (3,061 unnecessary queries identified)
- **Architecture Score**: 3.7/10 (monolithic, no separation of concerns)

### 2.2 Critical Issues Blocking Production
1. **XSS Vulnerabilities**: 17 innerHTML injection points in frontend
2. **Database Exposure**: SQLite file downloadable via HTTP (GET /recipes.db)
3. **Source Code Exposure**: All .py files publicly downloadable
4. **No Authentication**: Zero access control on any endpoint
5. **Schema Drift**: 3 conflicting schema definitions across files
6. **N+1 Queries**: 3,061 queries for 1,020 recipes (should be 4)
7. **COPPA Violation**: Children's data collected without parental consent mechanism
8. **Zero Logging**: Security logging completely disabled

### 2.3 Recommended Approach
**Rather than patching existing code**: Redesign for production using the existing zero-dependency philosophy but with proper architecture, security-first design, and comprehensive testing.

---

## 3. PRODUCT REQUIREMENTS

### 3.1 User Personas

#### 3.1.1 Primary: Eleanor (Age 9, Child User)
- Wants to discover fun recipes based on weather
- Needs simple UI with large buttons
- Interested in recipes with fun emoji and playful tips
- Tracks "favorite" recipes
- Selects ingredients available in pantry

#### 3.1.2 Secondary: Parent/Guardian
- Wants to monitor data collection
- Needs privacy assurance
- Wants ability to delete family data
- May manage multiple children
- Requires parental consent mechanism

#### 3.1.3 Tertiary: Family Admin (Parent Creating Family)
- Sets up family account
- Manages family-level settings
- Controls data visibility
- Can reset app or delete family

### 3.2 Core Features

#### 3.2.1 Weather-Based Recipe Discovery
**Requirement**: Display recipes matching current/selected weather
- Support 10 weather types: sunny, rainy, snowy, hot, windy, cloudy, rainbow, drizzly, stormy, foggy
- Display ~80-100 recipes per weather type
- Show recipe count per weather
- Quick preview: name, emoji, serves, cooking time estimate

**Technical Constraint**: Must work offline (client has local database)

#### 3.2.2 Ingredient-Based Filtering
**Requirement**: Show only recipes with ingredients family has
- Display pantry ingredient selector (fruit, veggies, dairy, grains, protein, pantry items)
- Show recipe counts filtered by selected ingredients
- Indicate which recipes are "completable" with pantry items
- Allow saving ingredient selections per family member

**Technical Constraint**: Pantry selection persists across sessions

#### 3.2.3 Recipe Details & Cooking
**Requirement**: Display full recipe with multiplier based on family size
- Show ingredients (with calculated amounts based on family_size multiplier)
- Display step-by-step instructions
- Show fun emoji, "why this recipe", and cooking tip
- Allow marking as favorite
- "Next Recipe" button stays in same weather/category

**Technical Constraint**: Multiplier calculation: `ceil(family_size / 2)` for recipe serving=2

#### 3.2.4 Meal Categories
**Requirement**: Filter recipes by meal type
- Support 4 categories: breakfast, lunch, dinner, snack
- Auto-categorize recipes by name patterns
- Show category badge on recipe cards
- Filter by category on recipe list

**Technical Constraint**: Categorization must be deterministic (same recipe name always same category)

#### 3.2.5 Favorites System
**Requirement**: Users can save favorite recipes
- Heart icon toggles favorite status
- Favorites persist across sessions
- "My Favorites" screen shows all favorited recipes
- Favorites count shows in navigation
- User-specific (other family members don't see your favorites)

**Technical Constraint**: Per-user favorites, not per-family

#### 3.2.6 Multi-User Support
**Requirement**: Multiple children can use app from one family
- User selection screen (pick your emoji name)
- Family size setting affects all recipes for that family
- Each user has own favorites and ingredient preferences
- Can switch users without reloading app

**Technical Constraint**: No password/authentication (children's app), but user selection UI

#### 3.2.7 Family Configuration
**Requirement**: Family-level settings
- Family size (1-20 people) - affects multiplier calculations
- Family name (optional)
- Can reset entire family data

**Technical Constraint**: One family per installation (localhost assumption for v1)

### 3.3 Data Model

#### 3.3.1 Core Tables

```
recipes
├── id (PK)
├── name, emoji, why, tip, serves, weather
├── category (breakfast|lunch|dinner|snack)
└── version_added (for future schema tracking)

recipe_ingredients
├── recipe_id (FK → recipes)
├── sort_order
└── ingredient_text (e.g., "2 eggs")

recipe_steps
├── recipe_id (FK → recipes)
├── step_number
└── step_text

recipe_tags
├── recipe_id (FK → recipes)
└── tag (e.g., "egg", "quick")

users
├── id (PK)
├── family_id (FK → families)
├── name, emoji
├── created_at, updated_at
└── is_active

families
├── id (PK)
├── name, family_size
├── created_at
└── is_active

user_ingredients
├── user_id (FK)
├── tag
└── added_at

user_favorites
├── user_id (FK)
├── recipe_id (FK)
└── favorited_at
```

#### 3.3.2 Constraints
- All foreign keys CASCADE DELETE
- UNIQUE(user_id, recipe_id) on user_favorites
- UNIQUE(user_id, tag) on user_ingredients
- CHECK(family_size BETWEEN 1 AND 20)
- CHECK(weather IN (...10 types...))
- CHECK(category IN (breakfast, lunch, dinner, snack))

---

## 4. TECHNICAL ARCHITECTURE (Production Constraints)

### 4.1 Design Principles

1. **Zero-Dependency Core**: Continue using Python stdlib for portability
   - http.server → Replace with production WSGI (Gunicorn/uWSGI wrapper)
   - sqlite3 → Keep for v1, plan migration path to PostgreSQL

2. **Security-First Architecture**
   - Input validation on all endpoints (strict types, length limits, allowed values)
   - SQL parameterized queries (already done, maintain)
   - XSS protection (textContent, CSP headers, no innerHTML)
   - CSRF tokens on all state-changing requests
   - Rate limiting (10 req/sec per IP)
   - Comprehensive logging (info, warning, error levels)
   - Error messages never leak implementation details

3. **Performance-First Design**
   - Batch queries (JOINs not N+1)
   - Gzip compression (90% reduction)
   - HTTP caching (ETag, Cache-Control)
   - Single database query per most API calls
   - Connection pooling (5 connections)
   - Pagination on all list endpoints

4. **Layered Architecture**
   ```
   Presentation Layer (HTML/CSS/JS)
         ↓
   API Layer (HTTP endpoints, validation)
         ↓
   Business Logic Layer (filtering, calculations)
         ↓
   Data Access Layer (repositories, queries)
         ↓
   Database Layer (SQLite/PostgreSQL)
   ```

### 4.2 Backend Stack

**Framework**: Custom Python HTTP server (stdlib) wrapped with Gunicorn
**Database**: SQLite (v1) → PostgreSQL (v2 optional)
**Language**: Python 3.8+
**Type Hints**: Full type annotations
**Concurrency**: ThreadingHTTPServer + connection pooling

**Key Modules**:
- `app.py` - WSGI application entry point
- `handlers.py` - HTTP request handlers
- `services.py` - Business logic (recipe filtering, calculations)
- `repositories.py` - Data access (database queries)
- `models.py` - Data classes and validation
- `security.py` - Input validation, CSRF tokens, sanitization
- `errors.py` - Exception handling, error responses
- `middleware.py` - Logging, rate limiting, CORS, security headers

### 4.3 Frontend Stack

**Framework**: Vanilla JavaScript (no build step)
**Bundling**: Single index.html with separate CSS/JS files served independently
**Storage**: LocalStorage for preferences, IndexedDB for optional offline recipe cache

**Key Files**:
- `index.html` - Structure only (links to CSS/JS)
- `styles.css` - All styling
- `app.js` - Main application logic
- `api.js` - API communication with retry/error handling
- `state.js` - Client-side state management
- `ui.js` - DOM manipulation (textContent-only, no innerHTML)
- `constants.js` - Hardcoded data (weather types, categories)

### 4.4 API Design

**RESTful Principles**:
- Proper HTTP methods (GET for reads, POST for creates, PUT for updates, DELETE for deletes)
- Proper status codes (200, 201, 400, 404, 409, 422, 429, 500)
- Request/response validation (Pydantic or custom)
- No side effects on GET requests

**Core Endpoints**:
```
GET /api/v1/recipes?weather=sunny&tags=egg,cheese&category=breakfast&limit=20&offset=0
GET /api/v1/recipes/{id}
GET /api/v1/stats/recipes-per-weather
GET /api/v1/tags/categories

POST /api/v1/families (create family)
GET /api/v1/families/{family_id}
PUT /api/v1/families/{family_id} (update settings)

POST /api/v1/users (create user)
GET /api/v1/users?family_id=...
GET /api/v1/users/{user_id}/ingredients
POST /api/v1/users/{user_id}/ingredients (replace list)
GET /api/v1/users/{user_id}/favorites
POST /api/v1/users/{user_id}/favorites/{recipe_id} (toggle)
```

**Security Headers**:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000 (for HTTPS)
```

---

## 5. SECURITY REQUIREMENTS (OWASP Top 10)

### 5.1 Authentication & Authorization
- **Requirement**: No passwords for v1 (children's app), but user context validation
- Family→User relationship enforced
- User cannot access other families' data
- Parental admin can override user access

### 5.2 Input Validation
- All user input must be validated server-side
- Type checking (int, string, array)
- Length limits (username max 50, family_size 1-20)
- Allowed value whitelisting (weather, category, tags)
- Reject invalid JSON with 400 error

### 5.3 XSS Prevention
- **No innerHTML** (use textContent for text, DOM APIs for structure)
- Content Security Policy headers
- Output encoding on all dynamic content
- No `eval()` or `Function()` constructor

### 5.4 SQL Injection Prevention
- Parameterized queries (already in place, maintain)
- No dynamic SQL string construction
- Test with SQL injection payloads

### 5.5 CSRF Protection
- CSRF tokens on all POST/PUT/DELETE endpoints
- Token validation before state changes
- SameSite=Strict on cookies (if used)

### 5.6 Cryptography
- HTTPS required for production (TLS 1.2+)
- No sensitive data in URLs
- Password storage: N/A for v1
- Database encryption: at-rest in production

### 5.7 Logging & Monitoring
- All API requests logged (timestamp, IP, endpoint, user_id, status, response_time)
- All errors logged with stack trace (not shown to user)
- Failed authentication attempts logged
- Rate limit violations logged
- No sensitive data in logs (no passwords, tokens, family_size numbers)

### 5.8 COPPA/GDPR Compliance
- Privacy policy in app footer
- Parental consent mechanism for new families
- Data deletion endpoint: DELETE /api/v1/families/{family_id}
- Data export endpoint: GET /api/v1/families/{family_id}/export
- Age verification (children under 13)
- No third-party tracking or analytics

### 5.9 Security Testing Requirements
- Automated OWASP scanning (OWASP ZAP or equivalent)
- XSS payload testing (20+ payloads)
- SQL injection testing (15+ payloads)
- CSRF testing (token validation)
- Rate limiting testing (exceed limits, verify 429 response)
- Authentication bypass testing (attempt direct database access)
- Coverage: All 28 previously identified vulnerabilities must have tests

---

## 6. PERFORMANCE REQUIREMENTS

### 6.1 Response Time SLAs
- API endpoints: **<100ms p95** (measured server-side)
- Full page load: **<1s p95** (with gzip compression)
- Recipe search: **<200ms p95**
- Database queries: **<5ms per query**

### 6.2 Throughput & Scalability
- **Concurrent users**: 100+ (with ThreadingHTTPServer)
- **Requests per second**: 50+ per core
- **Database connections**: Pool of 5 connections
- **Max request body**: 100KB
- **Rate limit**: 10 requests/second per IP

### 6.3 Data Transfer
- JSON responses gzip compressed (target: 90% reduction)
- HTTP caching headers on static assets (1 hour)
- No unnecessary data fields in responses
- Search results pagination (20 per page)
- Recipe listing pagination (20 per page)

### 6.4 Database Optimization
- **Recipe fetch**: Single JOIN query (not N+1)
- **Ingredient filtering**: Batch query with IN clause
- **Search**: LIMIT 20 server-side (not unlimited)
- **Indexes**: Composite indexes on (user_id, recipe_id), (recipe_id, sort_order)
- **Query targets**: <10ms for common queries

### 6.5 Performance Testing Requirements
- Load testing: 100 concurrent users for 10 minutes
- Benchmark suite: Recipe fetch, search, user creation
- Regression testing: Performance tests in CI/CD
- Monitoring dashboard: Query times, response times, error rates

---

## 7. TESTING REQUIREMENTS

### 7.1 Test Coverage Targets
- **Overall**: 80%+ code coverage
- **Critical paths**: 100% coverage
- **API endpoints**: 100% coverage
- **Security validators**: 100% coverage

### 7.2 Test Types

#### 7.2.1 Unit Tests (70% of tests)
- Input validators (types, ranges, formats)
- Business logic (recipe filtering, multiplier calculations)
- Data transformations
- Error handling

**Framework**: pytest
**Target**: 105+ tests, <5 second execution time

#### 7.2.2 Integration Tests (20% of tests)
- API endpoints (all 9 endpoints with all combinations)
- Database transactions
- Error response validation
- CSRF token validation

**Framework**: pytest with TestClient
**Target**: 48+ tests, <30 second execution time

#### 7.2.3 E2E Tests (10% of tests)
- User onboarding flow
- Recipe discovery workflow
- Favorites management
- Multi-user switching
- Edge cases (empty states, network errors)

**Framework**: Playwright
**Target**: 15+ tests, <5 minute execution time
**Browsers**: Chrome, Firefox, Safari

#### 7.2.4 Security Tests
- XSS payload injection (20+ payloads)
- SQL injection (15+ payloads)
- CSRF token validation
- IDOR (inter-user access)
- Rate limiting
- Input validation edge cases

**Framework**: pytest
**Target**: 50+ tests

#### 7.2.5 Performance Tests
- Recipe fetch: <5ms per 100 recipes
- Search: <100ms for 10,000 recipes
- Load test: 100 concurrent users
- Database connection pool: < 100ms wait time

**Framework**: pytest-benchmark, locust
**Target**: Baseline metrics established, no regression

### 7.3 Continuous Integration Requirements
- **On every commit**: Unit tests + integration tests (< 2 minutes)
- **On every PR**: Full test suite + coverage report (< 10 minutes)
- **Code quality**: Ruff linting, Black formatting, Bandit security scan
- **Coverage threshold**: Fail if <80%

---

## 8. DOCUMENTATION REQUIREMENTS

### 8.1 End-User Documentation
- **User Guide** (docs/user-guide.md): Step-by-step usage with screenshots
- **Privacy Policy** (PRIVACY.md): COPPA/GDPR compliant, in app footer
- **FAQ** (docs/faq.md): Common questions and troubleshooting

### 8.2 Developer Documentation
- **README.md**: Project overview, quick start, architecture diagram
- **API Reference** (docs/api.md): All endpoints, request/response examples
- **Architecture Guide** (docs/architecture.md): Design decisions, data flow diagrams
- **Setup Guide** (docs/setup.md): Prerequisites, installation, testing
- **Contributing Guide** (docs/contributing.md): Code style, testing, PR process

### 8.3 Operations Documentation
- **Deployment Guide** (docs/deployment.md): Production deployment steps
- **Runbooks** (docs/runbooks/): Emergency procedures, troubleshooting
- **Monitoring** (docs/monitoring.md): Logging, alerting, metrics
- **Backup/Recovery** (docs/backup.md): Database backup strategy

### 8.4 Code Documentation
- All functions have docstrings (parameters, return, exceptions)
- All classes have docstrings explaining purpose
- Complex algorithms have inline comments
- Database schema documented in code comments

---

## 9. COMPLIANCE & LEGAL

### 9.1 COPPA (Children's Online Privacy Protection Act)
- **Requirement**: Verifiable parental consent before collecting data
- Age gate: "Is the main user under 13?"
- Parent email verification (send verification code)
- Data deletion on parent request
- No targeted advertising
- Privacy policy accessible and understandable

### 9.2 GDPR (General Data Protection Regulation)
- **Requirement**: If serving EU families
- Privacy policy explaining data collection
- User data export capability
- Data deletion ("Right to be Forgotten")
- Data processing agreement with any third parties
- Privacy by design (minimal data collection)

### 9.3 Data Retention
- Deleted families: Purge after 30 days (soft delete → hard delete)
- Audit logs: Retain for 90 days
- Activity logs: Retain for 1 year

---

## 10. DEPLOYMENT & OPERATIONS

### 10.1 Deployment Options

#### 10.1.1 Option A: Localhost (Current)
**Target**: Single family, single computer
**Server**: Python with ThreadingHTTPServer
**Database**: SQLite local file
**Deployment**: Run start.sh

#### 10.1.2 Option B: LAN Server (Recommended for v1)
**Target**: Family LAN, multiple devices
**Server**: Gunicorn on dedicated machine
**Database**: SQLite with WAL mode
**Network**: Bind to 192.168.x.x, not 0.0.0.0
**TLS**: Self-signed cert for HTTPS

#### 10.1.3 Option C: Cloud (Future)
**Target**: Multi-family, public internet
**Server**: Gunicorn on Linux VM / Docker
**Database**: PostgreSQL managed service
**TLS**: Let's Encrypt
**DNS**: Custom domain
**Monitoring**: Logs aggregation, error tracking
**Backup**: Daily automated backups

### 10.2 DevOps Requirements
- **Version control**: Git with branching strategy (main, dev, feature branches)
- **CI/CD**: GitHub Actions running tests on every commit
- **Secrets management**: Environment variables, no hardcoded credentials
- **Containerization**: Dockerfile for easy deployment
- **Monitoring**: Error logging, request metrics, performance tracking
- **Backup**: Daily database backups, versioned schema migrations

### 10.3 Production Readiness Checklist
- [ ] All 28 security vulnerabilities fixed and tested
- [ ] 80% test coverage achieved
- [ ] All documentation complete
- [ ] COPPA compliance verified
- [ ] Load testing passed (100 concurrent users)
- [ ] Security audit completed
- [ ] Performance baselines established
- [ ] Deployment runbook tested
- [ ] Monitoring and alerting configured
- [ ] Disaster recovery plan documented

---

## 11. PROJECT PHASES & TIMELINE

### Phase 1: Foundation & Security (Weeks 1-2, 80 hours)
**Goal**: Secure, layered architecture with zero vulnerabilities
1. Implement new architecture (handlers → services → repos)
2. Fix all 28 security vulnerabilities
3. Add input validation everywhere
4. Add comprehensive logging
5. Create test infrastructure
6. Documentation: README, SECURITY.md, API reference

### Phase 2: Performance & Quality (Weeks 3-4, 60 hours)
**Goal**: Fast, well-tested, maintainable code
1. Optimize all queries (fix N+1)
2. Add gzip compression
3. Implement caching strategy
4. Unit tests (80% coverage)
5. Integration tests (all endpoints)
6. Documentation: Architecture, setup guide

### Phase 3: Features & Polish (Weeks 5-6, 60 hours)
**Goal**: Production-ready app with complete features
1. E2E tests (critical flows)
2. COPPA compliance (parental consent, data deletion)
3. Multi-family support (optional)
4. Deployment automation (Docker, CI/CD)
5. Performance testing & optimization
6. Documentation: User guide, runbooks

### Phase 4: Hardening & Release (Weeks 7-8, 40 hours)
**Goal**: Ready for production deployment
1. Security audit & penetration testing
2. Load testing (100+ concurrent users)
3. Disaster recovery testing
4. Documentation review & completion
5. Monitoring & alerting setup
6. Release candidate testing

**Total Estimated Effort**: 8-12 weeks (240 hours) with small team

---

## 12. SUCCESS CRITERIA

### 12.1 Security
- [ ] Zero OWASP Top 10 vulnerabilities
- [ ] 50+ security tests passing
- [ ] COPPA compliance verified
- [ ] Security audit completed with zero critical findings

### 12.2 Performance
- [ ] API endpoints <100ms p95
- [ ] Page load <1s p95
- [ ] 90%+ compression ratio on JSON
- [ ] Load test: 100 concurrent users, <500ms p95 response

### 12.3 Quality
- [ ] 80%+ test coverage
- [ ] Zero known bugs in critical paths
- [ ] All code reviewed before merge
- [ ] Linting passes (Ruff, Black)

### 12.4 Documentation
- [ ] README with quick start
- [ ] API reference with all endpoints
- [ ] User guide with screenshots
- [ ] Architecture documentation
- [ ] Deployment guide

### 12.5 Production Readiness
- [ ] Passes security audit
- [ ] Passes load testing
- [ ] Monitoring & alerting configured
- [ ] Backup/recovery tested
- [ ] Team trained on runbooks

---

## 13. ASSUMPTIONS & CONSTRAINTS

### 13.1 Assumptions
- Python 3.8+ available
- Development team familiar with Python and JavaScript
- SQLite sufficient for v1 (single family or LAN)
- Localhost/LAN deployment for v1 (no public internet)
- Eleanor (original user) and parents are primary stakeholders

### 13.2 Constraints
- **No external dependencies** (continue zero-dependency philosophy)
- **No build tools** (no npm, no webpack, no venv required for user)
- **Single-file deployment goal** (start.sh should just work)
- **Backward compatible data** (1,020 existing recipes must migrate)
- **Children-friendly** (must remain fun and engaging)

### 13.3 Dependencies to Accept
- **Production deployment**: Gunicorn/uWSGI wrapper (not optional for multi-user)
- **Testing**: pytest, Playwright (dev-only, not shipped)
- **CI/CD**: GitHub Actions (optional but recommended)

---

## 14. RISKS & MITIGATION

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Security vulnerabilities missed | Critical | Mandatory security audit + penetration testing |
| Performance degrades at scale | High | Load testing with 100+ concurrent users |
| COPPA violation leads to legal action | Critical | Legal review of compliance measures |
| Data loss without backups | High | Automated daily backups with restore testing |
| Team unfamiliar with architecture | Medium | Comprehensive documentation + training |

---

## 15. NEXT STEPS FOR AGENT

### 15.1 Create Detailed Implementation Plan
**Agent Task**: Read this PRD and create a phase-by-phase implementation plan with:
1. **File structure** (new files to create, existing files to refactor)
2. **Database migrations** (schema changes, data migrations from existing DB)
3. **API endpoint definitions** (request/response schemas)
4. **Security implementation** (validation rules, CSRF token strategy, logging)
5. **Testing strategy** (test files to create, fixture setup)
6. **Documentation** (outlines for each doc file)
7. **Timeline** (task dependencies, estimated hours per task)

### 15.2 Reference the Comprehensive Review Report
The full analysis (code quality, architecture, security, performance, testing, documentation) is available in the consolidated review. Use it to:
- Identify which existing code can be reused
- Map security vulnerabilities to security requirements
- Validate that proposed architecture addresses all issues
- Ensure test plan covers identified gaps

### 15.3 Deliverable
A detailed `IMPLEMENTATION_PLAN.md` that another agent (or human developer) can execute to build the production-hardened version within the 8-12 week timeline.

---

**PRD Status**: Ready for Agent-Driven Implementation Planning
**Version**: 1.0 (from comprehensive 6-phase code review)
**Created**: February 15, 2026
**Review Notes**: Incorporates findings from Phase 1A (Code Quality), Phase 1B (Architecture), Phase 2A (Security), Phase 2B (Performance), Phase 3A (Testing), Phase 3B (Documentation)
