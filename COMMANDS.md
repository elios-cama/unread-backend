# 🚀 Quick Command Reference

Common commands for Unread backend development.

## 🔧 Setup Commands

```bash
# Quick setup (automated)
python3 scripts/setup.py

# Manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp env.example .env
```

## 🏃‍♂️ Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Development server with auto-reload
python3 -m uvicorn app.main:app --reload

# Development server on specific host/port
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🗄️ Database Commands (Alembic)

```bash
# Create new migration (after model changes)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# See migration history
alembic history

# See current migration version
alembic current

# Create empty migration (manual)
alembic revision -m "Manual migration"
```

## 🧪 Testing Commands

```bash
# Run all tests
python3 -m pytest

# Run tests with coverage
python3 -m pytest --cov=app

# Run tests with coverage report
python3 -m pytest --cov=app --cov-report=html

# Run specific test file
python3 -m pytest tests/test_main.py

# Run specific test function
python3 -m pytest tests/test_main.py::test_root_endpoint

# Run tests with verbose output
python3 -m pytest -v

# Run tests and stop on first failure
python3 -m pytest -x
```

## 🎨 Code Quality Commands

```bash
# Format code with Black
python3 -m black app/

# Sort imports with isort
python3 -m isort app/

# Lint code with flake8
python3 -m flake8 app/

# Run all quality checks
python3 -m black app/ && python3 -m isort app/ && python3 -m flake8 app/

# Check formatting without applying
python3 -m black --check app/

# Check import sorting without applying
python3 -m isort --check-only app/
```

## 📦 Package Management

```bash
# Install new package
pip install package-name

# Install package and add to requirements
pip install package-name && pip freeze > requirements.txt

# Install from requirements
pip install -r requirements.txt

# Update all packages
pip list --outdated
pip install --upgrade package-name

# Show package info
pip show package-name
```

## 🔍 Development Helpers

```bash
# Check Python version
python3 --version

# Check if virtual environment is active
which python3

# List installed packages
pip list

# Show project structure
tree -I '__pycache__|*.pyc|venv'

# Find Python files
find . -name "*.py" -not -path "./venv/*"

# Count lines of code
find . -name "*.py" -not -path "./venv/*" | xargs wc -l
```

## 🌐 API Testing

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test root endpoint
curl http://localhost:8000/

# Open API docs in browser (macOS)
open http://localhost:8000/docs

# Test with httpie (if installed)
http GET localhost:8000/health
```

## 🔧 Environment Management

```bash
# Copy environment template
cp env.example .env

# Load environment variables (for testing)
export $(cat .env | xargs)

# Check environment variable
echo $DATABASE_URL

# Generate secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 🚀 Deployment Commands

```bash
# Railway CLI (if installed)
railway login
railway link
railway deploy

# Check Railway logs
railway logs

# Set Railway environment variable
railway variables set KEY=value
```

## 🐛 Debugging Commands

```bash
# Run with Python debugger
python3 -m pdb -m uvicorn app.main:app --reload

# Check imports
python3 -c "from app.main import app; print('Imports OK')"

# Test database connection
python3 -c "from app.db.database import engine; print('DB connection OK')"

# Check Alembic configuration
alembic check

# Show SQL that would be generated
alembic upgrade head --sql
```

## 📊 Monitoring Commands

```bash
# Monitor file changes
watch -n 1 'find . -name "*.py" -not -path "./venv/*" | xargs ls -la'

# Monitor logs (if using file logging)
tail -f logs/app.log

# Check process
ps aux | grep uvicorn

# Check port usage
lsof -i :8000
```

## 🔄 Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Add and commit changes
git add .
git commit -m "Add new feature"

# Push feature branch
git push origin feature/new-feature

# Merge to main (after PR approval)
git checkout main
git pull origin main
git merge feature/new-feature
git push origin main
```

## 💡 Tips

- Always activate virtual environment before running commands
- Use `python3 -m` prefix to ensure you're using the right Python
- Run tests before committing changes
- Format code before pushing
- Check migration files before applying them
- Keep environment files secure and never commit them 