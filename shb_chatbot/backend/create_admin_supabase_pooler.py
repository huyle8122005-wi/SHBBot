from urllib.parse import quote_plus

import bcrypt
from sqlalchemy import create_engine, text


def create_admin_sync():
    password = "[@SHBchatbot]"
    encoded_pass = quote_plus(password)
    # Pooler URL on Port 6543 (usually IPv4 friendly)
    url = f"postgresql://postgres:{encoded_pass}@aehzparpmmjdzpxkuwic.pooler.supabase.com:6543/postgres"
    print("Connecting (Sync Pooler) to Supabase...")

    try:
        engine = create_engine(url)

        email = "admin@example.com"
        raw_password = "admin123"
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        with engine.connect() as conn:
            print("Connected!")
            # Check if user exists
            result = conn.execute(text("SELECT id FROM users WHERE email = :email"), {"email": email}).fetchone()
            if result:
                print(f"User {email} already exists.")
                return

            # Insert user
            import uuid
            user_id = str(uuid.uuid4())
            conn.execute(
                text("INSERT INTO users (id, email, hashed_password, is_active, role) VALUES (:id, :email, :password, :active, :role)"),
                {"id": user_id, "email": email, "password": hashed_password, "active": True, "role": "admin"}
            )
            conn.commit()
            print(f"User {email} created successfully on Supabase!")
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    create_admin_sync()
