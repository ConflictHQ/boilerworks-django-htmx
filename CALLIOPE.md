# Calliope — Boilerworks Django + HTMX
<!-- Agent shim for https://github.com/calliopeai/calliope-cli -->

Primary conventions doc: [`bootstrap.md`](bootstrap.md)

Read it before writing any code.

---

## Project-specific notes

- Django 5 (Python 3.12+); HTMX 2.0 + Alpine.js 3 + Tailwind (CDN). Views return HTML — full pages plus HTMX partials.
- Django ORM with `Tracking`/`BaseCoreModel` base classes; session auth; group-based permissions via the `P` enum (`core/permissions.py`); Celery + Redis; PostgreSQL 16.
- Never expose integer PKs in URLs or templates — use `slug` or `guid`. Auth check at the top of every view: `@login_required` + `P.PERMISSION.check(request.user)`.
- Soft-delete only: `item.soft_delete(user=request.user)`, never `.delete()`.
- HTMX partials keyed on `request.headers.get("HX-Request")`; CSRF token injected via the `htmx:configRequest` event in `base.html`.
- Ruff (check + format), max line length 140; tests use pytest + real Postgres (assert against DB state, cover allow and deny cases).
