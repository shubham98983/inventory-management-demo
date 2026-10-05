# API Reference

All endpoints except `/health`, `/api/auth/register` and `/api/auth/login` require a
`Authorization: Bearer <token>` header. Responses are JSON unless stated otherwise.

## Auth

| Method | Path | Description |
|---|---|---|
| POST | `/api/auth/register` | Create an account (`username`, `email`, `password`) |
| POST | `/api/auth/login` | Returns a JWT token and the user |
| GET | `/api/auth/me` | Current user profile |

## Products

| Method | Path | Description |
|---|---|---|
| GET | `/api/products` | Paginated list (`page`, `page_size`, `category_id`) |
| GET | `/api/products/search?q=` | Search by name or SKU |
| GET | `/api/products/<id>` | Single product with stock status and margin |
| POST | `/api/products` | Create a product (`sku`, `name`, `price` required) |
| PUT | `/api/products/<id>` | Update product fields |
| DELETE | `/api/products/<id>` | Delete a product |

## Categories and suppliers

Admin only for create, update and delete.

| Method | Path |
|---|---|
| GET, POST | `/api/categories` |
| PUT, DELETE | `/api/categories/<id>` |
| GET, POST | `/api/suppliers` |
| GET, PUT, DELETE | `/api/suppliers/<id>` |

## Stock

| Method | Path | Description |
|---|---|---|
| POST | `/api/stock/<id>/adjust` | Change stock by `change` with a `reason` |
| POST | `/api/stock/<id>/restock` | Add `quantity` units |
| GET | `/api/stock/<id>/movements` | Movement history, newest first |

## Sales

| Method | Path | Description |
|---|---|---|
| POST | `/api/sales` | Create a sale from `items` (`product_id`, `quantity`, optional `discount_percent`) |
| GET | `/api/sales` | List sales, optional `start` and `end` dates |
| GET | `/api/sales/<id>` | Sale with line items |

Orders of 10, 50 and 100+ units of one product get automatic discounts of 5%, 10% and 15%
unless a `discount_percent` is supplied. Tax is added on top of the discounted subtotal.

## Alerts

| Method | Path | Description |
|---|---|---|
| GET | `/api/alerts/low-stock` | Products at or below their reorder level |
| GET | `/api/alerts/out-of-stock` | Products with no stock |

## Reports

| Method | Path | Description |
|---|---|---|
| GET | `/api/reports/sales` | Revenue, tax and average order value for a date range |
| GET | `/api/reports/inventory-value` | Stock value at cost and retail price |
| GET | `/api/reports/top-products` | Best sellers by units (`limit`) |
| GET | `/api/reports/categories` | Totals per category |
| GET | `/api/reports/export/products` | CSV download |
| GET | `/api/reports/export/sales` | CSV download |
| POST | `/api/reports/backup` | Admin only. Copy the database to the backup directory |
