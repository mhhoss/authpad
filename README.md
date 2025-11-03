![Status](https://img.shields.io/badge/Status-In_Progress-F57C00?style=flat-square&logo=todoist&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-2196F3?style=flat-square&logo=open-source-initiative&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat-square&logo=fastapi)


# AuthPad 🔐

**Production-ready authentication system** built with FastAPI and PostgreSQL. Designed to be secure, scalable, and developer-friendly.

## 🎯 Why AuthPad?

> 🖇️ Most authentication tutorials teach the basics but skip real-world complexity. **AuthPad bridges that gap** - it's a complete auth system that actually handles production needs like email verification, security best practices, and proper error handling.

---

## ✅ Features

- **🔐 JWT Authentication** - Secure token-based auth with configurable expiry
- **👤 User Management** - Registration, login, and profile management
- **📧 Email Verification** - OTP-based verification flow with SMTP delivery
- **🔒 Password Security** - BCrypt hashing
- **🐍 Async PostgreSQL** - High-performance async database operations
- **✅ Input Validation** - Type-safe Pydantic schemas (UserRequest, UserOut, and etc..)
- **🎯 Error Handling** - Custom HTTP exceptions with meaningful messages
- **📚 API Documentation** - Auto-generated OpenAPI docs with examples

## 🗺️ Roadmap

**🔄 Authentication**
- Password recovery and reset flow
- Two-factor authentication (2FA)
- Social login

**👥 User Management**
- User profile updates
- Password change functionality
- Account deletion
- Admin user management

**🛡️ Security**
- Role-based access control (RBAC)
- Rate limiting
- Audit logging

## 🛠️ Tech Stack

**Backend Framework**
- FastAPI - Modern, fast web framework
- Uvicorn - ASGI server for production

**Authentication & Security**
- Python-JOSE - JWT token handling
- Passlib[bcrypt] - Password hashing and verification
- Python-multipart - Form data handling

**Database & ORM**
- PostgreSQL - Primary database
- asyncpg - Async database driver
- SQLAlchemy - ORM and database models

**Development & Testing**
- Pytest - Testing framework with async support
- HTTPX - Async HTTP client for tests
- Python-dotenv - Environment management

## 📚 API Reference

- `POST	/auth/register`	Create new account
- `POST	/auth/token` Login & get JWT
- `POST /auth/refersh` Refresh token
- `POST	/auth/verify-email`	Verify email with OTP
- `POST	/auth/request-verification`	Request email verification
- `POST /auth/logout` Log out current user and invalidate token

- `GET	/users/me` Get current user profile

---

## 🧪 Testing

    ```bash

    # Run all tests
    pytest

    # Run specific test module
    pytest tests/auth/test_routes.py -v


## 📦 Usage
Run **Server**:

    ```bash
    uvicorn app.main:app --reload --port 8000

Run **quickly**:

    ```bash
    chmod +x setup.sh
    ./setup.sh


## ⚡Installation

```bash
git clone https://github.com/mhhoss/authpad.git
cd authpad

pip install -r requirements.txt

cp .env.example .env