import asyncio
import asyncpg
from urllib.parse import quote_plus

async def test_connection():
    password = "[@SHBchatbot]"
    encoded_pass = quote_plus(password)
    url = f"postgresql://postgres:{encoded_pass}@db.aehzparpmmjdzpxkuwic.supabase.co:5432/postgres"
    print(f"Connecting to {url.replace(encoded_pass, '***')}...")
    try:
        conn = await asyncpg.connect(url)
        print("Successfully connected to Supabase!")
        await conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection())
