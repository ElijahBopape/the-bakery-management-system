# The Bakery — REST API

Python + FastAPI backend for The Bakery Management System (XISD6329/w).

## Setup (local)

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # edit SECRET_KEY if needed

python seed.py         # populates the database with the menu and sample accounts (safe to repeat)
uvicorn main:app --reload --port 8000
```

API runs at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

## Sample data (seed.py)

The seed loads the shop's real menu: 13 items in Cakes, Frappes and Drinks & Extras, at the same prices as the website.
It is safe to run again. It runs on every deploy (see `Procfile`), so it updates the menu in place, removes the old
sample categories and products (Breads, Pastries, …) that have no orders, and only adds sample orders when there are none.
Users and orders are never deleted.

## Admin credentials (seeded)

| Email | Password |
|-------|----------|
| admin@thebakery.co.za | Admin@1234 |

## Auth (for mobile app and website)

All protected endpoints require:
```
Authorization: Bearer <token>
```

**Login flow:**
1. `POST /auth/login` → receive `access_token`
2. Store token on device
3. On app start: `GET /auth/sso` with the stored token
   - 200 → user is still logged in, continue
   - 401 → token expired, redirect to login screen

## Environment variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | JWT signing secret (change in production) |
| `ALGORITHM` | Always `HS256` |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Token lifetime (default 7) |
| `DATABASE_URL` | SQLite locally; on Railway the PostgreSQL database sets this automatically |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID used to check Google sign-in tokens (`POST /auth/google`) |

## Deployment (Railway)

Live URL: https://the-bakery-management-system-production.up.railway.app (docs at `/docs`)

The API and its PostgreSQL database both run on Railway. `railway.toml` (and the matching
`Procfile`) tell Railway how to start the server:

```
python seed.py; uvicorn main:app --host 0.0.0.0 --port $PORT
```

so the menu is seeded on every start (safe to run again) and `/health` is used as the health check.

1. In Railway, create a project from this GitHub repository with `backend/` as the root directory.
2. Add a **PostgreSQL** database to the project. Railway sets `DATABASE_URL` for the API
   (`database.py` changes `postgres://` to `postgresql://` for SQLAlchemy).
3. Set `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_DAYS` and `GOOGLE_CLIENT_ID` in the
   service's **Variables** tab.
4. Push to `main`; Railway builds and deploys automatically. Logs are under **Deploy Logs**.

`vercel.json` is kept from the short time the API ran on Vercel (12–16 November 2026); Railway does not use it.
