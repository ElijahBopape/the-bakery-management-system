# Release Notes — The Bakery Management System

All updates since the Task 1 prototype, newest first. Features marked **★ Innovative** are
the ones we added beyond the module brief.

| Version | Date | Milestone |
|---|---|---|
| [1.1.0](#v110--12-november-2026--task-3-final-release) | 12 Nov 2026 | Task 3 final release |
| [1.0.0](#v100--5-18-october-2026--task-2-working-system) | 5–18 Oct 2026 | Task 2 working system |
| [0.1.0](#v010--1-4-september-2026--task-1-prototype) | 1–4 Sep 2026 | Task 1 prototype |

---

## v1.1.0 — 12 November 2026 — Task 3 final release

### Fixed
- **Login and sign-up work again on the website and app.** The Railway free trial expired,
  so Railway removed our API and database and every request returned a 404
  ("Application not found"). The API now runs on **Vercel** with a free **Neon PostgreSQL**
  database: https://the-bakery-api.vercel.app ([PR #4](https://github.com/ElijahBopape/the-bakery-management-system/pull/4)).
  *Everyone must register again* — the old Railway data could not be moved.
- Database connections are checked before use (`pool_pre_ping`), so the API does not fail
  after the free database goes idle.

### Added
- **★ Innovative — Backend logging with request IDs.** Every API call is logged with its
  method, path, status and time taken. Each response carries an `X-Request-ID` header, so an
  error seen in the app can be matched to its exact log line in Vercel → Logs.
- **★ Innovative — Privacy-safe audit trail (POPIA).** Sign-ups, logins, failed logins, orders,
  order status changes and menu edits are logged with user ids and masked emails
  (`t***@gmail.com`). Passwords and tokens are never logged.
- Code comments with Harvard references across the backend (FastAPI, SQLAlchemy, Passlib, Python logging).
- Signed release APK: the Android build reads an upload key from a git-ignored
  `keystore.properties`, so the key never reaches GitHub.
- JUnit unit tests for the app's price formatting and API models (Isam).
- `RELEASE_NOTES.md` (this file) and an updated README.

### Changed
- Website (`bake/api.js`) and app (`BakeryApi.kt`) now point at the Vercel API. Only the
  address line changed.
- API version 1.0.0 → 1.1.0.

### Still to be added by the team before submission
- [ ] Website updates from lecturer feedback, with screenshots (Smilo)
- [ ] Google Play Console upload screenshot (Isam)
- [ ] Final demonstration video link (Tlou)

---

## v1.0.0 — 5–18 October 2026 — Task 2 working system

### Backend and database (Elijah)
- REST API in **Python + FastAPI** with 15 endpoints: auth (4), categories (2), products (5), orders (4).
- Five related tables (users, categories, products, orders, order_items), seeded with the
  real menu: 13 products in 3 categories, 12 users, 12 orders and 25 order lines.
- **Passwords hashed with bcrypt**; sign-in returns a JWT that lasts 7 days.
- **★ Innovative — Single sign-on with a saved token.** The website and the app call
  `GET /auth/sso` when they open, so a returning user skips the login screen for 7 days.
- **★ Innovative — Tamper-proof pricing.** Order totals use prices from the database, not
  from the phone or browser, and each order line stores the price paid at the time of ordering.
- **★ Innovative — Safe menu changes.** A product that is on past orders can't be deleted
  (409). Staff hide it instead, so order history never breaks.
- Seed script that is safe to run again (updates the menu in place, never deletes orders).
- API smoke test: 45 automated checks (standard library only).

### Android app (Isam)
- Kotlin + Jetpack Compose app: register, login, SSO auto sign-in, menu with category filter,
  cart, place order, order history, and a Settings screen (profile, order notifications, log out).
- Connected to the live API with Retrofit.

### Website (Smilo)
- Website connected to the same API: live menu, cart, sign in / register, My Orders.
- **★ Innovative — Staff dashboard** (`admin.html`): add, edit, hide and delete menu items and
  move orders through pending → confirmed → preparing → ready → delivered.
- **★ Innovative — WhatsApp ordering and an offline menu.** If the server can't be reached,
  the site still shows its built-in menu and customers can send their order on WhatsApp.
- **★ Innovative — "Meet the Baker & Lessons" page** (`baker.html`) with videos of the baker's
  work and her baking lessons.

### DevOps (Tlou)
- GitHub Actions: **Android CI** (build), **Web CI** and **Backend CI** (lint + the 45-check
  API smoke test on Python 3.11 and 3.12) on every push and pull request to `main`.
- Azure Pipelines and the Azure DevOps Kanban board.

---

## v0.1.0 — 1–4 September 2026 — Task 1 prototype

- Repository and README created.
- Static HTML prototype pages: home, about, products, services, contact, login, register,
  dashboard.
- Website and mobile app wireframes and sitemaps.
