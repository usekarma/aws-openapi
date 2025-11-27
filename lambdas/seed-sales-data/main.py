import os
import json
import random
import math
from datetime import datetime, timedelta
from pymongo import MongoClient, UpdateOne

# ============================================================
# Constants (mirroring the Node.js script)
# ============================================================
DAYS_BACK = 180
WEEKDAY_BASE_ORDERS = 80
WEEKEND_BASE_ORDERS = 40
EXTRA_SYNTHETIC_CUSTOMERS = 200

DB_NAME = "sales"


# ============================================================
# Helpers
# ============================================================
def rand_choice(arr):
    return random.choice(arr)


def rand_int(min_v, max_v):
    return random.randint(min_v, max_v)


def rand_float(min_v, max_v, decimals=2):
    v = random.random() * (max_v - min_v) + min_v
    return round(v, decimals)


def make_date_in_day(day):
    """Given a datetime at midnight, add random hour/min/sec."""
    return day + timedelta(
        hours=rand_int(0, 23),
        minutes=rand_int(0, 59),
        seconds=rand_int(0, 59),
    )


# ============================================================
# Seed functions
# ============================================================
def ensure_base_customers(db):
    coll = db.customers
    print("[seed] Ensuring baseline customers...")

    base_customers = [
        {
            "customer_id": "C100001",
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "+1-312-555-0101",
            "addresses": [
                {
                    "address_id": "ADDR-1",
                    "type": "shipping",
                    "line1": "123 Main St",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60601",
                    "country": "US",
                    "is_default": True,
                }
            ],
            "status": "active",
            "loyalty_level": "gold",
            "marketing_opt_in": True,
        },
        {
            "customer_id": "C100002",
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "phone": "+1-415-555-0199",
            "addresses": [
                {
                    "address_id": "ADDR-2",
                    "type": "shipping",
                    "line1": "500 W Madison",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60661",
                    "country": "US",
                    "is_default": True,
                }
            ],
            "status": "active",
            "loyalty_level": "silver",
            "marketing_opt_in": False,
        },
        {
            "customer_id": "C100003",
            "first_name": "Alice",
            "last_name": "Nguyen",
            "email": "alice.nguyen@example.com",
            "phone": "+1-617-555-0123",
            "addresses": [
                {
                    "address_id": "ADDR-3",
                    "type": "shipping",
                    "line1": "1 Market St",
                    "city": "San Francisco",
                    "state": "CA",
                    "postal_code": "94105",
                    "country": "US",
                    "is_default": True,
                }
            ],
            "status": "active",
            "loyalty_level": "platinum",
            "marketing_opt_in": True,
        },
        {
            "customer_id": "C100004",
            "first_name": "Robert",
            "last_name": "Garcia",
            "email": "robert.garcia@example.com",
            "phone": "+1-773-555-0456",
            "addresses": [
                {
                    "address_id": "ADDR-4",
                    "type": "shipping",
                    "line1": "750 N Rush St",
                    "city": "Chicago",
                    "state": "IL",
                    "postal_code": "60611",
                    "country": "US",
                    "is_default": True,
                }
            ],
            "status": "active",
            "loyalty_level": "bronze",
            "marketing_opt_in": True,
        },
        {
            "customer_id": "C100005",
            "first_name": "Emily",
            "last_name": "Chen",
            "email": "emily.chen@example.com",
            "phone": "+1-213-555-0789",
            "addresses": [
                {
                    "address_id": "ADDR-5",
                    "type": "shipping",
                    "line1": "200 Spring St",
                    "city": "Los Angeles",
                    "state": "CA",
                    "postal_code": "90013",
                    "country": "US",
                    "is_default": True,
                }
            ],
            "status": "active",
            "loyalty_level": "bronze",
            "marketing_opt_in": False,
        },
    ]

    now = datetime.utcnow()
    ops = []
    for c in base_customers:
        c.setdefault("created_at", now)
        c["updated_at"] = now
        ops.append(
            UpdateOne(
                {"customer_id": c["customer_id"]},
                {"$set": c},
                upsert=True,
            )
        )

    coll.bulk_write(ops)
    print("[seed] Baseline customers upserted.")


def add_synthetic_customers(db, extra_count):
    coll = db.customers
    base_count = coll.count_documents({})
    print(f"[seed] Adding ~{extra_count} synthetic customers (current count: {base_count})...")

    docs = []
    now = datetime.utcnow()

    for i in range(extra_count):
        n = base_count + i + 1
        docs.append(
            {
                "customer_id": f"C{100000 + n}",
                "first_name": f"Cust{n}",
                "last_name": "Demo",
                "email": f"customer{n}@example.com",
                "phone": f"+1-555-000-{str(n).zfill(4)}",
                "addresses": [
                    {
                        "address_id": f"ADDR-{n}",
                        "type": "shipping",
                        "line1": f"{100 + (n % 900)} Demo St",
                        "city": rand_choice(["Chicago", "New York", "Los Angeles", "Dallas"]),
                        "state": rand_choice(["IL", "NY", "CA", "TX"]),
                        "postal_code": "60601",
                        "country": "US",
                        "is_default": True,
                    }
                ],
                "status": "active",
                "loyalty_level": rand_choice(["bronze", "silver", "gold", "platinum"]),
                "marketing_opt_in": rand_int(0, 100) < 60,
                "created_at": now,
                "updated_at": now,
            }
        )

    if docs:
        coll.insert_many(docs)
        print(f"[seed] Inserted {len(docs)} synthetic customers.")


def ensure_vendors(db):
    coll = db.vendors
    print("[seed] Ensuring vendors...")

    vendors = [
        {
            "vendor_id": "V1001",
            "name": "Acme Supplies",
            "contact_email": "sales@acmesupplies.com",
            "status": "active",
            "terms": "NET_30",
        },
        {
            "vendor_id": "V1002",
            "name": "Global Tech Distributors",
            "contact_email": "accounts@globaltech.example",
            "status": "active",
            "terms": "NET_45",
        },
        {
            "vendor_id": "V1003",
            "name": "Midwest Retail Partners",
            "contact_email": "info@midwestretail.example",
            "status": "active",
            "terms": "NET_30",
        },
    ]

    now = datetime.utcnow()
    ops = []
    for v in vendors:
        v.setdefault("created_at", now)
        v["updated_at"] = now
        ops.append(
            UpdateOne(
                {"vendor_id": v["vendor_id"]},
                {"$set": v},
                upsert=True,
            )
        )

    coll.bulk_write(ops)
    print("[seed] Vendors upserted.")


def ensure_products_and_inventory(db):
    products = db.products
    inventory = db.inventory
    print("[seed] Ensuring products + inventory...")

    product_docs = [
        {
            "product_id": "P1001",
            "name": "Wireless Mouse",
            "category": "Electronics",
            "unit_price": 24.99,
            "vendor_id": "V1001",
        },
        {
            "product_id": "P1002",
            "name": "Mechanical Keyboard",
            "category": "Electronics",
            "unit_price": 89.99,
            "vendor_id": "V1001",
        },
        {
            "product_id": "P1003",
            "name": "USB-C Docking Station",
            "category": "Accessories",
            "unit_price": 149.99,
            "vendor_id": "V1002",
        },
        {
            "product_id": "P1004",
            "name": "27\" 4K Monitor",
            "category": "Displays",
            "unit_price": 329.99,
            "vendor_id": "V1002",
        },
        {
            "product_id": "P1005",
            "name": "Noise-Cancelling Headphones",
            "category": "Audio",
            "unit_price": 199.99,
            "vendor_id": "V1003",
        },
    ]

    now = datetime.utcnow()
    ops = []

    for p in product_docs:
        p.setdefault("created_at", now)
        p["updated_at"] = now
        ops.append(
            UpdateOne(
                {"product_id": p["product_id"]},
                {"$set": p},
                upsert=True,
            )
        )

        # Inventory row
        inv_key = {"product_id": p["product_id"], "location_id": "WH-CHI-01"}
        inv_doc = {
            "product_id": p["product_id"],
            "location_id": "WH-CHI-01",
            "on_hand": rand_int(100, 500),
            "on_order": rand_int(0, 100),
            "safety_stock": 50,
            "updated_at": now,
        }
        inventory.update_one(inv_key, {"$set": inv_doc}, upsert=True)

    products.bulk_write(ops)
    print("[seed] Products + inventory upserted.")


def generate_orders(db):
    orders = db.orders
    customers = list(db.customers.find({"status": "active"}))
    vendors = list(db.vendors.find({"status": "active"}))
    products = list(db.products.find({}))

    if not customers or not vendors or not products:
        raise Exception("Need customers, vendors, and products before generating orders.")

    print("[seed] Clearing existing orders...")
    orders.delete_many({})

    now = datetime.utcnow()
    start_date = now - timedelta(days=DAYS_BACK)

    global_order_seq = 1
    total_orders = 0

    for d in range(DAYS_BACK):
        day = start_date + timedelta(days=d)
        day_str = day.strftime("%Y-%m-%d")
        dow = day.weekday()  # 0=Mon

        base = WEEKDAY_BASE_ORDERS if dow < 5 else WEEKEND_BASE_ORDERS
        base += rand_int(-10, 25)
        if base < 20:
            base = 20

        print(f"[seed] Generating ~{base} orders for {day_str}...")

        day_docs = []
        for _ in range(base):
            customer = rand_choice(customers)
            vendor = rand_choice(vendors)
            order_date = make_date_in_day(day)

            # line items
            used = set()
            line_items = []
            order_total = 0
            n_items = rand_int(1, 5)

            for _ in range(n_items):
                for _ in range(5):
                    product = rand_choice(products)
                    if product["product_id"] not in used:
                        break
                used.add(product["product_id"])

                qty = rand_int(1, 5)
                unit_price = product["unit_price"] * (1 + rand_float(-0.05, 0.05, 4))
                extended = qty * unit_price

                order_total += extended

                line_items.append(
                    {
                        "product_id": product["product_id"],
                        "quantity": qty,
                        "unit_price": round(unit_price, 2),
                        "extended_price": round(extended, 2),
                    }
                )

            order_total = round(order_total, 2)
            order_id = f"SO-{str(global_order_seq).zfill(8)}"
            global_order_seq += 1

            addr = (customer.get("addresses") or [{}])[0]

            status_roll = rand_int(1, 100)
            if status_roll > 90:
                status = "CANCELLED"
            elif status_roll > 70:
                status = "SHIPPED"
            elif status_roll > 40:
                status = "PAID"
            else:
                status = "NEW"

            doc = {
                "order_id": order_id,
                "customer_id": customer["customer_id"],
                "vendor_id": vendor["vendor_id"],
                "order_date": order_date,
                "status": status,
                "line_items": line_items,
                "order_total": order_total,
                "currency": "USD",
                "payment_method": rand_choice(["visa", "mastercard", "amex", "paypal"]),
                "sales_channel": rand_choice(["web", "mobile", "phone", "store"]),
                "shipping_address": addr,
                "billing_address": addr,
                "created_at": order_date,
                "updated_at": order_date,
            }

            day_docs.append(doc)

        if day_docs:
            orders.insert_many(day_docs)
            total_orders += len(day_docs)

    # Indexes
    orders.create_index([("order_id", 1)], unique=True)
    orders.create_index([("customer_id", 1), ("order_date", -1)])
    orders.create_index([("line_items.product_id", 1), ("order_date", -1)])

    print(f"[seed] Inserted total orders: {total_orders}")
    print("[seed] Orders generation complete.")


# ============================================================
# Lambda handler
# ============================================================
def handler(event, context):
    print("[seed] Starting seeding process...")

    mongo_uri = os.environ.get("MONGO_URI")
    if not mongo_uri:
        raise Exception("Missing MONGO_URI environment variable.")

    client = MongoClient(mongo_uri)
    db = client[DB_NAME]

    ensure_base_customers(db)
    ensure_vendors(db)
    ensure_products_and_inventory(db)

    if EXTRA_SYNTHETIC_CUSTOMERS > 0:
        add_synthetic_customers(db, EXTRA_SYNTHETIC_CUSTOMERS)

    generate_orders(db)

    print("[seed] Done.")
    return {"status": "ok", "message": "Seeding complete"}
