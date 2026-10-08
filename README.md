# The Bakery Digital Management System

## Project Overview

The Bakery Digital Management System is a software solution designed to improve the management of customer orders, products, sales, payments, inventory and business reporting for The Bakery.

The project extends the system proposed in XISD5319 by providing a web-based interface and mobile application connected to a database.

## Project Objectives

* Digitise bakery customer and order management.
* Improve the recording and tracking of sales.
* Improve inventory and stock management.
* Provide low-stock notifications.
* Manage bakery products and suppliers.
* Provide business reports to support decision-making.
* Provide a user-friendly website and mobile application.
* Apply software development and DevOps practices throughout the project lifecycle.

## System Components

### Website

The website provides the public-facing bakery interface and authenticated management functionality.

### Mobile Application

The mobile application provides authorised bakery users with access to key operational functions such as orders, sales, customers, inventory and notifications.

### Database

The database stores and manages system information including customers, products, orders, sales, payments, stock, suppliers and system users.

## Repository Structure
```
the-bakery-management-system/
├── backend/           # REST API (Python + FastAPI)
├── bake/              # Website (HTML/CSS/JS)
├── mobile-app/        # Android app (Kotlin)
├── documentation/
│   ├── sitemap/
│   ├── wireframes/
│   └── project-plan/
├── README.md
└── .gitignore
```

## API (Backend)

Built with **Python + FastAPI**. The live API uses **PostgreSQL on Railway**. Locally it uses a SQLite file by default, or Postgres if you set `DATABASE_URL`. See [`backend/`](./backend/) for setup instructions.

Base URL (live): `https://the-bakery-api-production.up.railway.app`  
Base URL (local): `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs` (or `/docs` on the live URL)

### How the website and app connect

| Part | File | API calls |
|------|------|-----------|
| Server address (website) | `bake/api.js` (`API_BASE`, one line) | — |
| Server address (mobile app) | `mobile-app/app/src/main/java/com/bakery/app/data/BakeryApi.kt` (`BAKERY_BASE_URL`, one line) | — |
| Public menu | `bake/public-menu.js` | `GET /categories`, `GET /products` |
| Cart and ordering | `bake/cart.js` | `POST /orders` (customer signed in) |
| Sign in, register, my orders | `bake/account.html` + `account.js` | `/auth/login`, `/auth/register`, `/auth/sso`, `GET /orders` |
| Staff dashboard | `bake/admin.html` + `admin.js` | `/products` add/edit/hide/delete, `GET /orders`, `PUT /orders/{id}/status` |
| Mobile app (Android) | `mobile-app/` | `/auth/register`, `/auth/login`, `/auth/sso`, `/auth/me`, `/categories`, `/products`, `POST /orders`, `GET /orders` |

The sign-in token is saved in `localStorage` under `token` and checked with `GET /auth/sso` whenever a page opens (SSO), so a valid sign-in skips the login form for 7 days.
If the server can't be reached, the website still shows its built-in menu and customers can send their order on WhatsApp.

### Key Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | — | Register new user |
| POST | `/auth/login` | — | Login, returns JWT token |
| GET | `/auth/sso` | Bearer | Verify token (SSO check on app startup) |
| GET | `/auth/me` | Bearer | Get current user profile |
| GET | `/categories` | — | List all product categories |
| GET | `/products` | — | List all available products |
| GET | `/products/{id}` | — | Get single product |
| POST | `/products` | Admin | Create product |
| PUT | `/products/{id}` | Admin | Update product |
| DELETE | `/products/{id}` | Admin | Delete product |
| POST | `/orders` | Bearer | Place an order |
| GET | `/orders` | Bearer | List orders (own / all for admin) |
| GET | `/orders/{id}` | Bearer | Get order detail |
| PUT | `/orders/{id}/status` | Admin | Update order status |

## Running and testing

Quick start (API on your PC):

```bash
cd backend
python -m venv .venv && .venv\Scripts\activate      # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python seed.py                                      # menu + sample accounts (safe to repeat)
uvicorn main:app --reload --port 8000               # docs at http://localhost:8000/docs
```

Run the website against it by setting `API_BASE` in `bake/api.js` to the localhost line, then serving `bake/` with `python -m http.server 5500`. Run the Android app from Android Studio by opening `mobile-app/`.

Automated API test (standard library only, writes test data, so run it against a local server):

```bash
cd backend
python tests/api_smoke_test.py                      # expects "45 checks, 0 failed"
```

## Documentation

Project documentation includes:

* Project Plan
* Website Sitemap
* Mobile Application Sitemap
* Website Wireframes
* Mobile Application Wireframes
* System Design Documentation

## Team

| Member                      | Role             |
| --------------------------- | ---------------- |
| Tlou Pheme                  | Team Leader      |
| Mahlatse Mphelo             | Business Analyst |
| Matome Elijah Bopape        | Systems Analyst  |
| Motsobane Lethabo Boshomane | Researcher       |
| Isam Eltawil                | Researcher       |

## Development

The project will be developed collaboratively using GitHub for source control. Team members will work on allocated features and regularly commit and push their progress to the repository.

## Project Background

The system is based on the requirements and system design developed for The Bakery during XISD5319 and has been updated to meet the current XISD6329 requirement for both a website and mobile application.
