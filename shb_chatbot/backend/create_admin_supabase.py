import sqlalchemy
from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import bcrypt

def create_admin_sync():
    password = "[@SHBchatbot]"
    encoded_pass = quote_plus(password)
    # Sync URL
    url = f"postgresql://postgres:{encoded_pass}@db.aehzparpmmjdzpxkuwic.supabase.co:5432/postgres"
    print(f"Connecting (Sync) to Supabase...")
    
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

if __name__ == "__main__":
    create_admin_sync()
