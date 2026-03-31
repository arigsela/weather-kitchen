# Weather Kitchen — Auth Flow Implementation Plan

**Created**: March 30, 2026
**Status**: Phase 2 Complete — All Tasks Done
**Branch**: `feat/frontend-implementation`

---

## Overview

Add a proper login/signup flow with password-based family authentication. Currently the app goes straight to family creation (`/setup`) with a 4-6 digit PIN. This plan replaces the PIN with a proper password and adds a login page for returning families.

### Goals
- Replace numeric PIN with password (min 8 chars, uppercase + lowercase + digit required)
- Add `POST /api/v1/auth/login` endpoint (family name + password → JWT tokens)
- Add landing page with Login / Sign Up options
- Add login page for returning families
- Keep bcrypt hashing (already used for PIN)

---

## Phase 1: Backend — Password Auth

### Subphase 1A: Config & Password Utilities

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Add password settings to config: `password_min_length=8`, `password_max_attempts=5`, `password_lockout_minutes=15` | `app/config.py` | ✅ |
| 2 | Create `app/auth/password.py` with `hash_password()`, `verify_password()`, `validate_password_strength()` — reuse bcrypt, validate min 8 chars + 1 upper + 1 lower + 1 digit | `app/auth/password.py` | ✅ |
| 3 | Export new functions from `app/auth/__init__.py` | `app/auth/__init__.py` | ✅ |

### Subphase 1B: Model & Migration

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Add `password_hash` column (String 128, nullable) to Family model. Keep `admin_pin_hash` for backward compat | `app/models/family.py` | ✅ |
| 5 | Create Alembic migration to add `password_hash` column | `alembic/versions/` | ✅ |

### Subphase 1C: Schemas

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 6 | Update `FamilyCreate` schema: replace `admin_pin` with `password` field (min 8 chars, validated by `validate_password_strength`) | `app/schemas/family.py` | ✅ |
| 7 | Add `LoginRequest` schema: `name` (str) + `password` (str) | `app/schemas/auth.py` | ✅ |
| 8 | Update `TokenRotateRequest` to use `password` instead of `admin_pin` | `app/schemas/auth.py` | ✅ |

### Subphase 1D: Service & Login Endpoint

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 9 | Update `FamilyService.create_family()` to hash password instead of PIN, store in `password_hash` | `app/services/family_service.py` | ✅ |
| 10 | Add `FamilyService.login()` method: lookup family by name, verify password, check lockout, return JWT tokens | `app/services/family_service.py` | ✅ |
| 11 | Add `POST /api/v1/auth/login` endpoint that calls `FamilyService.login()` | `app/api/v1/auth.py` | ✅ |
| 12 | Update `require_pin` dependency to `require_password` — accept password, verify against `password_hash` | `app/auth/dependencies.py` | ✅ |
| 13 | Update PIN-protected endpoints (purge, token rotate, verify) to use password | `app/api/v1/families.py` | ✅ |

### Subphase 1E: Backend Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 14 | Unit tests: `validate_password_strength()` — valid passwords, too short, missing upper/lower/digit | `tests/unit/` | ✅ |
| 15 | Integration test: login flow — create family with password → login → get tokens → access protected endpoint | `tests/integration/` | ✅ |
| 16 | Integration test: login failures — wrong password, lockout after 5 attempts, nonexistent family returns 401 | `tests/integration/` | ✅ |
| 17 | Update existing tests that use `admin_pin` to use `password` | `tests/` | ✅ |

---

## Phase 2: Frontend — Login/Signup Flow

### Subphase 2A: Types & API

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 18 | Update `FamilyCreateRequest` type: replace `admin_pin` with `password` | `src/types/user.ts` | ✅ |
| 19 | Add `login()` function to `src/api/auth.ts`: `POST /api/v1/auth/login` with `{ name, password }` → `TokenResponse` | `src/api/auth.ts` | ✅ |
| 20 | Update `deleteFamily()` to send `password` instead of `admin_pin` | `src/api/families.ts` | ✅ |

### Subphase 2B: Landing & Login Pages

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 21 | Create `LandingPage.tsx` — Welcome screen with app logo, "Login" button, "Sign Up" button | `src/features/auth/LandingPage.tsx` | ✅ |
| 22 | Create `LoginPage.tsx` — Family name + password form, error messages, link to sign up | `src/features/auth/LoginPage.tsx` | ✅ |
| 23 | Update `FamilySetupPage.tsx` — Replace PIN input with password input (min 8 chars, show/hide toggle, strength hint), add "Already have an account? Log in" link | `src/features/family/FamilySetupPage.tsx` | ✅ |

### Subphase 2C: Routing & Auth Guard

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 24 | Update `App.tsx` routes: `/` → LandingPage (public), `/login` → LoginPage (public), `/signup` → FamilySetupPage (public), `/home` → WeatherSelector (auth required). AuthGuard redirects to `/` instead of `/setup` | `src/App.tsx` | ✅ |
| 25 | Update `useAuth.ts` bootstrap: on page load with refreshToken, try refresh → if success go to `/home`, if fail go to `/` | `src/hooks/useAuth.ts` | ✅ |

### Subphase 2D: Update Existing Pages

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 26 | Update `DataManagementPage.tsx` — Delete confirmation modal uses password instead of PIN | `src/features/privacy/DataManagementPage.tsx` | ✅ |
| 27 | Update `FamilySettingsPage.tsx` — Add "Change Password" section | `src/features/family/FamilySettingsPage.tsx` | ⬜ (deferred — no backend endpoint yet) |
| 28 | Update Header/Footer links if needed for new routes | `src/components/layout/` | ✅ |

---

## Password Validation Rules

```
Minimum 8 characters
At least 1 uppercase letter (A-Z)
At least 1 lowercase letter (a-z)
At least 1 digit (0-9)
Maximum 128 characters
No null bytes
```

These are "somewhat lax" — no special character requirement, no common password blocklist.

---

## API Changes Summary

| Endpoint | Change |
|----------|--------|
| `POST /api/v1/families` | `admin_pin` → `password` in request body |
| `POST /api/v1/auth/login` | **NEW** — `{ name, password }` → JWT tokens |
| `POST /api/v1/auth/refresh` | No change |
| `POST /api/v1/auth/logout` | No change |
| `POST /api/v1/families/{id}/token/rotate` | `admin_pin` → `password` |
| `POST /api/v1/families/{id}/purge` | `admin_pin` → `password` |
| `POST /api/v1/families/{id}/verify-pin` | Replace with `/verify-password` |

---

## Route Changes Summary

| Path | Before | After |
|------|--------|-------|
| `/` | WeatherSelector (auth required) | LandingPage (public) |
| `/login` | — | LoginPage (public) |
| `/signup` | — | FamilySetupPage (public) |
| `/home` | — | WeatherSelector (auth required) |
| `/setup` | FamilySetupPage | Redirect to `/signup` |
| All other routes | Same | Same (auth required) |

---

## File Impact

### Backend (modify)
- `app/config.py` — Add password settings
- `app/auth/__init__.py` — Export password functions
- `app/auth/dependencies.py` — `require_pin` → `require_password`
- `app/models/family.py` — Add `password_hash` column
- `app/schemas/family.py` — `admin_pin` → `password`
- `app/schemas/auth.py` — Add `LoginRequest`, update rotate request
- `app/services/family_service.py` — Update `create_family()`, add `login()`
- `app/api/v1/auth.py` — Add login endpoint
- `app/api/v1/families.py` — Update PIN-protected endpoints

### Backend (create)
- `app/auth/password.py` — Password hash/verify/validate
- `alembic/versions/*_add_password_hash.py` — Migration

### Frontend (modify)
- `src/App.tsx` — New routes, updated auth guard
- `src/types/user.ts` — `admin_pin` → `password`
- `src/api/auth.ts` — Add `login()` function
- `src/api/families.ts` — Update `deleteFamily()` param
- `src/features/family/FamilySetupPage.tsx` — Password field
- `src/features/privacy/DataManagementPage.tsx` — Password confirmation
- `src/features/family/FamilySettingsPage.tsx` — Change password section
- `src/hooks/useAuth.ts` — Update redirect target

### Frontend (create)
- `src/features/auth/LandingPage.tsx` — Welcome page
- `src/features/auth/LoginPage.tsx` — Login form

---

## Phase Summaries

### Phase 1 — Backend (Complete)
All 17 backend tasks completed. 302/302 tests passing, 80.95% coverage. Key deliverables: `app/auth/password.py` (bcrypt hash/verify/validate), `password_hash` column on Family model with Alembic migration (using batch mode for SQLite compatibility), `POST /api/v1/auth/login` endpoint, `verify-pin` endpoint replaced with `verify-password`, all tests migrated from `admin_pin`/`"1234"` to `password`/`"TestPass1"`.

### Phase 2 — Frontend (Complete, 1 task deferred)
27/28 frontend tasks completed. Build passes. Key deliverables: `LandingPage.tsx` (public welcome screen), `LoginPage.tsx` (family name + password with show/hide), `FamilySetupPage.tsx` updated with password field + strength hint, full route restructure (`/` = landing, `/login`, `/signup`, `/home`), AuthGuard redirects to `/`, all internal nav links updated to `/home`. Task 27 (Change Password section in settings) deferred pending a backend `PATCH /api/v1/families/{id}/password` endpoint.

---

**Overall Progress**: 27/28 tasks (96%)
**Last Updated**: March 31, 2026
