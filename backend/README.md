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

python seed.py         # populates the database with sample data
uvicorn main:app --reload --port 8000
```

API runs at: http://localhost:8000  
Interactive docs: http://localhost:8000/docs

## Sample data (seed.py)

The seed loads the shop's real menu: 13 items in Cakes, Frappes and Drinks & Extras, at the same prices as the website.
The original sample products (White Loaf, Croissants, …) are still created but hidden (`is_available = false`),
so category IDs 1–10 and product IDs 1–15 are unchanged for the mobile app. The admin dashboard can show or delete them.

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
