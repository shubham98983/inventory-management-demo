# Inventory Management System

A REST API for managing products, stock levels, sales, low-stock alerts and reports.
Built with Flask and SQLite.

## Features

- **Products**: CRUD, search, pagination, categories and suppliers
- **Stock**: adjustments, restocking and a full movement history
- **Sales**: multi-item sales with automatic bulk discounts and tax
- **Alerts**: low-stock and out-of-stock alerts with reorder suggestions
- **Reports**: sales summary, inventory valuation, top sellers, category breakdown, CSV export
- **Auth**: JWT based login with `admin` and `staff` roles

## Getting started

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt

python -m scripts.seed_data     # create the database with sample data
python run.py                   # start the server on port 5000
```

The seed script creates an `admin` user. Log in with `POST /api/auth/login`
and send the returned token as `Authorization: Bearer <token>`.

## Running the tests

```bash
pytest
pytest --cov=app
```

## Project layout

```
app/
  models/         dataclasses mapped from database rows
  repositories/   all SQL lives here
  services/       business rules (stock, pricing, sales, alerts, reports, auth)
  routes/         Flask blueprints, one per resource
  utils/          validators, decorators, formatters, CSV export, backup
scripts/          seed_data.py
tests/            pytest suite
docs/             API reference and architecture notes
```

See `docs/API.md` for the endpoint reference.
