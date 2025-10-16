![Status](https://img.shields.io/badge/Status-In_Progress-F57C00?style=flat-square&logo=todoist&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2196F3?style=flat-square&logo=open-source-initiative&logoColor=white)


# AuthPad 🔐

> **AuthPad** is built with FastAPI to simplify secure user management in modern web apps.


---

## ✅ Features
- User registeration with password hashing
- JWT-based login routes
- `/me` endpoint to fetch current user info
- Modular route structure with docstrings
- Pydantic-based input validation

> “Security is not a feature — it's a foundation.”


## 🧪 Soon...
- Refresh tokens
- Role-based access control (RBAC)
- Rate limiting
- API documetation with examples
- Test coverage and CI setup (w/ pytest & github action)


## 🛠️ Tech Stack
- FastAPI
- Uvicorn
- Pydantic
- Python-Jose
- Passlib
- PostgreSQL (planned)


## 📦 Usage
Run locally:
```bash
uvicorn app.main:app --reload