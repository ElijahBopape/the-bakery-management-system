"""
Run once to populate the database with sample data.
Usage: python seed.py
"""
from database import SessionLocal, engine, Base
from models import User, Category, Product, Order, OrderItem
from routers.auth import hash_password

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# ── Categories (10) ───────────────────────────────────────────────────────────
categories_data = [
    {"name": "Breads",       "description": "Freshly baked loaves and artisan breads"},
    {"name": "Cakes",        "description": "Celebration and everyday cakes"},
    {"name": "Pastries",     "description": "Croissants, danishes, and flaky pastries"},
    {"name": "Muffins",      "description": "Sweet and savoury muffins baked daily"},
    {"name": "Cookies",      "description": "Crispy and chewy cookies in every flavour"},
    {"name": "Pies",         "description": "Savoury and sweet pies"},
    {"name": "Rolls",        "description": "Dinner rolls, hot cross buns, and more"},
    {"name": "Beverages",    "description": "Coffee, tea, and cold drinks"},
    {"name": "Specials",     "description": "Limited daily specials from the chef"},
    {"name": "Gluten-Free",  "description": "Certified gluten-free options"},
]

cats = []
for c in categories_data:
    obj = Category(**c)
    db.add(obj)
    cats.append(obj)
db.flush()

cat_map = {c.name: c.id for c in cats}

# ── Products (15) ─────────────────────────────────────────────────────────────
products_data = [
    {"name": "White Loaf",           "description": "Soft white bread, 700g",                  "price": 18.00, "category": "Breads"},
    {"name": "Whole Wheat Loaf",     "description": "Nutty whole wheat, 700g",                  "price": 22.00, "category": "Breads"},
    {"name": "Sourdough Loaf",       "description": "Tangy artisan sourdough",                  "price": 45.00, "category": "Breads"},
    {"name": "Chocolate Cake",       "description": "Rich 3-layer chocolate fudge cake",        "price": 180.00,"category": "Cakes"},
    {"name": "Carrot Cake",          "description": "Moist carrot cake with cream cheese icing","price": 160.00,"category": "Cakes"},
    {"name": "Red Velvet Cake",      "description": "Classic red velvet with white frosting",   "price": 175.00,"category": "Cakes"},
    {"name": "Butter Croissant",     "description": "Flaky French-style butter croissant",      "price": 28.00, "category": "Pastries"},
    {"name": "Almond Danish",        "description": "Danish pastry with almond filling",        "price": 32.00, "category": "Pastries"},
    {"name": "Blueberry Muffin",     "description": "Bursting with fresh blueberries",          "price": 22.00, "category": "Muffins"},
    {"name": "Choc Chip Muffin",     "description": "Double chocolate chip muffin",             "price": 22.00, "category": "Muffins"},
    {"name": "Choc Chip Cookies",    "description": "Chewy cookies, pack of 6",                 "price": 55.00, "category": "Cookies"},
    {"name": "Peanut Butter Cookies","description": "Crispy peanut butter cookies, pack of 6",  "price": 55.00, "category": "Cookies"},
    {"name": "Chicken Pie",          "description": "Creamy chicken and mushroom pie",          "price": 65.00, "category": "Pies"},
    {"name": "Caramel Latte",        "description": "Espresso with caramel and steamed milk",   "price": 38.00, "category": "Beverages"},
    {"name": "GF Banana Bread",      "description": "Gluten-free banana bread slice",           "price": 35.00, "category": "Gluten-Free"},
]

for p in products_data:
    db.add(Product(
        name=p["name"],
        description=p["description"],
        price=p["price"],
        category_id=cat_map[p["category"]],
        is_available=True,
    ))
db.flush()

# ── Users (12) ────────────────────────────────────────────────────────────────
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

users = []
for u in users_data:
    obj = User(
        name=u["name"],
        email=u["email"],
        password_hash=hash_password(u["password"]),
        role=u.get("role", "customer"),
        phone=u.get("phone"),
    )
    db.add(obj)
    users.append(obj)
db.flush()

# ── Orders + OrderItems (12 orders) ───────────────────────────────────────────
products = db.query(Product).all()
prod_map = {p.name: p for p in products}

orders_data = [
    {"user_idx": 2, "items": [("White Loaf", 2), ("Blueberry Muffin", 3)],          "status": "delivered", "address": "12 Main St, Polokwane"},
    {"user_idx": 3, "items": [("Chocolate Cake", 1), ("Caramel Latte", 2)],          "status": "delivered", "address": "45 Church St, Polokwane"},
    {"user_idx": 4, "items": [("Butter Croissant", 4), ("Choc Chip Muffin", 2)],     "status": "delivered", "address": "7 Park Ave, Polokwane"},
    {"user_idx": 5, "items": [("Sourdough Loaf", 1), ("Chicken Pie", 2)],            "status": "ready",     "address": "22 Nelson Mandela Dr"},
    {"user_idx": 6, "items": [("Red Velvet Cake", 1), ("Almond Danish", 3)],         "status": "preparing", "address": "89 Rabe St, Polokwane"},
    {"user_idx": 7, "items": [("Choc Chip Cookies", 2), ("Peanut Butter Cookies", 1)],"status": "confirmed", "address": "3 Vorster St"},
    {"user_idx": 8, "items": [("Carrot Cake", 1), ("Caramel Latte", 1)],             "status": "pending",   "address": "15 Bodenstein St"},
    {"user_idx": 9, "items": [("GF Banana Bread", 2), ("Blueberry Muffin", 2)],      "status": "delivered", "address": "101 Grobler St"},
    {"user_idx": 10,"items": [("Whole Wheat Loaf", 2), ("Butter Croissant", 2)],     "status": "delivered", "address": "56 Hans van Rensburg St"},
    {"user_idx": 11,"items": [("Chocolate Cake", 1), ("Red Velvet Cake", 1)],        "status": "confirmed", "address": "77 Thabo Mbeki St"},
    {"user_idx": 2, "items": [("White Loaf", 3), ("Chicken Pie", 1)],                "status": "pending",   "address": "12 Main St, Polokwane"},
    {"user_idx": 3, "items": [("Sourdough Loaf", 1), ("Almond Danish", 2), ("Caramel Latte", 1)], "status": "preparing", "address": "45 Church St"},
]

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
