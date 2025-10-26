![Status](https://img.shields.io/badge/Status-In_Progress-F57C00?style=flat-square&logo=todoist&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2196F3?style=flat-square&logo=open-source-initiative&logoColor=white)


# AuthPad 🔐

**AuthPad** is a FastAPI-powered authentication system designed to be secure, scalable, and developer-friendly — perfect for modern web apps and real-world use cases.

## 👨‍💻 Why I'm Building AuthPad

> 🖇️AuthPad isn’t just a project — it’s my learning playground, and my commitment to building things the right way, even while I’m still learning.

---

## ✅ Current Features
- User registration with hashed passwords (`passlib[bcrypt]`)
- JWT-based token routes
- `/me` endpoint to fetch current user info
- Modular route structure with docstrings
- Input validation using Pydentic models (`UserCreate`, `UserRead`, etc.)
- async db connection (`PostgreSQL`) via `asyncpg`
- Custom error handling with meaningful HTTPException messages


## 🚧 Roadmap
- Refresh token support for longer sessions
- User account routes: update profile, change password, delete account
- Admin-only access to `/users/{id}`
- Role-based access control (RBAC)
- Rate limiting for brute-force protection *
- API docs with real-world examples
- Test coverage and CI setup (w/ pytest & Github Action)
- Docker support for local dev and deployment


## 🛠️ Tech Stack
- FastAPI
- Uvicorn
- Pydantic
- Python-Jose
- Passlib[bcrypt]
- PostgreSQL (via `asyncpg` and dependency injection)
- pytest


## 📦 Usage
Run locally:

    ```bash
    uvicorn app.main:app --reload

Run **quickly**:

    ```bash
    chmod +x setup.sh
    ./setup.sh
