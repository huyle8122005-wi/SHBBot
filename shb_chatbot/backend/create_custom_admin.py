import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.security import get_password_hash
from app.db.models.user import UserRole
import os
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use direct credentials for Supabase - Trying IPv4 pooler IP
DB_HOST = "172.67.158.141" # One of the IPs for aehzparpmmjdzpxkuwic.pooler.supabase.com
DB_USER = "postgres.aehzparpmmjdzpxkuwic" # Prefixed user for pooler
DB_PASS = "[@SHBchatbot]" 
DB_NAME = "postgres"

async def create_shbbot_admin():
    encoded_pass = quote_plus(DB_PASS)
    # Using asyncpg URL - port 6543 for pooler
    url = f"postgresql+asyncpg://{DB_USER}:{encoded_pass}@{DB_HOST}:6543/{DB_NAME}"
    
    logger.info(f"Connecting to Supabase (Pooler IP) to create admin user...")
    
    engine = create_async_engine(url, connect_args={"ssl": "require"})
    
    async with engine.begin() as conn:
        try:
            email = "shbbot@gmail.com"
            password = "shbbot"
            
            # Check for existing user
            result = await conn.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            row = result.fetchone()
            
            hashed_password = get_password_hash(password)
            
            if row:
                logger.info(f"User {email} already exists. Promoting to ADMIN and updating password...")
                await conn.execute(
                    text("UPDATE users SET hashed_password = :password, role = :role WHERE email = :email"),
                    {"email": email, "password": hashed_password, "role": UserRole.ADMIN.value}
                )
            else:
                import uuid
                logger.info(f"Creating new ADMIN user: {email}")
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
                        "full_name": "SHB Bot Admin"
                    }
                )
            
            logger.info("Admin user created/updated successfully on Supabase!")
            logger.info(f"CREDENTIALS: {email} / {password}")
            
        except Exception as e:
            logger.error(f"Failed to create admin: {e}")
            raise
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(create_shbbot_admin())
