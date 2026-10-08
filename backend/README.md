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
| `DATABASE_URL` | SQLite locally; Railway sets this automatically for PostgreSQL |

## Deployment (Railway)

1. Push this repo to GitHub
2. Create a new Railway project → "Deploy from GitHub repo"
3. Set root directory to `backend/`
4. Railway auto-detects the `Procfile` and runs the server
5. Copy the Railway URL and share with the team
