# Weather Kitchen - Frontend Implementation Plan (React.js)

**Document Version**: 2.0 — Updated for JWT Auth & General Users
**Created**: February 16, 2026
**Updated**: February 18, 2026
**Stack**: React 19 + TypeScript + Vite + TanStack Query + Tailwind CSS
**Estimated Timeline**: 6 weeks (parallel with backend after Phase 1)
**PRD Reference**: `docs/weather_kitcne_prd.md`

> **v2.0 Changes from v1.0:**
> - App pivoted from children's (COPPA) to **general users** — COPPA/age gate/consent flow removed
> - Authentication changed from SHA256 API tokens to **JWT access + refresh tokens**
> - `User.age` replaced by `User.emoji`
> - Phase 5A rewritten: COPPA UI → GDPR Data Management
> - New: `src/api/auth.ts`, `src/hooks/useAuth.ts`, JWT token refresh interceptor

---

## Overview

A delightful, accessible, and secure React.js frontend for the Weather Kitchen recipe discovery app. Designed for general users with large touch targets, playful UI, and JWT-based authentication. Consumes the FastAPI backend REST API.

### Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | React 19 | Latest stable, component-based, massive ecosystem |
| Language | TypeScript | Type safety, better DX, catches bugs at build time |
| Build Tool | Vite | Fast HMR, zero-config, modern ESM-first |
| Routing | React Router v7 | Standard React routing, nested layouts |
| Server State | TanStack Query v5 | Caching, background refetch, optimistic updates |
| Client State | Zustand | Lightweight, simple API, no boilerplate |
| Styling | Tailwind CSS v4 | Utility-first, responsive, customizable design system |
| HTTP Client | ky (or fetch wrapper) | Lightweight, retry support, TypeScript-native |
| Testing | Vitest + React Testing Library | Fast, Vite-native, standard React testing |
| E2E Testing | Playwright | Cross-browser, reliable, fast |
| Linting | ESLint + Prettier | Standard React/TS linting and formatting |
| Icons | Lucide React | Lightweight, tree-shakeable icon set |

---

## Project Structure

```
frontend/
├── public/
│   ├── favicon.ico
│   └── manifest.json
├── src/
│   ├── main.tsx                        # React DOM entry point
│   ├── App.tsx                         # Root: providers, router
│   ├── api/                            # API client layer
│   │   ├── client.ts                   # Base HTTP client with JWT refresh interceptor
│   │   ├── auth.ts                     # refreshTokens(), logout() — NEW
│   │   ├── recipes.ts                  # Recipe API functions
│   │   ├── families.ts                 # Family API functions
│   │   ├── users.ts                    # User API functions
│   │   └── types.ts                    # API response/request types (JWT TokenResponse)
│   ├── components/                     # Shared components
│   │   ├── ui/                         # Generic UI primitives
│   │   │   ├── Button.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── EmptyState.tsx
│   │   │   ├── ErrorBoundary.tsx
│   │   │   ├── Pagination.tsx
│   │   │   └── Modal.tsx
│   │   └── layout/                     # Layout components
│   │       ├── AppLayout.tsx           # Main app shell (header + content + footer)
│   │       ├── Header.tsx              # Nav bar with user avatar, favorites count
│   │       └── Footer.tsx              # Privacy policy link, family info
│   ├── features/                       # Feature modules (collocated)
│   │   ├── weather/                    # Weather selection
│   │   │   ├── WeatherSelector.tsx     # Grid of weather type buttons
│   │   │   ├── WeatherCard.tsx         # Single weather button with emoji + count
│   │   │   └── useWeatherStats.ts      # TanStack Query hook
│   │   ├── recipes/                    # Recipe browsing
│   │   │   ├── RecipeListPage.tsx      # Page: weather → recipe list
│   │   │   ├── RecipeGrid.tsx          # Grid of recipe cards
│   │   │   ├── RecipeCard.tsx          # Card: emoji, name, serves, time, category
│   │   │   ├── RecipeDetailPage.tsx    # Page: full recipe view
│   │   │   ├── RecipeIngredients.tsx   # Ingredients with multiplier
│   │   │   ├── RecipeSteps.tsx         # Step-by-step instructions
│   │   │   ├── CategoryFilter.tsx      # Breakfast/lunch/dinner/snack tabs
│   │   │   ├── NextRecipeButton.tsx    # Navigate to next recipe in set
│   │   │   ├── useRecipes.ts           # TanStack Query hook for recipe list
│   │   │   └── useRecipeDetail.ts      # TanStack Query hook for single recipe
│   │   ├── pantry/                     # Ingredient/pantry management
│   │   │   ├── PantryPage.tsx          # Page: manage ingredients
│   │   │   ├── IngredientCategory.tsx  # Category group (fruit, dairy, etc.)
│   │   │   ├── IngredientChip.tsx      # Toggleable ingredient chip
│   │   │   ├── PantryRecipeCount.tsx   # "X recipes match your pantry"
│   │   │   ├── useUserIngredients.ts   # TanStack Query hook
│   │   │   └── useSaveIngredients.ts   # Mutation hook
│   │   ├── favorites/                  # Favorites system
│   │   │   ├── FavoritesPage.tsx       # Page: list all favorites
│   │   │   ├── FavoriteButton.tsx      # Heart toggle (used in cards + detail)
│   │   │   ├── useFavorites.ts         # TanStack Query hook
│   │   │   └── useToggleFavorite.ts    # Mutation hook with optimistic update
│   │   ├── family/                     # Family & user management
│   │   │   ├── FamilySetupPage.tsx     # Page: first-time family creation
│   │   │   ├── UserSelectorPage.tsx    # Page: "Who's cooking today?"
│   │   │   ├── UserAvatar.tsx          # Emoji avatar for user
│   │   │   ├── AddUserForm.tsx         # Form to add new family member
│   │   │   ├── FamilySettingsPage.tsx  # Page: family size, name, reset
│   │   │   ├── useFamily.ts            # TanStack Query hook
│   │   │   ├── useUsers.ts            # TanStack Query hook
│   │   │   └── useCreateUser.ts        # Mutation hook
│   │   └── privacy/                    # GDPR compliance (no COPPA)
│   │       ├── PrivacyPolicyPage.tsx   # Privacy policy display
│   │       └── DataManagementPage.tsx  # Export/delete family data (GDPR)
│   ├── hooks/                          # Shared custom hooks
│   │   ├── useAuth.ts                  # JWT token state, refresh, logout — NEW
│   │   ├── useCurrentUser.ts           # Get/set current active user
│   │   ├── useCurrentFamily.ts         # Get current family context
│   │   └── useMultiplier.ts            # Calculate serving multiplier
│   ├── store/                          # Client-side state (Zustand)
│   │   ├── appStore.ts                 # Current user, family, JWT tokens
│   │   └── types.ts                    # Store types
│   ├── types/                          # Shared TypeScript types
│   │   ├── recipe.ts                   # Recipe, Ingredient, Step, Tag types
│   │   ├── user.ts                     # User, Family types
│   │   └── common.ts                   # Pagination, API response wrappers
│   ├── utils/                          # Utility functions
│   │   ├── multiplier.ts               # ceil(family_size / 2) calculation
│   │   ├── categorize.ts               # Deterministic meal categorization
│   │   └── format.ts                   # Number formatting, pluralization
│   ├── constants/                      # App constants
│   │   ├── weather.ts                  # Weather types, emojis, labels
│   │   ├── categories.ts              # Meal categories
│   │   └── ingredients.ts              # Ingredient categories and tags
│   └── styles/                         # Global styles
│       └── globals.css                 # Tailwind imports, CSS custom properties
├── tests/
│   ├── setup.ts                        # Vitest setup (MSW, testing-library)
│   ├── mocks/                          # MSW mock handlers
│   │   ├── handlers.ts                 # API mock handlers
│   │   └── server.ts                   # MSW server setup
│   ├── unit/                           # Component unit tests
│   │   ├── RecipeCard.test.tsx
│   │   ├── WeatherSelector.test.tsx
│   │   ├── FavoriteButton.test.tsx
│   │   ├── IngredientChip.test.tsx
│   │   └── multiplier.test.ts
│   ├── integration/                    # Feature integration tests
│   │   ├── RecipeDiscovery.test.tsx
│   │   ├── FavoritesFlow.test.tsx
│   │   └── FamilySetup.test.tsx
│   └── e2e/                            # Playwright E2E tests
│       ├── onboarding.spec.ts
│       ├── recipe-discovery.spec.ts
│       ├── favorites.spec.ts
│       ├── user-switching.spec.ts
│       └── privacy.spec.ts
├── index.html                          # Vite entry HTML
├── package.json                        # Dependencies, scripts
├── vite.config.ts                      # Vite configuration
├── tsconfig.json                       # TypeScript config
├── tailwind.config.ts                  # Tailwind theme customization
├── postcss.config.js                   # PostCSS (required by Tailwind)
├── eslint.config.js                    # ESLint flat config
├── prettier.config.js                  # Prettier config
├── playwright.config.ts               # Playwright E2E config
├── vitest.config.ts                    # Vitest config
├── Dockerfile                          # Production build (nginx)
├── nginx.conf                          # Nginx config for SPA routing
└── .env.example                        # Environment variables template
```

---

## Phase 1: Project Foundation & Design System

**Goal**: Scaffolded React project with routing, API client, and reusable UI components
**Estimated Time**: 1 week
**Tasks**: 16

### Subphase 1A: Project Scaffolding

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Initialize Vite + React + TypeScript project | `package.json`, `vite.config.ts`, `tsconfig.json` | ⬜ |
| 2 | Install dependencies: react-router, @tanstack/react-query, zustand, tailwindcss, ky, lucide-react | `package.json` | ⬜ |
| 3 | Install dev dependencies: vitest, @testing-library/react, @testing-library/jest-dom, msw, playwright, eslint, prettier | `package.json` | ⬜ |
| 4 | Configure Tailwind CSS with custom theme (child-friendly colors, large font sizes, rounded corners) | `tailwind.config.ts`, `src/styles/globals.css` | ⬜ |
| 5 | Configure ESLint + Prettier | `eslint.config.js`, `prettier.config.js` | ⬜ |
| 6 | Configure Vitest with React Testing Library | `vitest.config.ts`, `tests/setup.ts` | ⬜ |
| 7 | Create `.env.example` with `VITE_API_URL=http://localhost:8000` | `.env.example` | ⬜ |

### Subphase 1B: Core Infrastructure

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 8 | Create API client with base URL, error handling, retry logic, and **JWT refresh interceptor** (on 401: call /auth/refresh → retry, on refresh failure: clear tokens + redirect) | `src/api/client.ts` | ⬜ |
| 9 | Create API type definitions matching backend JWT schemas: `TokenResponse`, `FamilyCreateResponse` (with `access_token`/`refresh_token`), `User` (with `emoji` not `age`) | `src/api/types.ts` | ⬜ |
| 10 | Configure TanStack Query client with defaults (staleTime, gcTime, retry) | `src/App.tsx` | ⬜ |
| 11 | Create Zustand store for app state (currentUserId, currentFamilyId, **accessToken, refreshToken, tokenExpiry**) with `setTokens()`, `clearTokens()` actions | `src/store/appStore.ts` | ⬜ |
| 11b | Create `src/api/auth.ts`: `refreshTokens(refreshToken)` and `logout(refreshToken)` | `src/api/auth.ts` | ⬜ |
| 11c | Create `src/hooks/useAuth.ts`: exposes `{ isAuthenticated, accessToken, logout }`, auto-refreshes token before expiry | `src/hooks/useAuth.ts` | ⬜ |
| 12 | Create React Router config with nested layouts, route guard (redirect to `/setup` if no access token) | `src/App.tsx` | ⬜ |

### Subphase 1C: Layout & UI Primitives

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 13 | Create AppLayout (header, main content area, footer) | `src/components/layout/AppLayout.tsx` | ⬜ |
| 14 | Create Header (logo, navigation: Weather/Pantry/Favorites, user avatar) | `src/components/layout/Header.tsx` | ⬜ |
| 15 | Create Footer (privacy policy link, family name) | `src/components/layout/Footer.tsx` | ⬜ |
| 16 | Create UI primitives: Button (sizes: sm/md/lg, variants: primary/secondary/ghost), Card, Badge, Spinner, EmptyState | `src/components/ui/*.tsx` | ⬜ |
| 17 | Create ErrorBoundary component with child-friendly error message | `src/components/ui/ErrorBoundary.tsx` | ⬜ |
| 18 | Create Pagination component | `src/components/ui/Pagination.tsx` | ⬜ |
| 19 | Create Modal component (for confirmations, settings) | `src/components/ui/Modal.tsx` | ⬜ |

### Phase 1 Acceptance Criteria
- [ ] `npm run dev` starts dev server with HMR
- [ ] App renders with header/footer layout on all routes
- [ ] API client configured and types match backend schemas
- [ ] TanStack Query provider wraps app
- [ ] Router handles `/`, `/recipes`, `/pantry`, `/favorites`, `/settings` routes
- [ ] All UI primitives render correctly with variants
- [ ] ESLint + Prettier pass with zero errors
- [ ] Tailwind produces child-friendly styling (large fonts, rounded corners, bright colors)

---

## Phase 2: Weather Selection & Recipe Discovery

**Goal**: Core recipe browsing experience - weather selection, recipe list, recipe detail
**Estimated Time**: 1.5 weeks
**Tasks**: 14

### Subphase 2A: Constants & Types

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create weather constants (10 types with emoji, label, description, color) | `src/constants/weather.ts` | ⬜ |
| 2 | Create category constants (4 meal types with emoji, label) | `src/constants/categories.ts` | ⬜ |
| 3 | Create TypeScript types for Recipe, Ingredient, Step, Tag, WeatherStats | `src/types/recipe.ts` | ⬜ |

### Subphase 2B: Weather Selection

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Create recipe API functions: fetchRecipes, fetchRecipeById, fetchWeatherStats, fetchTagCategories | `src/api/recipes.ts` | ⬜ |
| 5 | Create `useWeatherStats` hook (TanStack Query, fetches recipe count per weather) | `src/features/weather/useWeatherStats.ts` | ⬜ |
| 6 | Create WeatherCard component (large emoji, weather name, recipe count, clickable) | `src/features/weather/WeatherCard.tsx` | ⬜ |
| 7 | Create WeatherSelector page (grid of 10 WeatherCards, responsive 2-col mobile / 5-col desktop) | `src/features/weather/WeatherSelector.tsx` | ⬜ |

### Subphase 2C: Recipe List

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 8 | Create `useRecipes` hook (TanStack Query, params: weather, tags, category, pagination) | `src/features/recipes/useRecipes.ts` | ⬜ |
| 9 | Create RecipeCard component (emoji, name, serves, cook time estimate, category badge, favorite heart) | `src/features/recipes/RecipeCard.tsx` | ⬜ |
| 10 | Create CategoryFilter component (tabs: All / Breakfast / Lunch / Dinner / Snack) | `src/features/recipes/CategoryFilter.tsx` | ⬜ |
| 11 | Create RecipeGrid component (responsive grid of RecipeCards) | `src/features/recipes/RecipeGrid.tsx` | ⬜ |
| 12 | Create RecipeListPage (weather header, category filter, recipe grid, pagination) | `src/features/recipes/RecipeListPage.tsx` | ⬜ |

### Subphase 2D: Recipe Detail

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 13 | Create `useRecipeDetail` hook (TanStack Query, fetch by ID) | `src/features/recipes/useRecipeDetail.ts` | ⬜ |
| 14 | Create RecipeIngredients component (list with amounts adjusted by multiplier) | `src/features/recipes/RecipeIngredients.tsx` | ⬜ |
| 15 | Create RecipeSteps component (numbered steps, large text) | `src/features/recipes/RecipeSteps.tsx` | ⬜ |
| 16 | Create RecipeDetailPage (emoji hero, name, "why this recipe", ingredients, steps, tip, favorite button, next recipe button) | `src/features/recipes/RecipeDetailPage.tsx` | ⬜ |
| 17 | Create NextRecipeButton (stays within same weather/category) | `src/features/recipes/NextRecipeButton.tsx` | ⬜ |
| 18 | Create `useMultiplier` hook (reads family_size from store, calculates ceil(family_size/2)) | `src/hooks/useMultiplier.ts` | ⬜ |

### Subphase 2E: Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 19 | Create MSW mock handlers for recipe, stats, **auth** (`POST /api/v1/families` → JWT response, `POST /api/v1/auth/refresh`, `POST /api/v1/auth/logout`) and family endpoints | `tests/mocks/handlers.ts` | ⬜ |
| 20 | Unit tests: WeatherCard, RecipeCard, CategoryFilter, RecipeIngredients | `tests/unit/*.test.tsx` | ⬜ |
| 21 | Unit test: multiplier utility (various family sizes) | `tests/unit/multiplier.test.ts` | ⬜ |
| 22 | Integration test: full recipe discovery flow (select weather → see recipes → view detail) | `tests/integration/RecipeDiscovery.test.tsx` | ⬜ |

### Phase 2 Acceptance Criteria
- [ ] Home page shows 10 weather cards with recipe counts
- [ ] Clicking weather card shows filtered recipe list
- [ ] Category tabs filter recipes within selected weather
- [ ] Recipe cards show emoji, name, serves, category badge
- [ ] Recipe detail shows full recipe with multiplied ingredient amounts
- [ ] "Next Recipe" navigates to next recipe in same weather/category
- [ ] Pagination works on recipe list
- [ ] Loading states show spinner, empty states show friendly message
- [ ] All components render without XSS (no dangerouslySetInnerHTML)

---

## Phase 3: Family Setup & User Management

**Goal**: Family onboarding, user creation, user switching
**Estimated Time**: 1 week
**Tasks**: 12

### Subphase 3A: API Functions & Types

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create family API functions: `createFamily` (returns `access_token`+`refresh_token`+`token_type`+`expires_in`, **not** `api_token`), `getFamily`, `updateFamily`, `deleteFamily` | `src/api/families.ts` | ⬜ |
| 2 | Create user API functions: `createUser` (accepts `name`+`emoji`, **not** `age`), `listUsers`, `getUserIngredients`, `saveIngredients`, `getFavorites`, `addFavorite`, `removeFavorite` | `src/api/users.ts` | ⬜ |
| 3 | Create TypeScript types: `Family` (no `consent_given`/`api_token_hash`), `User` (`emoji: string`, no `age`), `TokenResponse`, `FamilyCreateResponse` | `src/types/user.ts` | ⬜ |

### Subphase 3B: Family Setup Flow

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 4 | Create FamilySetupPage (family name, family size slider 1-20, admin PIN, create button) — on success: store `access_token` + `refresh_token` in Zustand | `src/features/family/FamilySetupPage.tsx` | ⬜ |
| 5 | Create first user creation step within setup (name, pick emoji — **not age**) | `src/features/family/FamilySetupPage.tsx` | ⬜ |
| 6 | Create `useFamily` and `useCreateUser` hooks | `src/features/family/useFamily.ts`, `useCreateUser.ts` | ⬜ |
| 7 | Implement redirect to `/setup` if no `accessToken` in store (JWT-aware guard route) | `src/App.tsx` | ⬜ |

### Subphase 3C: User Selection & Switching

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 8 | Create UserSelectorPage ("Who's cooking today?" with emoji avatars) | `src/features/family/UserSelectorPage.tsx` | ⬜ |
| 9 | Create UserAvatar component (emoji display, name, active indicator) | `src/features/family/UserAvatar.tsx` | ⬜ |
| 10 | Create AddUserForm (inline form to add new family member) | `src/features/family/AddUserForm.tsx` | ⬜ |
| 11 | Create `useCurrentUser` hook (reads from Zustand store, updates on switch) | `src/hooks/useCurrentUser.ts` | ⬜ |
| 12 | Create `useCurrentFamily` hook (reads family from store) | `src/hooks/useCurrentFamily.ts` | ⬜ |

### Subphase 3D: Family Settings

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 13 | Create FamilySettingsPage (edit family name, family size, list members, reset button) | `src/features/family/FamilySettingsPage.tsx` | ⬜ |
| 14 | Add user avatar + switch button to Header | `src/components/layout/Header.tsx` | ⬜ |

### Subphase 3E: Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 15 | Unit tests: UserAvatar, AddUserForm, FamilySettingsPage | `tests/unit/*.test.tsx` | ⬜ |
| 16 | Integration test: family setup flow (create family → add user → select user → see weather) | `tests/integration/FamilySetup.test.tsx` | ⬜ |

### Phase 3 Acceptance Criteria
- [ ] First visit redirects to family setup
- [ ] Family creation with name and size works
- [ ] First user created during family setup
- [ ] User selector shows all family members with emoji avatars
- [ ] User switching updates all user-specific data (favorites, ingredients)
- [ ] Can add new users from user selector
- [ ] Family settings page allows editing name and size
- [ ] Header shows current user avatar and name

---

## Phase 4: Pantry & Favorites

**Goal**: Ingredient management and favorites system
**Estimated Time**: 1 week
**Tasks**: 12

### Subphase 4A: Pantry / Ingredient Management

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Create ingredient constants (categories: fruit, veggies, dairy, grains, protein, pantry items; tags per category) | `src/constants/ingredients.ts` | ⬜ |
| 2 | Create `useUserIngredients` hook (TanStack Query, fetch user's saved ingredients) | `src/features/pantry/useUserIngredients.ts` | ⬜ |
| 3 | Create `useSaveIngredients` mutation hook (replaces user's ingredient list) | `src/features/pantry/useSaveIngredients.ts` | ⬜ |
| 4 | Create IngredientChip component (toggleable chip with emoji, active state) | `src/features/pantry/IngredientChip.tsx` | ⬜ |
| 5 | Create IngredientCategory component (collapsible section, chips for each ingredient in category) | `src/features/pantry/IngredientCategory.tsx` | ⬜ |
| 6 | Create PantryRecipeCount component ("You can make X recipes!") | `src/features/pantry/PantryRecipeCount.tsx` | ⬜ |
| 7 | Create PantryPage (all categories, save button, recipe count, link to filtered recipes) | `src/features/pantry/PantryPage.tsx` | ⬜ |

### Subphase 4B: Favorites System

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 8 | Create `useFavorites` hook (TanStack Query, fetch user's favorites) | `src/features/favorites/useFavorites.ts` | ⬜ |
| 9 | Create `useToggleFavorite` mutation hook (optimistic update, invalidates favorites query) | `src/features/favorites/useToggleFavorite.ts` | ⬜ |
| 10 | Create FavoriteButton component (heart icon, animated toggle, used in RecipeCard + RecipeDetail) | `src/features/favorites/FavoriteButton.tsx` | ⬜ |
| 11 | Create FavoritesPage (grid of favorited RecipeCards, empty state: "No favorites yet!") | `src/features/favorites/FavoritesPage.tsx` | ⬜ |
| 12 | Add favorites count badge to Header navigation | `src/components/layout/Header.tsx` | ⬜ |

### Subphase 4C: Integration

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 13 | Integrate FavoriteButton into RecipeCard and RecipeDetailPage | `RecipeCard.tsx`, `RecipeDetailPage.tsx` | ⬜ |
| 14 | Add pantry filter integration to recipe list (filter recipes by selected ingredients) | `RecipeListPage.tsx` | ⬜ |

### Subphase 4D: Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 15 | Unit tests: IngredientChip, FavoriteButton (toggle states, animation) | `tests/unit/*.test.tsx` | ⬜ |
| 16 | Integration test: favorites flow (add favorite → see in list → remove → gone) | `tests/integration/FavoritesFlow.test.tsx` | ⬜ |
| 17 | Integration test: pantry flow (select ingredients → see recipe count → view filtered recipes) | `tests/integration/PantryFlow.test.tsx` | ⬜ |

### Phase 4 Acceptance Criteria
- [ ] Pantry page shows all ingredient categories with toggleable chips
- [ ] Selected ingredients persist (saved to backend per user)
- [ ] Recipe count updates based on selected ingredients
- [ ] Heart button toggles favorite with animation
- [ ] Favorites page shows all user's favorited recipes
- [ ] Favorites count shows in header navigation
- [ ] Favorites are per-user (switching users shows different favorites)
- [ ] Optimistic update: heart toggles immediately, reverts on error

---

## Phase 5: Privacy, Accessibility & Polish

**Goal**: GDPR data controls, accessible, polished experience for all users
**Estimated Time**: 1 week
**Tasks**: 12

> **v2.0 Note**: COPPA compliance UI removed (AgeGate, ConsentPage, consent gate). Replaced with GDPR data management only.

### Subphase 5A: GDPR Data Management

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | ~~Create AgeGate component~~ — **REMOVED** (no COPPA) | ~~`AgeGate.tsx`~~ | ~~N/A~~ |
| 2 | ~~Create ConsentPage~~ — **REMOVED** (no COPPA) | ~~`ConsentPage.tsx`~~ | ~~N/A~~ |
| 3 | Create PrivacyPolicyPage (general privacy policy, GDPR data retention info) | `src/features/privacy/PrivacyPolicyPage.tsx` | ⬜ |
| 4 | Create DataManagementPage: "Export My Data" → `GET /api/v1/families/{id}/export`, "Delete My Data" → `DELETE /api/v1/families/{id}` with PIN + confirmation modal | `src/features/privacy/DataManagementPage.tsx` | ⬜ |
| 5 | ~~Integrate consent check~~ — **REMOVED** (no COPPA consent gate in app) | ~~`src/App.tsx`~~ | ~~N/A~~ |
| 6 | Add privacy policy link to Footer | `src/components/layout/Footer.tsx` | ⬜ |

### Subphase 5B: Accessibility (WCAG 2.1 AA)

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 7 | Audit all components for keyboard navigation (tab order, focus visible, enter/space activation) | All components | ⬜ |
| 8 | Add ARIA labels to all interactive elements (buttons, links, toggles) | All components | ⬜ |
| 9 | Ensure color contrast meets AA standards (4.5:1 for text, 3:1 for large text) | `tailwind.config.ts` | ⬜ |
| 10 | Add skip-to-content link | `src/components/layout/AppLayout.tsx` | ⬜ |
| 11 | Test with screen reader (VoiceOver/NVDA) | Manual test | ⬜ |

### Subphase 5C: UI Polish & Child-Friendly Design

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 12 | Add page transitions (fade in/slide) using CSS transitions | Global styles / layout | ⬜ |
| 13 | Add micro-animations: heart bounce on favorite, weather card hover scale, ingredient chip pop | Various components | ⬜ |
| 14 | Add fun loading states (cooking emoji animation instead of spinner) | `src/components/ui/Spinner.tsx` | ⬜ |
| 15 | Ensure all touch targets are min 44x44px (WCAG 2.5.8) | All interactive components | ⬜ |
| 16 | Responsive design audit: mobile (320px), tablet (768px), desktop (1024px+) | All pages | ⬜ |

### Subphase 5D: Tests

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 17 | E2E test: onboarding flow (**family setup → user emoji selection → weather selection** — no age gate or consent) | `tests/e2e/onboarding.spec.ts` | ⬜ |
| 18 | E2E test: recipe discovery (select weather → filter category → view recipe → next recipe) | `tests/e2e/recipe-discovery.spec.ts` | ⬜ |
| 19 | E2E test: favorites (add favorite → check favorites page → remove) | `tests/e2e/favorites.spec.ts` | ⬜ |
| 20 | E2E test: user switching (select user A → add favorite → switch to user B → verify no favorite) | `tests/e2e/user-switching.spec.ts` | ⬜ |
| 21 | E2E test: auth refresh (access token expires → silent refresh → user unaware; refresh token expired → redirect to setup) | `tests/e2e/auth-refresh.spec.ts` | ⬜ |

### Phase 5 Acceptance Criteria
- [ ] ~~Age gate and consent flow~~ — **REMOVED** (no COPPA)
- [ ] Privacy policy accessible from every page via footer
- [ ] Data export downloads JSON file with all family data (`GET /api/v1/families/{id}/export`)
- [ ] Data deletion shows PIN confirmation modal, then removes all data
- [ ] JWT token refresh happens silently without interrupting user
- [ ] Expired refresh token redirects to `/setup` with clear "session expired" message
- [ ] All interactive elements keyboard accessible
- [ ] Screen reader can navigate full app flow
- [ ] Color contrast meets WCAG AA standards
- [ ] All touch targets >= 44x44px
- [ ] Animations are smooth and polished
- [ ] 5+ E2E tests passing across Chrome/Firefox/Safari

---

## Phase 6: Testing, Performance & Deployment

**Goal**: Comprehensive test coverage, optimized builds, production-ready container
**Estimated Time**: 1 week
**Tasks**: 12

### Subphase 6A: Test Coverage Completion

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 1 | Audit test coverage, identify gaps (target: 80%+) | Coverage report | ⬜ |
| 2 | Add missing unit tests to reach coverage target | `tests/unit/*.test.tsx` | ⬜ |
| 3 | Add error state tests (API errors, network failures, empty data) | Various test files | ⬜ |
| 4 | Configure MSW to simulate error scenarios (500, 404, 429, network timeout) | `tests/mocks/handlers.ts` | ⬜ |

### Subphase 6B: Performance Optimization

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 5 | Add React.lazy() code splitting for route-level pages | `src/App.tsx` | ⬜ |
| 6 | Add Suspense boundaries with loading fallbacks | `src/App.tsx`, layout | ⬜ |
| 7 | Optimize bundle: analyze with `vite-plugin-inspect`, tree-shake unused code | `vite.config.ts` | ⬜ |
| 8 | Add image optimization (if any static images) | Vite config | ⬜ |
| 9 | Verify TanStack Query caching reduces unnecessary API calls | Dev tools inspection | ⬜ |

### Subphase 6C: Docker & Deployment

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 10 | Create multi-stage Dockerfile (build stage → nginx serve stage) | `Dockerfile` | ⬜ |
| 11 | Create nginx.conf for SPA routing (all routes → index.html) | `nginx.conf` | ⬜ |
| 12 | Configure environment variable injection at build time (VITE_API_URL) | `Dockerfile`, `vite.config.ts` | ⬜ |

### Subphase 6D: CI/CD Pipeline

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 13 | Create GitHub Actions workflow: lint → type-check → unit tests → build → E2E tests | `.github/workflows/frontend-ci.yml` | ⬜ |
| 14 | Add coverage threshold enforcement (fail < 80%) | `vitest.config.ts` | ⬜ |
| 15 | Add Lighthouse CI for performance auditing | `.github/workflows/frontend-ci.yml` | ⬜ |

### Subphase 6E: Documentation

| # | Task | File(s) | Status |
|---|------|---------|--------|
| 16 | Create frontend README: setup, dev workflow, component architecture, testing | `frontend/README.md` | ⬜ |
| 17 | Create component documentation (props, usage examples) via JSDoc/TSDoc | All components | ⬜ |

### Phase 6 Acceptance Criteria
- [ ] Test coverage > 80% (Vitest coverage report)
- [ ] Bundle size < 200KB gzipped (Vite build output)
- [ ] Lighthouse performance score > 90
- [ ] All E2E tests pass in CI (Chrome, Firefox, Safari)
- [ ] Docker image builds and serves app correctly
- [ ] nginx handles SPA routing (deep links work)
- [ ] CI pipeline runs in < 5 minutes
- [ ] README provides clear quickstart instructions

---

## Route Map

| Path | Page | Description | Phase |
|------|------|-------------|-------|
| `/` | WeatherSelector | Home: pick a weather type | 2 |
| `/recipes/:weather` | RecipeListPage | Recipes for selected weather | 2 |
| `/recipes/:weather/:id` | RecipeDetailPage | Full recipe view | 2 |
| `/pantry` | PantryPage | Manage pantry ingredients | 4 |
| `/favorites` | FavoritesPage | View favorite recipes | 4 |
| `/settings` | FamilySettingsPage | Family configuration | 3 |
| `/users` | UserSelectorPage | Pick active user | 3 |
| `/setup` | FamilySetupPage | First-time family setup | 3 |
| `/privacy` | PrivacyPolicyPage | Privacy policy (GDPR) | 5 |
| `/privacy/data` | DataManagementPage | Export/delete data (GDPR) | 5 |
| ~~`/consent`~~ | ~~ConsentPage~~ | ~~Parental consent~~ — **REMOVED** | ~~5~~ |

---

## Design System Tokens (Tailwind Theme)

### Colors (Child-Friendly Palette)
```
primary:     #FF6B6B (warm coral - main actions)
secondary:   #4ECDC4 (teal - secondary actions)
accent:      #FFE66D (sunny yellow - highlights)
background:  #F7F7F7 (soft white)
surface:     #FFFFFF (card backgrounds)
text:        #2D3436 (dark gray - readable)
text-muted:  #636E72 (medium gray)
success:     #00B894 (green - confirmations)
warning:     #FDCB6E (amber - caution)
danger:      #E17055 (red-orange - destructive)

weather-sunny:   #FFE66D
weather-rainy:   #74B9FF
weather-snowy:   #DFE6E9
weather-hot:     #FF7675
weather-windy:   #A29BFE
weather-cloudy:  #B2BEC3
weather-rainbow: linear-gradient(...)
weather-drizzly: #81ECEC
weather-stormy:  #636E72
weather-foggy:   #DFE6E9
```

### Typography
```
font-family:  'Nunito', 'Quicksand', sans-serif (rounded, child-friendly)
font-size-xs:  0.875rem (14px)
font-size-sm:  1rem (16px)
font-size-md:  1.125rem (18px - base body text)
font-size-lg:  1.5rem (24px)
font-size-xl:  2rem (32px)
font-size-2xl: 3rem (48px - weather emojis)
```

### Spacing & Sizing
```
touch-target-min: 44px (WCAG 2.5.8)
border-radius:    12px (large, friendly)
card-padding:     1.5rem
grid-gap:         1rem
page-max-width:   1200px
```

---

## State Management Architecture

### Server State (TanStack Query)
All data from the backend is managed by TanStack Query:
- Recipes, weather stats, tag categories
- Family data, user data
- User ingredients, user favorites

### Client State (Zustand)
Only local app state in Zustand:
- `currentFamilyId: string | null`
- `currentUserId: string | null`
- `hasCompletedSetup: boolean`
- `accessToken: string | null` — current JWT access token (15-min TTL)
- `refreshToken: string | null` — JWT refresh token (7-day TTL, stored in sessionStorage)
- `tokenExpiry: number | null` — Unix timestamp when access token expires
- ~~`hasConsent: boolean`~~ — **REMOVED** (no COPPA)

### State Flow
```
User Action → TanStack Query Mutation → Backend API → Cache Invalidation → UI Update
                                                          ↓
                                              Optimistic Update (favorites)
```

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | > 80% | Vitest coverage report |
| E2E Tests | 5+ passing (3 browsers) | Playwright report |
| Bundle Size | < 200KB gzipped | Vite build output |
| Lighthouse Performance | > 90 | Lighthouse CI |
| Lighthouse Accessibility | > 95 | Lighthouse CI |
| First Contentful Paint | < 1s | Lighthouse |
| Time to Interactive | < 2s | Lighthouse |
| ESLint/Prettier | 0 errors | `npm run lint` |
| TypeScript | 0 errors | `npm run type-check` |
| Touch Targets | >= 44x44px | Manual audit |

---

## Dependencies

**Dependency Review Date**: February 16, 2026 | **Status**: All versions verified and up-to-date

### Runtime Dependencies (Latest Stable Versions)

| Package | Version | Released | Node | Notes |
|---------|---------|----------|------|-------|
| react, react-dom | **19.2.4** | Jan 26, 2026 | 14+ | Latest stable, DoS mitigations for Server Actions |
| react-router | **7.13.0** | Jan 23, 2026 | 14+ | Latest, crossOrigin support, security fixes |
| @tanstack/react-query | **5.90.21** | 5 days ago | 14+ | Latest stable, 20% smaller than v4, Suspense support |
| zustand | **5.0.11** | 15 days ago | 14+ | Latest, native useSyncExternalStore, React 18+ required |
| ky | **1.14.3** | 21 days ago | 14+ | Latest, tiny fetch wrapper, 1124+ projects using |
| lucide-react | **0.564.0** | 3 days ago | 14+ | Latest, 9964+ projects using, tree-shakeable |

### Dev Dependencies (Latest Stable Versions)

| Package | Version | Released | Notes |
|---------|---------|----------|-------|
| typescript | **6.0 beta** | Feb 11, 2026 | ES2025 support, last JS-based release before v7 (Go-based) |
| vite, @vitejs/plugin-react | **7.3.1** | 1 month ago | Latest stable, Vite 8 beta available (not production-ready) |
| tailwindcss | **4.1.18** | 2 months ago | Latest, 5x faster builds, 100x faster incremental |
| postcss | **8.x** (latest) | Latest | Latest stable |
| autoprefixer | **10.4.24** | 17 days ago | Latest, vendor prefixing for modern browsers |
| vitest | **4.0.18** | 25 days ago | Latest, Browser Mode stable, Visual Regression support |
| @testing-library/react | **16.3.2** | 1 month ago | Latest, requires React 18+ |
| @testing-library/jest-dom | **Latest 6.x** | Latest | Latest stable |
| @testing-library/user-event | **Latest 14.x** | Latest | Latest stable, user interaction simulation |
| msw (Mock Service Worker) | **2.12.10** | 6 days ago | Latest, Fetch API primitives support |
| playwright, @playwright/test | **1.58.2** | 10 days ago | Latest, cross-browser testing |
| eslint | **Latest 8.x** (9.x beta) | Latest | Latest stable (v9 in beta) |
| prettier | **Latest 3.x** | Latest | Latest stable |
| eslint-plugin-prettier | **5.5.5** | 1 month ago | ESLint + Prettier integration |
| eslint-config-prettier | **10.1.8** | 7 months ago | Resolves ESLint/Prettier conflicts |
| eslint-plugin-react-hooks | **Latest 4.x** | Latest | Latest stable |
| eslint-plugin-jsx-a11y | **Latest 6.x** | Latest | Accessibility linting |

---

### ⚠️ Important Dependency Notes

#### TypeScript 6.0 (Beta) vs 5.9
- TypeScript **6.0 beta** was released Feb 11, 2026
- **Recommendation**: Use **5.x LTS** for now (more stable), upgrade to 6.0 GA when released
- TypeScript 7.0 (Go-based) coming October 2026

#### Vite 8 (Beta)
- Vite 8 beta is available but **NOT production-ready**
- **Recommendation**: Use **Vite 7.3.1** for Phase 1 (production-stable)
- Monitor for Vite 8 GA release later in 2026

#### React & TanStack Query
- ✅ React 19.2.4 is stable, production-ready
- ✅ TanStack Query v5 is stable with 20% smaller bundle than v4
- No action needed

#### Tailwind CSS v4
- ✅ Battle-tested on thousands of production sites
- ✅ v4.1.18 is latest stable (not experimental)
- No compatibility concerns

---

### Updated package.json Template

```json
{
  "name": "weather-kitchen-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview",
    "type-check": "tsc --noEmit",
    "lint": "eslint . && prettier --check .",
    "format": "prettier --write .",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage",
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui"
  },
  "dependencies": {
    "react": "19.2.4",
    "react-dom": "19.2.4",
    "react-router": "7.13.0",
    "@tanstack/react-query": "5.90.21",
    "zustand": "5.0.11",
    "ky": "1.14.3",
    "lucide-react": "0.564.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^7.3.1",
    "@testing-library/jest-dom": "^6.x",
    "@testing-library/react": "16.3.2",
    "@testing-library/user-event": "^14.x",
    "@types/node": "^20.x",
    "@types/react": "^19.x",
    "@types/react-dom": "^19.x",
    "autoprefixer": "10.4.24",
    "eslint": "^8.x",
    "eslint-config-prettier": "10.1.8",
    "eslint-plugin-jsx-a11y": "^6.x",
    "eslint-plugin-prettier": "5.5.5",
    "eslint-plugin-react-hooks": "^4.x",
    "msw": "2.12.10",
    "postcss": "^8.x",
    "prettier": "^3.x",
    "tailwindcss": "4.1.18",
    "typescript": "~5.6.x",
    "vite": "7.3.1",
    "vitest": "4.0.18",
    "playwright": "1.58.2",
    "@playwright/test": "1.58.2"
  }
}
```

---

### TypeScript Configuration Recommendation

Since TypeScript 6.0 is beta and TypeScript 7.0 (Go-based) is coming in October 2026:

**Phase 1 Recommendation**: Pin to **TypeScript 5.6.x** for maximum stability
```json
{
  "devDependencies": {
    "typescript": "~5.6.x"
  }
}
```

**Timeline for Upgrades**:
- ✅ Now (Feb 2026): Use TypeScript 5.6.x
- Q2 2026: Evaluate TypeScript 6.0 GA when released
- Q4 2026: Plan migration to TypeScript 7.0 (Go-based, major performance improvement)

---

### Bundle Size Impact

Using latest versions:
- React 19.2.4: ~42KB gzipped
- TanStack Query 5.90.21: ~16KB gzipped (20% smaller than v4)
- Zustand 5.0.11: ~2.2KB gzipped
- Tailwind CSS 4.1.18: ~15KB gzipped (PurgeCSS removes unused)
- Other libraries: ~50KB gzipped

**Total Expected**: ~120-150KB gzipped (**well under 200KB target**)

---

### Compatibility Matrix

| Component | Node 18 | Node 20 | Node 22 |
|-----------|:-------:|:-------:|:-------:|
| react 19.2.4 | ✅ | ✅ | ✅ |
| vite 7.3.1 | ✅ | ✅ | ✅ |
| typescript 5.6 | ✅ | ✅ | ✅ |
| tailwindcss 4.1.18 | ✅ | ✅ | ✅ |
| vitest 4.0.18 | ✅ | ✅ | ✅ |
| playwright 1.58.2 | ✅ | ✅ | ✅ |
| **Overall** | **✅ OK** | **✅ Recommended** | **✅ Latest** |

**Recommendation**: Use **Node 20 LTS** for optimal balance of stability and performance.

---

**Plan Status**: Ready for Implementation (v2.0 — aligned with JWT backend)
**Last Updated**: February 18, 2026
**Overall Progress**: 0/~85 tasks (0%)

### v2.0 Breaking Changes Summary

| Area | v1.0 | v2.0 |
|------|------|------|
| Auth | Single `api_token` from `createFamily` | JWT `access_token` + `refresh_token` |
| Token refresh | No refresh — token never expired | Auto-refresh via `POST /api/v1/auth/refresh` |
| User field | `age: number` | `emoji: string` |
| COPPA | AgeGate + ConsentPage + consent gate | **Removed** — general users only |
| Privacy | COPPA + GDPR consent flow | GDPR data export/delete only |
| Store | `hasConsent: boolean` | `accessToken`, `refreshToken`, `tokenExpiry` |
| Route guard | Redirect if no `api_token` | Redirect if no `accessToken` (JWT) |
| New files | — | `src/api/auth.ts`, `src/hooks/useAuth.ts` |
