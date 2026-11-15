"""
Populates the database with The Bakery's real menu and some sample users/orders.

Safe to run again: it runs on every deploy (see Procfile), so it updates the menu
in place instead of inserting duplicates, and it never deletes orders or users.
Usage: python seed.py
"""
from database import SessionLocal, engine, Base
from models import User, Category, Product, Order, OrderItem
from routers.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Menu categories (same as the website) ─────────────────────────────────────
categories_data = [
    {"name": "Frappes",         "description": "Cold blended frappes"},
    {"name": "Cakes",           "description": "Celebration and everyday cakes"},
    {"name": "Drinks & Extras", "description": "Cold drinks and scones"},
]

cat_map = {}
for c in categories_data:
    cat = db.query(Category).filter(Category.name == c["name"]).first()
    if not cat:
        cat = Category(name=c["name"])
        db.add(cat)
    cat.description = c["description"]
    cat_map[c["name"]] = cat
db.flush()

# ── Menu products (same names and prices as the website, index.html) ──────────
menu_data = [
    {"name": "Caramel Frappe",      "price": 45.00, "category": "Frappes"},
    {"name": "Oreo Frappe",         "price": 54.00, "category": "Frappes"},
    {"name": "Chocolate Frappe",    "price": 35.00, "category": "Frappes"},
    {"name": "Vanilla Frappe",      "price": 35.00, "category": "Frappes"},
    {"name": "Vanilla Cake",        "price": 35.00, "category": "Cakes"},
    {"name": "Chocolate Cake",      "price": 45.00, "category": "Cakes"},
    {"name": "Chocolate Oreo Cake", "price": 45.00, "category": "Cakes"},
    {"name": "Carrot Cake",         "price": 35.00, "category": "Cakes"},
    {"name": "Red Velvet Cake",     "price": 45.00, "category": "Cakes"},
    {"name": "Water",               "price": 10.00, "category": "Drinks & Extras"},
    {"name": "Power Rate",          "price": 22.00, "category": "Drinks & Extras"},
    {"name": "Coke",                "price": 15.00, "category": "Drinks & Extras"},
    {"name": "Scones",              "price": 10.00, "category": "Drinks & Extras"},
]
menu_names = {p["name"] for p in menu_data}

prod_map = {}
for p in menu_data:
    prod = db.query(Product).filter(Product.name == p["name"]).first()
    if not prod:
        prod = Product(name=p["name"])
        db.add(prod)
    prod.description = None
    prod.price = p["price"]
    prod.category_id = cat_map[p["category"]].id
    prod.is_available = True
    prod_map[p["name"]] = prod
db.flush()

# Remove leftovers from the old sample menu (Breads, Pastries, ...). Items that
# already appear on orders are hidden instead of deleted, so order history stays intact.
ordered_product_ids = {row.product_id for row in db.query(OrderItem.product_id).all()}
for old in db.query(Product).all():
    if old.name in menu_names:
        continue
    if old.id in ordered_product_ids:
        old.is_available = False
    else:
        db.delete(old)
db.flush()

for old_cat in db.query(Category).all():
    if old_cat.name in cat_map:
        continue
    if db.query(Product).filter(Product.category_id == old_cat.id).first() is None:
        db.delete(old_cat)
db.flush()

# ── Users (sample accounts) ───────────────────────────────────────────────────
users_data = [
    {"name": "Admin User",       "email": "admin@thebakery.co.za",  "password": "Admin@1234",  "role": "admin"},
    {"name": "Elijah Bopape",    "email": "elijah@thebakery.co.za", "password": "Elijah@1234", "role": "admin"},
    {"name": "Thabo Nkosi",      "email": "thabo@gmail.com",        "password": "Pass@1234",   "role": "customer", "phone": "0821234567"},
    {"name": "Zanele Dlamini",   "email": "zanele@gmail.com",       "password": "Pass@1234",   "role": "customer", "phone": "0839876543"},
    {"name": "Sipho Molefe",     "email": "sipho@gmail.com",        "password": "Pass@1234",   "role": "customer"},
    {"name": "Lerato Mokoena",   "email": "lerato@gmail.com",       "password": "Pass@1234",   "role": "customer", "phone": "0711234567"},
    {"name": "Bongani Zulu",     "email": "bongani@gmail.com",      "password": "Pass@1234",   "role": "customer"},
    {"name": "Nomsa Khumalo",    "email": "nomsa@gmail.com",        "password": "Pass@1234",   "role": "customer", "phone": "0729876543"},
    {"name": "Kwena Sithole",    "email": "kwena@gmail.com",        "password": "Pass@1234",   "role": "customer"},
    {"name": "Palesa Tau",       "email": "palesa@gmail.com",       "password": "Pass@1234",   "role": "customer", "phone": "0651234567"},
    {"name": "Andile Ndlovu",    "email": "andile@gmail.com",       "password": "Pass@1234",   "role": "customer"},
    {"name": "Mapula Sefolo",    "email": "mapula@gmail.com",       "password": "Pass@1234",   "role": "customer", "phone": "0601234567"},
]

users_by_email = {}
for u in users_data:
    user = db.query(User).filter(User.email == u["email"]).first()
    if not user:
        user = User(
            name=u["name"],
            email=u["email"],
            password_hash=hash_password(u["password"]),
            role=u.get("role", "customer"),
            phone=u.get("phone"),
        )
        db.add(user)
    users_by_email[u["email"]] = user
db.flush()
users = [users_by_email[u["email"]] for u in users_data]

# ── Sample orders (only when there are none yet, so restarts don't duplicate them) ──
orders_data = [
    {"user_idx": 2, "items": [("Caramel Frappe", 2), ("Scones", 3)],                 "status": "delivered", "address": "12 Main St, Polokwane"},
    {"user_idx": 3, "items": [("Chocolate Cake", 1), ("Oreo Frappe", 2)],            "status": "delivered", "address": "45 Church St, Polokwane"},
    {"user_idx": 4, "items": [("Vanilla Frappe", 2), ("Carrot Cake", 2)],            "status": "delivered", "address": "7 Park Ave, Polokwane"},
    {"user_idx": 5, "items": [("Red Velvet Cake", 1), ("Coke", 2)],                  "status": "ready",     "address": "22 Nelson Mandela Dr"},
    {"user_idx": 6, "items": [("Chocolate Oreo Cake", 2), ("Water", 2)],             "status": "preparing", "address": "89 Rabe St, Polokwane"},
    {"user_idx": 7, "items": [("Chocolate Frappe", 1), ("Vanilla Cake", 2)],         "status": "confirmed", "address": "3 Vorster St"},
    {"user_idx": 8, "items": [("Carrot Cake", 1), ("Caramel Frappe", 1)],            "status": "pending",   "address": "15 Bodenstein St"},
    {"user_idx": 9, "items": [("Scones", 4), ("Power Rate", 2)],                     "status": "delivered", "address": "101 Grobler St"},
    {"user_idx": 10,"items": [("Oreo Frappe", 2), ("Chocolate Cake", 2)],            "status": "delivered", "address": "56 Hans van Rensburg St"},
    {"user_idx": 11,"items": [("Red Velvet Cake", 1), ("Vanilla Cake", 1)],          "status": "confirmed", "address": "77 Thabo Mbeki St"},
    {"user_idx": 2, "items": [("Coke", 3), ("Chocolate Oreo Cake", 1)],              "status": "pending",   "address": "12 Main St, Polokwane"},
    {"user_idx": 3, "items": [("Vanilla Frappe", 1), ("Scones", 2), ("Water", 1)],   "status": "preparing", "address": "45 Church St"},
]

if db.query(Order).count() == 0:
    for o in orders_data:
        user = users[o["user_idx"]]
        total = sum(prod_map[name].price * qty for name, qty in o["items"])
        order = Order(
            user_id=user.id,
            total=round(total, 2),
            status=o["status"],
            delivery_address=o.get("address"),
        )
        db.add(order)
        db.flush()
        for name, qty in o["items"]:
            p = prod_map[name]
            db.add(OrderItem(order_id=order.id, product_id=p.id, quantity=qty, unit_price=p.price))

db.commit()
db.close()
print("Database seeded successfully.")
print("\nAdmin credentials:")
print("  Email:    admin@thebakery.co.za")
print("  Password: Admin@1234")
