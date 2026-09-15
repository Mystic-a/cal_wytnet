"""
Database migration script to add WytPass SSO columns
Run this once to update existing production database
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./calculator.db")

# Fix postgres:// to postgresql:// for SQLAlchemy 1.4+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)

def migrate():
    """Add WytPass columns to users table if they don't exist"""
    with engine.connect() as conn:
        try:
            # Check if columns exist
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='users' AND column_name IN ('wytpass_id', 'is_sso_user')
            """))
            existing_columns = [row[0] for row in result]
            
            # Add wytpass_id if missing
            if 'wytpass_id' not in existing_columns:
                print("Adding wytpass_id column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN wytpass_id VARCHAR"))
                conn.commit()
                print("✅ Added wytpass_id column")
            else:
                print("✓ wytpass_id column already exists")
            
            # Add is_sso_user if missing
            if 'is_sso_user' not in existing_columns:
                print("Adding is_sso_user column...")
                conn.execute(text("ALTER TABLE users ADD COLUMN is_sso_user BOOLEAN DEFAULT FALSE"))
                conn.commit()
                print("✅ Added is_sso_user column")
            else:
                print("✓ is_sso_user column already exists")
            
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == "__main__":
    migrate()
