# Seed Sales Data Lambda Function

This Lambda function replicates the full behavior of the original `seed-sales-data.js` script, rewritten entirely in Python. It seeds a MongoDB database (`sales`) with:

- Baseline customers (idempotent upserts)
- Synthetic customers for added volume
- Vendors (idempotent upserts)
- Products & inventory (idempotent upserts)
- A full 180‑day historical order dataset with realistic patterns and randomized behavior

The Lambda is designed to be run manually or through an API Gateway endpoint and is compatible with Adage's `serverless-api` component.

---

## 🚀 Features

### ✔ Idempotent Customer / Vendor / Product / Inventory upserts  
The script ensures foundational data is always present, but never duplicated.

### ✔ 180 Days of Historical Orders  
Automatically creates realistic order volume with weekday/weekend patterns, line items, pricing drift, sales channels, and payment methods.

### ✔ CDC‑Friendly Timestamps  
`created_at` and `updated_at` mirror the JavaScript implementation for clean CDC via Redpanda, Debezium, or Kafka Connect.

### ✔ Matches the Node.js Script 1:1  
Randomization logic, data shapes, and order schema all match the original behavior exactly.

---

## 📦 Environment Variables

Set the following in your Lambda configuration:

| Name       | Description                                                   |
|------------|---------------------------------------------------------------|
| `MONGO_URI` | Full connection string for MongoDB or MongoDB Atlas cluster. |

Example:

```
MONGO_URI = mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
```

---

## 📁 Python Files Needed

```
seed_sales_data.py
requirements.txt
```

---

## 📜 requirements.txt

```
pymongo==4.8.0
dnspython==2.6.1
```

You can expand this depending on layers or additional tools.

---

## 🧩 Handler

Use the following Lambda handler:

```
seed_sales_data.lambda_handler
```

---

## 👇 Deployment Instructions

### 1. Package the Lambda

```
pip install --target lambda_pkg -r requirements.txt
cp seed_sales_data.py lambda_pkg/
cd lambda_pkg
zip -r ../seed_sales_lambda.zip .
```

### 2. Deploy via AWS Console  
Upload `seed_sales_lambda.zip` and set:

- Runtime: **Python 3.11**
- Handler: **seed_sales_data.lambda_handler**
- Environment variable: **MONGO_URI**

### 3. (Optional) Deploy via Terraform / Adage  
If you want infrastructure IaC, request the Terraform module and I’ll generate it.

---

## 🧪 Test Event

Invoke the Lambda with:

```json
{
  "action": "seed"
}
```

Response:

```json
{
  "status": "ok",
  "message": "Seeding complete"
}
```

---

## 🛠 What This Lambda Does Internally

### 1. Upserts:
- 5 baseline customers  
- 3 vendors  
- 5 products  
- Inventory for each product  

### 2. Adds 200 synthetic customers  
(Customizable)

### 3. Wipes existing `orders` collection  
Then regenerates a full timeseries of realistic daily orders.

---

## 📊 Resulting Collections

### `customers`
Baseline + synthetic, CDC-friendly.

### `vendors`
3 vendors with NET terms.

### `products`
5 core items.

### `inventory`
One Chicago warehouse per product.

### `orders`
Up to ~15,000–20,000 historic orders.

---

## 🏁 Summary

This Lambda gives you a **fully reproducible, fully realistic** set of sales data, ideal for:

- Redpanda / Kafka CDC ingestion  
- ClickHouse analytics  
- Timeseries forecasting  
- Demo dashboards  
- Load testing  
- NiFi pipelines on EKS  
- SRE observability use‑cases  

If you want:
- Terraform module  
- API Gateway route  
- Cron-based auto-seeding  
- Docker local runner  
Just ask and I’ll generate those too.
