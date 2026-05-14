"""Script to force initialize Supabase database schema and admin user."""

import asyncio
import logging
from urllib.parse import quote_plus

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.security import get_password_hash
from app.db.models.user import UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use direct credentials if env is not loaded correctly in this context
# Update these with your ACTUAL Supabase details if running manually
DB_HOST = "db.aehzparpmmjdzpxkuwic.supabase.co"
DB_USER = "postgres"
DB_PASS = "[@SHBchatbot]" # Encoded later
DB_NAME = "postgres"

async def initialize_db():
    encoded_pass = quote_plus(DB_PASS)
    # Force use the direct connection string with encoded password
    url = f"postgresql+asyncpg://{DB_USER}:{encoded_pass}@{DB_HOST}:5432/{DB_NAME}"

    logger.info(f"Connecting to: {DB_HOST}")
    engine = create_async_engine(url)

    async with engine.begin() as conn:
        try:
            logger.info("Ensuring 'users' table exists...")
            # Simple DDL to ensure table exists if migrations haven't run
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id UUID PRIMARY KEY,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255),
                    full_name VARCHAR(255),
                    is_active BOOLEAN DEFAULT TRUE NOT NULL,
                    role VARCHAR(50) DEFAULT 'user' NOT NULL,
                    avatar_url VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """))

            email = "admin@example.com"
            password = "admin123"

            # Check for existing admin
            result = await conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            if result.fetchone():
                logger.info(f"Admin {email} already exists. Updating password...")
                hashed_password = get_password_hash(password)
                await conn.execute(
                    text("UPDATE users SET hashed_password = :password WHERE email = :email"),
                    {"email": email, "password": hashed_password}
                )
            else:
                import uuid
                logger.info(f"Creating new admin: {email}")
                hashed_password = get_password_hash(password)
                await conn.execute(
                    text("""
                        INSERT INTO users (id, email, hashed_password, is_active, role, full_name)
                        VALUES (:id, :email, :password, :active, :role, :full_name)
                    """),
                    {
                        "id": uuid.uuid4(),
                        "email": email,
                        "password": hashed_password,
                        "active": True,
                        "role": UserRole.ADMIN.value,
                        "full_name": "System Admin"
                    }
                )

            logger.info("Database initialization complete!")
            logger.info(f"ADMIN LOGIN: {email} / {password}")

        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(initialize_db())
