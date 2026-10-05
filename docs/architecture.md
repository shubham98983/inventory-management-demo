# Architecture

The application follows a layered design. Each layer only talks to the one below it.

```
routes  ->  services  ->  repositories  ->  SQLite
              |
            utils / models
```

- **Routes** parse HTTP requests, validate input with `utils/validators.py`, call a service
  and turn the result into JSON. Authentication is applied with the decorators in
  `utils/decorators.py`.
- **Services** hold business rules: stock adjustments, pricing, sale creation, alerts,
  reports and authentication.
- **Repositories** contain every SQL statement and return model objects or plain dicts.
- **Models** are dataclasses built from `sqlite3.Row` objects via `BaseModel.from_row`.

## Database

SQLite with seven tables: `users`, `categories`, `suppliers`, `products`,
`stock_movements`, `sales` and `sale_items`. The schema is in `app/schema.sql` and is
created by `init_db()`. A connection is opened per request and closed when the
application context ends.

## Authentication

Users log in with a username and password. The server returns a JWT containing the user id
and role. Routes protected by `login_required` accept any valid token; `admin_required`
additionally checks the role claim.

## Stock and sales flow

1. A sale request lists products and quantities.
2. `sales_service.create_sale` checks stock, applies bulk or explicit discounts and tax.
3. The sale and its line items are stored.
4. `inventory_service.adjust_stock` reduces each product and writes a stock movement.
5. `alert_service` can then report products that need reordering.
