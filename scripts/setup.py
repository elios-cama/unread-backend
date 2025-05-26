#!/usr/bin/env python3
"""
Setup script for Unread backend development.
"""

import os
import sys
import subprocess
import secrets
from pathlib import Path


def run_command(command: str, description: str = ""):
    """Run a shell command and handle errors."""
    print(f"🔄 {description or command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"✅ {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False


def generate_secret_key():
    """Generate a secure secret key."""
    return secrets.token_urlsafe(32)


def setup_environment():
    """Set up the development environment."""
    print("🚀 Setting up Unread backend development environment...\n")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print("❌ Python 3.11+ is required")
        sys.exit(1)
    
    print(f"✅ Python {sys.version.split()[0]} detected")
    
    # Create virtual environment
    if not os.path.exists("venv"):
        print("\n📦 Creating virtual environment...")
        if not run_command("python3 -m venv venv", "Creating virtual environment"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")
    
    # Install dependencies
    print("\n📚 Installing dependencies...")
    activate_cmd = "source venv/bin/activate" if os.name != 'nt' else "venv\\Scripts\\activate"
    pip_cmd = f"{activate_cmd} && pip install -r requirements.txt"
    
    if not run_command(pip_cmd, "Installing Python packages"):
        print("❌ Failed to install dependencies")
        sys.exit(1)
    
    # Set up environment file
    setup_env_file()
    
    # Set up database
    setup_database()
    
    print("\n🎉 Setup complete!")
    print("\n📋 Next steps:")
    print("1. Activate virtual environment:")
    print("   source venv/bin/activate  # On macOS/Linux")
    print("   venv\\Scripts\\activate     # On Windows")
    print("\n2. Update your .env file with your Supabase credentials")
    print("\n3. Run the application:")
    print("   python3 -m uvicorn app.main:app --reload")
    print("\n4. Visit http://localhost:8000/docs for API documentation")


def setup_env_file():
    """Set up the environment file."""
    print("\n🔧 Setting up environment file...")
    
    if os.path.exists(".env"):
        print("✅ .env file already exists")
        return
    
    # Generate a secret key
    secret_key = generate_secret_key()
    
    # Read template and replace values
    with open("env.example", "r") as f:
        env_content = f.read()
    
    # Replace placeholder secret key
    env_content = env_content.replace(
        "your-super-secret-key-here-change-this-in-production",
        secret_key
    )
    
    # Write .env file
    with open(".env", "w") as f:
        f.write(env_content)
    
    print("✅ Created .env file with generated secret key")
    print("⚠️  Remember to update Supabase credentials in .env")


def setup_database():
    """Set up the database with Alembic."""
    print("\n🗄️  Setting up database...")
    
    activate_cmd = "source venv/bin/activate" if os.name != 'nt' else "venv\\Scripts\\activate"
    
    # Check if alembic is initialized
    if not os.path.exists("alembic/versions"):
        print("❌ Alembic versions directory not found")
        return
    
    # Create initial migration
    print("📝 Creating initial database migration...")
    migration_cmd = f"{activate_cmd} && alembic revision --autogenerate -m 'Initial migration'"
    
    if run_command(migration_cmd, "Creating initial migration"):
        print("✅ Initial migration created")
        
        # Apply migration
        print("🔄 Applying migration to database...")
        upgrade_cmd = f"{activate_cmd} && alembic upgrade head"
        
        if run_command(upgrade_cmd, "Applying database migration"):
            print("✅ Database migration applied successfully")
        else:
            print("⚠️  Migration failed - make sure your DATABASE_URL is correct in .env")
    else:
        print("⚠️  Migration creation failed - this is normal if you haven't set up your database yet")


def main():
    """Main setup function."""
    if len(sys.argv) > 1:
        if sys.argv[1] == "env":
            setup_env_file()
        elif sys.argv[1] == "db":
            setup_database()
        else:
            print("Usage: python3 scripts/setup.py [env|db]")
    else:
        setup_environment()


if __name__ == "__main__":
    main() 