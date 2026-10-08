"""
API smoke test for The Bakery backend. Standard library only (no install needed).

    python tests/api_smoke_test.py                                   # tests http://localhost:8000
    python tests/api_smoke_test.py https://the-bakery-api-production.up.railway.app

WARNING: this test writes data. It creates a new customer account and orders, adds
and deletes a test product, and HIDES "Caramel Frappe" at the end. Run it against a
local server or a test database, not the live API.

Start a local server first:  uvicorn main:app --port 8000   (from the backend folder)
"""
import json, sys, time
import urllib.request, urllib.error

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"
results = []


def call(method, path, body=None, token=None, headers=None):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    h.update(headers or {})
    req = urllib.request.Request(BASE + path, data=data, method=method, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            try:
                return r.status, (json.loads(raw) if raw else None), r.headers
            except ValueError:
                return r.status, raw, r.headers
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw), e.headers
        except Exception:
            return e.code, raw, e.headers


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("PASS " if cond else "FAIL ") + name + (("  -> " + str(detail)) if not cond and detail != "" else ""))


email = "tester%d@example.com" % int(time.time())

# ---- Auth ----
s, b, _ = call("POST", "/auth/register", {"name": "Tester", "email": email, "password": "Pass@1234", "phone": "0821112222"})
check("register new customer -> 201", s == 201, (s, b))
cust_token = b["access_token"] if s == 201 else None
check("register returns user.role=customer", s == 201 and b["user"]["role"] == "customer", b)
s, b, _ = call("POST", "/auth/register", {"name": "Tester", "email": email, "password": "Pass@1234"})
check("register duplicate email -> 400", s == 400, (s, b))
s, b, _ = call("POST", "/auth/register", {"name": "Bad", "email": "not-an-email", "password": "x"})
check("register invalid email -> 422", s == 422, (s, b))
s, b, _ = call("POST", "/auth/login", {"email": email, "password": "Pass@1234"})
check("login correct password -> 200", s == 200 and b.get("access_token"), (s, b))
s, b, _ = call("POST", "/auth/login", {"email": email, "password": "wrong"})
check("login wrong password -> 401", s == 401, (s, b))
s, b, _ = call("POST", "/auth/login", {"email": "nobody@example.com", "password": "x"})
check("login unknown email -> 401", s == 401, (s, b))
s, b, _ = call("GET", "/auth/sso", token=cust_token)
check("sso with valid token -> 200", s == 200 and b["email"] == email, (s, b))
s, b, _ = call("GET", "/auth/sso")
check("sso without token -> 401/403", s in (401, 403), (s, b))
s, b, _ = call("GET", "/auth/sso", token="garbage.token.value")
check("sso with garbage token -> 401", s == 401, (s, b))
s, b, _ = call("GET", "/auth/me", token=cust_token)
check("me -> 200 with profile", s == 200 and b["name"] == "Tester", (s, b))

admin_login = call("POST", "/auth/login", {"email": "admin@thebakery.co.za", "password": "Admin@1234"})
check("admin login -> 200", admin_login[0] == 200, admin_login[1])
admin_token = admin_login[1]["access_token"]

# Earlier runs hide "Caramel Frappe" at the end. Make it available again so this run starts clean.
_, all_products, _ = call("GET", "/products?available_only=false")
for p in all_products if isinstance(all_products, list) else []:
    if p["name"] == "Caramel Frappe" and not p["is_available"]:
        call("PUT", "/products/%d" % p["id"], {"is_available": True}, token=admin_token)

# ---- Menu ----
s, cats, _ = call("GET", "/categories")
names = [c["name"] for c in cats] if s == 200 else []
check("categories are exactly the website's three", sorted(names) == sorted(["Frappes", "Cakes", "Drinks & Extras"]), names)
s, b, _ = call("GET", "/categories/999")
check("category 999 -> 404", s == 404, (s, b))
s, prods, _ = call("GET", "/products")
check("products (default) -> 200 with 13 items", s == 200 and len(prods) == 13, (s, len(prods) if isinstance(prods, list) else prods))
price = {p["name"]: p["price"] for p in prods} if isinstance(prods, list) else {}
expected = {"Caramel Frappe": 45, "Oreo Frappe": 54, "Chocolate Frappe": 35, "Vanilla Frappe": 35,
            "Vanilla Cake": 35, "Chocolate Cake": 45, "Chocolate Oreo Cake": 45, "Carrot Cake": 35,
            "Red Velvet Cake": 45, "Water": 10, "Power Rate": 22, "Coke": 15, "Scones": 10}
mismatch = {k: (price.get(k), v) for k, v in expected.items() if price.get(k) != v}
check("all 13 website prices match", not mismatch, mismatch)
s, b, _ = call("GET", "/products?category_id=1")
check("filter by category_id returns only that category", s == 200 and all(p["category_id"] == 1 for p in b), (s, b if s != 200 else ""))
s, b, _ = call("GET", "/products?available_only=false")
check("available_only=false returns the same 13 (nothing hidden)", s == 200 and len(b) == 13, (s, len(b) if isinstance(b, list) else b))
first_id = prods[0]["id"]
s, b, _ = call("GET", "/products/%d" % first_id)
check("product by id -> 200", s == 200 and b["id"] == first_id, (s, b))
s, b, _ = call("GET", "/products/999999")
check("product 999999 -> 404", s == 404, (s, b))

# ---- Orders (customer) ----
frappe_id = next(p["id"] for p in prods if p["name"] == "Caramel Frappe")
scone_id = next(p["id"] for p in prods if p["name"] == "Scones")
s, b, _ = call("POST", "/orders", {"items": [{"product_id": frappe_id, "quantity": 2}]})
check("create order without token -> 401/403", s in (401, 403), (s, b))
s, b, _ = call("POST", "/orders", {"items": [{"product_id": frappe_id, "quantity": 2}, {"product_id": scone_id, "quantity": 3}],
                                   "delivery_address": "1 Test St", "notes": "no nuts"}, token=cust_token)
check("create order -> 201", s == 201, (s, b))
check("order total = 2x45 + 3x10 = 120", s == 201 and abs(b["total"] - 120.0) < 0.01, (s, b.get("total") if isinstance(b, dict) else b))
check("order status starts pending", s == 201 and b["status"] == "pending", b)
check("order items carry product + unit_price", s == 201 and all("product" in i and "unit_price" in i for i in b["items"]), b)
order_id = b["id"] if s == 201 else None
s, b, _ = call("POST", "/orders", {"items": []}, token=cust_token)
check("create order with no items -> 400", s == 400, (s, b))
s, b, _ = call("POST", "/orders", {"items": [{"product_id": frappe_id, "quantity": 0}]}, token=cust_token)
check("create order quantity 0 -> 400", s == 400, (s, b))
s, b, _ = call("POST", "/orders", {"items": [{"product_id": 999999, "quantity": 1}]}, token=cust_token)
check("create order unknown product -> 404", s == 404, (s, b))
s, b, _ = call("POST", "/orders", {"notes": "missing items field"}, token=cust_token)
check("create order missing items field -> 422", s == 422, (s, b))
s, b, _ = call("GET", "/orders", token=cust_token)
check("customer sees own orders only", s == 200 and all(o["user_id"] == b[0]["user_id"] for o in b) and len(b) == 1, (s, b if s != 200 else len(b)))
s, b, _ = call("GET", "/orders/%s" % order_id, token=cust_token)
check("customer gets own order by id -> 200", s == 200 and b["id"] == order_id, (s, b))
s, b, _ = call("GET", "/orders/1", token=cust_token)
check("customer gets someone else's order -> 403", s == 403, (s, b))
s, b, _ = call("GET", "/orders/999999", token=cust_token)
check("order 999999 -> 404", s == 404, (s, b))
s, b, _ = call("PUT", "/orders/%s/status" % order_id, {"status": "confirmed"}, token=cust_token)
check("customer cannot change order status -> 403", s == 403, (s, b))

# ---- Admin ----
s, b, _ = call("GET", "/orders", token=admin_token)
check("admin sees all orders", s == 200 and len(b) >= 13, (s, len(b) if isinstance(b, list) else b))
s, b, _ = call("PUT", "/orders/%s/status" % order_id, {"status": "confirmed"}, token=admin_token)
check("admin updates order status -> 200", s == 200 and b["status"] == "confirmed", (s, b))
s, b, _ = call("PUT", "/orders/%s/status" % order_id, {"status": "lunch"}, token=admin_token)
check("admin invalid status -> 400", s == 400, (s, b))
s, b, _ = call("POST", "/products", {"name": "Test Muffin", "price": 20, "category_id": 1}, token=cust_token)
check("customer cannot create product -> 403", s == 403, (s, b))
s, b, _ = call("POST", "/products", {"name": "Test Muffin", "price": 20, "category_id": 1}, token=admin_token)
check("admin creates product -> 201", s == 201, (s, b))
new_id = b["id"] if s == 201 else None
s, b, _ = call("PUT", "/products/%s" % new_id, {"price": 25}, token=admin_token)
check("admin updates product price -> 200", s == 200 and b["price"] == 25, (s, b))
s, b, _ = call("DELETE", "/products/%s" % new_id, token=admin_token)
check("admin deletes product -> 204", s == 204, (s, b))

s, b, _ = call("DELETE", "/products/%d" % frappe_id, token=admin_token)
check("admin cannot delete a product that is on orders -> 409", s == 409, (s, b))
s, b, _ = call("GET", "/orders", token=admin_token)
check("admin orders list still loads after that attempt -> 200", s == 200, (s, b if s != 200 else ""))
s, b, _ = call("PUT", "/products/%d" % frappe_id, {"is_available": False}, token=admin_token)
check("admin can hide a product that is on orders -> 200", s == 200 and b["is_available"] is False, (s, b))

# ---- CORS (website + mobile) ----
s, b, h = call("OPTIONS", "/products", headers={"Origin": "https://example.com", "Access-Control-Request-Method": "GET"})
check("CORS preflight allowed", s == 200 and h.get("access-control-allow-origin") in ("*", "https://example.com"), (s, h.get("access-control-allow-origin")))

failed = [r for r in results if not r[1]]
print("\n%d checks, %d failed" % (len(results), len(failed)))
