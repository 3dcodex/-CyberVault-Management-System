# CyberVault Management System

A full-stack web application built with Python and Django that combines a **secure password manager** with a **vulnerability reporting platform**. Designed as a cybersecurity-focused internal tool demonstrating authentication, encryption at rest, role-based access control, and secure coding practices.

---

## Features

| Module | Functionality |
|---|---|
| Accounts | Register, login, logout, user profile, personal dashboard |
| Vault | Store, view, edit, and delete encrypted credentials (passwords) |
| Vulnerabilities | Submit and track vulnerability reports with severity levels |
| Admin Panel | Staff-only user management — search, activate/deactivate, delete accounts |

---

## Project Structure

```
CyberVault Management System/
│
├── cybervault/               # Project configuration
│   ├── settings.py           # Django settings (secrets loaded from .env)
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py
│   └── asgi.py
│
├── accounts/                 # Authentication & user management app
│   ├── models.py             # Uses Django's built-in User model
│   ├── views.py              # register, login, logout, dashboard, profile, admin views
│   ├── forms.py              # RegisterForm
│   ├── urls.py               # /login/ /register/ /dashboard/ /manage/users/ etc.
│   └── management/commands/  # seed_data, create_admin management commands
│
├── vault/                    # Password manager app
│   ├── models.py             # Credential model (auto-encrypts password on save)
│   ├── encryption.py         # Fernet AES-128 encrypt/decrypt helpers
│   ├── views.py              # CRUD views for credentials
│   ├── forms.py              # CredentialForm
│   └── urls.py               # /vault/ /vault/add/ /vault/<id>/edit/ /vault/<id>/delete/
│
├── vulnerabilities/          # Vulnerability reporting app
│   ├── models.py             # VulnerabilityReport model (severity + status choices)
│   ├── views.py              # CRUD views + filter by severity/status
│   ├── forms.py              # VulnerabilityReportForm
│   └── urls.py               # /vulnerabilities/ /vulnerabilities/add/ etc.
│
├── templates/                # HTML templates
│   ├── base.html             # Shared layout (navbar, messages)
│   ├── accounts/             # login, register, dashboard, profile, admin_users
│   ├── vault/                # credential_list, credential_form, confirm_delete
│   └── vulnerabilities/      # report_list, report_detail, report_form, confirm_delete
│
├── static/                   # CSS, JS, images
├── .env.example              # Template for environment variables (copy to .env)
├── requirements.txt          # Python dependencies
└── manage.py                 # Django management entry point
```

---

## URL Map

```
/                          → redirects to /login/
/login/                    → login page
/register/                 → create new account
/logout/                   → POST logout
/dashboard/                → personal stats (passwords saved, reports open/fixed)
/profile/                  → user profile page

/vault/                    → list your saved credentials
/vault/add/                → add a new credential
/vault/<id>/edit/          → edit a credential
/vault/<id>/delete/        → delete a credential

/vulnerabilities/          → shared vulnerability report board
/vulnerabilities/add/      → submit a new report
/vulnerabilities/<id>/     → report detail view
/vulnerabilities/<id>/edit/    → edit a report (owner or staff only)
/vulnerabilities/<id>/delete/  → delete a report (owner or staff only)

/manage/users/             → staff-only user list with search & filters
/manage/users/<id>/toggle/ → activate / deactivate a user account
/manage/users/<id>/delete/ → permanently delete a user account

/admin/                    → Django built-in admin (superuser only)
```

---

## Security Highlights

- **Encryption at rest** — Passwords are encrypted with Fernet (AES-128-CBC + HMAC-SHA256) before being written to the database. The raw ciphertext is never exposed.
- **Authentication required** — Every non-public view is protected with `@login_required`.
- **Role-based access control** — Staff-only views use a `@staff_required` decorator. Object-level checks prevent users from accessing other users' credentials.
- **CSRF protection** — Django's built-in CSRF middleware is active on all POST forms.
- **Safe redirects** — The `?next=` login redirect is validated with `url_has_allowed_host_and_scheme()` to prevent open-redirect attacks.
- **Session hardening** — `HttpOnly`, `SameSite=Lax`, and a 2-hour session expiry are configured.
- **Security headers** — `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff` are set.
- **Secrets in environment** — `SECRET_KEY` and `CREDENTIAL_ENCRYPTION_KEY` are loaded from `.env` via `python-decouple` and are never committed to version control.

---

## Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/3dcodex/-CyberVault-Management-System.git
cd -CyberVault-Management-System

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
copy .env.example .env
# Edit .env and fill in SECRET_KEY and CREDENTIAL_ENCRYPTION_KEY

# Generate a Django secret key:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Generate a Fernet encryption key:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) Create a superuser
python manage.py create_admin

# 6. (Optional) Load sample data
python manage.py seed_data

# 7. Run the development server
python manage.py runserver
```

Open `http://127.0.0.1:8000/` — it will redirect you to the login page.

---

## Dependencies

| Package | Version | Purpose |
|---|---|---|
| Django | 4.2.29 | Web framework |
| cryptography | 46.0.6 | Fernet encryption for vault passwords |
| python-decouple | 3.8 | Load secrets from `.env` file |

---

## Built With

- **Python 3** — core language
- **Django 4.2** — web framework (ORM, auth, admin, templates, CSRF)
- **Fernet (AES-128-CBC)** — symmetric authenticated encryption
- **SQLite** — development database (swap for PostgreSQL in production)
