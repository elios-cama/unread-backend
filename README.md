# Unread Backend

Backend API for the "[unread]" platform - a mobile-first ebook sharing platform for authors and readers.

## 🚀 Features

- **FastAPI** - Modern, fast web framework with full async support
- **PostgreSQL** - Dual Supabase instances (dev/prod) with migrations
- **OAuth-Only Authentication** - Google and Apple sign-in via Supabase
- **JWT Tokens** - Secure API access with token validation
- **Repository Pattern** - Clean separation of data access and business logic
- **Type Safety** - Complete type hints with Pydantic v2 validation
- **Mobile-Optimized** - Grid endpoints and efficient data structures
- **Auto Documentation** - Interactive API docs with real-time testing

## 🏗️ Architecture

### Core Entities
- **Users** - OAuth-only authentication (Google/Apple) with username-based profiles
- **Ebooks** - Digital books with metadata, file storage, and privacy controls
- **Collections** - Series/groupings of ebooks with color theming and privacy settings
- **Share Links** - Trackable sharing with analytics *(planned)*
- **Reading Progress** - User reading state and bookmarks *(planned)*
- **Reviews** - User feedback and ratings *(planned)*

### API Structure
```
/api/v1/
├── auth/          # ✅ OAuth authentication (Supabase integration)
├── users/         # ✅ User management and profiles
├── ebooks/        # ✅ Ebook CRUD and file operations
├── collections/   # ✅ Collection management with grid endpoints
├── shares/        # 📝 Share link generation and tracking (planned)
├── reading/       # 📝 Reading progress and bookmarks (planned)
└── reviews/       # 📝 Review and rating system (planned)
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
# Database (Supabase PostgreSQL)
DATABASE_URL=postgresql+asyncpg://postgres.xxx:password@aws-0-region.pooler.supabase.com:5432/postgres

# JWT Security
JWT_SECRET_KEY=your-secure-jwt-secret
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-key

# OAuth Providers
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
APPLE_CLIENT_ID=your-apple-client-id
APPLE_CLIENT_SECRET=your-apple-client-secret

# Environment
ENVIRONMENT=development  # or production
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
# Development database
cp env.development .env
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head

# Production database  
cp env.production .env
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current migration status
alembic current
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

**✅ Authentication System**:
- Complete OAuth-only authentication (Google & Apple via Supabase)
- JWT token generation and validation
- User profile management with username-based identification
- Supabase integration for user verification

**✅ Database & Models**:
- Complete database schema with proper relationships
- User model (OAuth-only, no email/password)
- Ebook model with file storage support
- Collection model with privacy controls and color theming
- Database migrations with Alembic (dev/prod environments)

**✅ Core API Endpoints**:
- **Authentication**: `/api/v1/auth/supabase` - OAuth token exchange
- **Users**: Profile management, username checks, user search
- **Ebooks**: Full CRUD, file uploads, downloads with pagination
- **Collections**: Complete collection management with grid-optimized endpoints
- Interactive API documentation at `/docs`

**✅ Advanced Features**:
- Repository pattern for clean data access
- Service layer for business logic
- Privacy controls (public/private content)
- Collection color theming for frontend gradients
- Grid-optimized endpoints for mobile UI
- Comprehensive error handling and logging

**✅ Infrastructure**:
- Railway deployment ready
- Dual environment setup (dev/prod Supabase instances)
- Async/await throughout the application
- Type safety with Pydantic schemas
- CORS configuration for mobile apps

**📝 TODO (Future Enhancements)**:
- Share link system with analytics
- Reading progress tracking and bookmarks
- Review and rating system
- Advanced search and filtering
- Background job processing
- Real-time notifications

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