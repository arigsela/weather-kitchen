# Weather Kitchen — Frontend

React frontend for the Weather Kitchen recipe discovery app. Provides weather-based recipe browsing, family/user management, pantry ingredients, favorites, and GDPR data controls.

## Quick Start

```bash
# 1. Install dependencies
npm install

# 2. Configure environment (optional — defaults to Vite proxy)
cp .env.example .env

# 3. Start dev server
npm run dev
```

Frontend: `http://localhost:5173` | Backend API proxied from `http://localhost:8000`

The Vite dev server proxies `/api` and `/health` to the backend automatically. Make sure the backend is running first (`cd ../backend && make dev`).

---

## Tech Stack

| Component    | Technology                     |
| ------------ | ------------------------------ |
| Framework    | React 19 + TypeScript 5.9      |
| Build        | Vite 8                         |
| Server State | TanStack Query v5              |
| Client State | Zustand v5 (persisted)         |
| Styling      | Tailwind CSS v4                |
| HTTP Client  | ky                             |
| Icons        | Lucide React                   |
| Testing      | Vitest + React Testing Library |
| E2E          | Playwright                     |

---

## Commands

```bash
npm run dev           # Start dev server with HMR
npm run build         # Production build (TypeScript check + Vite)
npm run preview       # Preview production build
npm run type-check    # TypeScript type checking only
npm run lint          # ESLint + Prettier check
npm run format        # Auto-format with Prettier
npm run test          # Vitest unit tests
npm run test:watch    # Vitest in watch mode
npm run test:coverage # Vitest with coverage report
```

---

## Project Structure

```
src/
├── api/              # HTTP client (ky), API functions, JWT refresh interceptor
├── components/
│   ├── ui/           # Button, Card, Badge, Spinner, Modal, Pagination, etc.
│   └── layout/       # AppLayout, Header (nav), Footer
├── features/
│   ├── weather/      # Weather selector (home page)
│   ├── recipes/      # Recipe list, detail, category filter, ingredients, steps
│   ├── family/       # Family setup, user selector, settings, avatar
│   ├── pantry/       # Ingredient management (6 categories)
│   ├── favorites/    # Favorites list, heart toggle with optimistic updates
│   └── privacy/      # Privacy policy, GDPR data export/delete
├── hooks/            # useAuth, useCurrentUser, useCurrentFamily, useMultiplier
├── store/            # Zustand store (JWT tokens, current user/family)
├── types/            # TypeScript interfaces (Recipe, User, Family, etc.)
├── constants/        # Weather types, meal categories, ingredient categories
└── styles/           # Tailwind CSS globals and theme tokens
```

---

## Routes

| Path                    | Page                             | Auth Required |
| ----------------------- | -------------------------------- | :-----------: |
| `/setup`                | Family creation + first user     |      No       |
| `/`                     | Weather selector (home)          |      Yes      |
| `/recipes/:weather`     | Recipe list for weather type     |      Yes      |
| `/recipes/:weather/:id` | Recipe detail                    |      Yes      |
| `/pantry`               | Ingredient management            |      Yes      |
| `/favorites`            | Favorite recipes                 |      Yes      |
| `/users`                | User selector ("Who's cooking?") |      Yes      |
| `/settings`             | Family settings                  |      Yes      |
| `/privacy`              | Privacy policy                   |      Yes      |
| `/privacy/data`         | Data export/delete (GDPR)        |      Yes      |

---

## Authentication

The app uses JWT tokens from the backend:

1. **Family setup** creates a family and stores `access_token` + `refresh_token`
2. **Access tokens** (15 min) are sent as `Authorization: Bearer` headers via ky interceptor
3. **Auto-refresh**: tokens are silently refreshed 1 minute before expiry
4. **Page reload**: persisted `refreshToken` in localStorage is exchanged for a new access token
5. **Expired session**: redirects to `/setup` if refresh fails

---

## Docker

```bash
# Build
docker build -t weather-kitchen-web .

# Run (set VITE_API_URL at build time)
docker build --build-arg VITE_API_URL=http://api:8000 -t weather-kitchen-web .
docker run -p 3000:3000 weather-kitchen-web
```

The Dockerfile uses a multi-stage build (Node for building, nginx for serving) with SPA routing configured in `nginx.conf`.
