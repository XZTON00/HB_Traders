# H.B. Trader's — Django Catalog

A Django rebuild of the original single-file HTML catalog. The public site keeps the
exact same brutalist design (fonts, colors, layout, hover effects), now driven by a
database instead of a hard-coded JS array. The Django admin has also been re-skinned
with the same design tokens so managing the catalog feels like part of the same product.

**For VPS production deployment (hbtraders.com), see [`DEPLOY.md`](DEPLOY.md).**
This README covers local development.

## What's included

- **`catalog` app** — `Product`, `ProductSpec` (specs table per product), and a
  singleton `BusinessDetail` model (company name, address, phone, email, etc.).
- **Public pages** (`catalog/templates/catalog/`):
  - `/` — the catalog grid.
  - `/item/<number>/` — product detail page with Prev/Next, Call Now (`tel:`), and
    WhatsApp (`wa.me`) links.
  - Real Django URLs instead of `#hash` routing — linkable, shareable, works without JS.
- **Customer login** — `/login/`, `/register/`, logout, styled to match the site.
  An account bar at the top of every page shows Login/Sign Up or Hi, `<name>`.
- **Admin** (`catalog/admin.py` + `static/admin/css/hbt_admin.css` +
  `templates/admin/base_site.html`) — manage products (inline specs, image upload,
  price, stock/active toggles) and the one Business Detail record, styled with the
  site's yellow/blue/red/lime palette.
- **`seed_catalog` management command** — recreates the original 20 placeholder
  "Item 1..20" products and the original business details.
- **Production-ready `settings.py`** — a single settings file that works unmodified
  for both local dev (SQLite, `DEBUG=True`, zero config) and production
  (PostgreSQL, locked-down security headers, WhiteNoise static files), switched
  entirely by environment variables — see `.env.example`.
- **`deploy/`** — Gunicorn config, a systemd service unit (auto-restart), and an
  Nginx site config with SSL, ready to drop onto a VPS. Full walkthrough in
  `DEPLOY.md`.

## Local development setup

```bash
python -m venv venv
source venv/bin/activate        # venv\Scripts\activate on Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_catalog   # loads the 20 placeholder products + business info
python manage.py createsuperuser

python manage.py runserver
```

Visit:
- `http://127.0.0.1:8000/` — the catalog
- `http://127.0.0.1:8000/login/` and `/register/` — customer login / sign-up
- `http://127.0.0.1:8000/admin/` — the admin panel

No `.env` file is needed for local dev — `settings.py` defaults to SQLite and
`DEBUG=True` automatically when there's no `.env` present.

## Editing content

Everything editable is under `/admin/`:

- **Products** → add/edit items, upload a real product photo, edit specs inline,
  toggle **In stock** / **Active**.
- **Business Details** → the hero tagline/subtitle/description, and the
  address/phone/email used across the hero, footer, Call Now button, and WhatsApp link.

## Going to production

See **[`DEPLOY.md`](DEPLOY.md)** for the full step-by-step VPS guide covering:
DNS, PostgreSQL, `.env` production config, migrations, admin account, catalog seed,
Gunicorn, systemd (automatic restart), Nginx, and SSL via Let's Encrypt — targeting
`https://hbtraders.com`.
