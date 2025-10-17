![Status](https://img.shields.io/badge/Status-In_Progress-F57C00?style=flat-square&logo=todoist&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2196F3?style=flat-square&logo=open-source-initiative&logoColor=white)


# AuthPad 🔐

**AuthPad** is built with FastAPI to simplify secure user management in modern web apps.

> 🖇️AuthPad isn’t just a project — it’s my learning playground, and my commitment to building things the right way, even while I’m still learning.

---

## ✅ Features
- User registration with password hashing
- JWT-based login routes
- `/me` endpoint to fetch current user info
- Modular route structure with docstrings
- Pydantic-based input validation
- async db connection via `asyncpg`


## 🧪 Soon...
- Refresh tokens
- User account routes: update profile, change password, delete account
- Admin-only: `/users/{id}`
- Role-based access control (RBAC)
- Rate limiting *
- API docs with real-world examples
- Test coverage and CI setup (w/ pytest & Github Action)


## 🛠️ Tech Stack
- FastAPI
- Uvicorn
- Pydantic
- Python-Jose
- Passlib
- PostgreSQL (via `asyncpg` and dependency injection)


## 📦 Usage
Run locally:
```bash
uvicorn app.main:app --reload