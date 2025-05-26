# Unread Backend

Backend API for the "[unread]" platform - a mobile-first ebook sharing platform for authors and readers.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **PostgreSQL** - Robust relational database via Supabase
- **JWT Authentication** - Secure token-based authentication
- **OAuth Integration** - Google and Apple sign-in support
- **File Storage** - Supabase Storage for ebooks and cover images
- **Async/Await** - Full async support for better performance
- **Type Hints** - Complete type safety with Pydantic
- **Auto Documentation** - Interactive API docs with Swagger UI

## 🏗️ Architecture

### Core Entities
- **Users** - Authors and readers with role-based access
- **Ebooks** - Digital books with metadata and file storage
- **Collections** - Series/groupings of ebooks by authors
- **Share Links** - Trackable sharing with analytics
- **Reading Progress** - User reading state and bookmarks
- **Reviews** - User feedback and ratings

### API Structure
```
/api/v1/
├── auth/          # Authentication (login, register, OAuth)
├── users/         # User management and profiles
├── ebooks/        # Ebook CRUD and file operations
├── collections/   # Collection/series management
├── shares/        # Share link generation and tracking
├── reading/       # Reading progress and bookmarks
└── reviews/       # Review and rating system
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL (via Supabase)
- **ORM**: SQLAlchemy 2.0 (async)
- **Authentication**: JWT + OAuth (Google, Apple)
- **File Storage**: Supabase Storage
- **Validation**: Pydantic v2
- **Testing**: pytest + pytest-asyncio
- **Code Quality**: black, isort, flake8

## 📦 Quick Start

### Automated Setup (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd backend

# Run the setup script
python3 scripts/setup.py
```

This will automatically:
- Create virtual environment
- Install dependencies
- Generate secure `.env` file
- Set up database migrations

### Manual Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your Supabase credentials

# Set up database
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Run the application
python3 -m uvicorn app.main:app --reload
```

## 📚 Detailed Setup Guide

For comprehensive setup instructions including:
- **Alembic explanation** and database migrations
- **Environment configuration** for development and production
- **Supabase setup** with multiple environments
- **Railway deployment** guide
- **Troubleshooting** common issues

👉 **See [SETUP.md](SETUP.md) for the complete guide**

## 🔧 Configuration

### Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/unread_db

# Security
SECRET_KEY=your-secret-key-here

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key
```

See `env.example` for all available configuration options.

## 🚀 Running the Application

```bash
# Development
python3 -m uvicorn app.main:app --reload

# Production (Railway handles this automatically)
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Visit:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 🧪 Testing

```bash
# Run all tests
python3 -m pytest

# Run with coverage
python3 -m pytest --cov=app

# Run specific test file
python3 -m pytest tests/test_main.py
```

## 🔨 Development

### Database Migrations (Alembic)

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality

```bash
# Format code
python3 -m black app/

# Sort imports
python3 -m isort app/

# Lint code
python3 -m flake8 app/

# Run all quality checks
python3 -m black app/ && python3 -m isort app/ && python3 -m flake8 app/
```

## 🚀 Deployment

### Railway Deployment

1. **Connect repository** to Railway
2. **Set environment variables** in Railway dashboard
3. **Deploy** - Railway auto-detects Python apps

The project includes:
- `Procfile` for Railway
- `railway.json` configuration
- Health check endpoints
- Production-ready settings

## 📁 Project Structure

```
backend/
├── app/
│   ├── api/v1/endpoints/     # API route handlers
│   ├── core/                 # Configuration and security
│   ├── db/                   # Database connection
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic
│   └── main.py               # FastAPI app
├── alembic/                  # Database migrations
├── scripts/                  # Setup and utility scripts
├── tests/                    # Test files
├── requirements.txt          # Dependencies
├── SETUP.md                  # Detailed setup guide
└── README.md                 # This file
```

## 🎯 What's Implemented

**✅ Core Infrastructure**:
- Complete database schema (Users, Ebooks, Collections, etc.)
- Authentication system with JWT
- API structure and routing
- Database migrations with Alembic
- Testing framework
- Deployment configuration

**📝 TODO (Next Development Phase)**:
- Implement API endpoints
- File upload handling
- Supabase Storage integration
- OAuth provider integration
- Email verification
- Advanced search and filtering

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🆘 Support

- **Setup Issues**: Check [SETUP.md](SETUP.md)
- **API Documentation**: Visit `/docs` when running locally
- **Create Issues**: Use GitHub issues for bugs and feature requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. 