"""Script to create an admin user on Supabase asynchronously."""

import asyncio
import logging
import uuid

from sqlalchemy import text

from app.core.security import get_password_hash
from app.db.models.user import UserRole
from app.db.session import async_session_maker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_admin():
    email = "admin@example.com"
    password = "admin123"

    logger.info(f"Checking for admin user: {email}")

    async with async_session_maker() as session:
        try:
            # Check if user already exists
            result = await session.execute(
                text("SELECT id FROM users WHERE email = :email"),
                {"email": email}
            )
            user_exists = result.fetchone()

            if user_exists:
                logger.info(f"Admin user {email} already exists.")
                return

            # Create admin user
            hashed_password = get_password_hash(password)
            user_id = uuid.uuid4()

            # Using raw SQL to ensure bypass of any complex ORM logic if needed,
            # but ORM is cleaner if the model is ready.
            from app.db.models.user import User
            admin = User(
                id=user_id,
                email=email,
                hashed_password=hashed_password,
                is_active=True,
                role=UserRole.ADMIN.value,
                full_name="System Admin"
            )

            session.add(admin)
            await session.commit()
            logger.info(f"Admin user {email} created successfully with ID: {user_id}")
            logger.info(f"Login with Password: {password}")

        except Exception as e:
            logger.error(f"Error creating admin: {e}")
            await session.rollback()

if __name__ == "__main__":
    asyncio.run(create_admin())
