from dotenv import load_dotenv
import os
load_dotenv()

def get_database_url() -> str:
    if not os.getenv("DATABASE_URL"):
        raise ValueError("DATABASE_URL environment variable not set")
    return os.getenv("DATABASE_URL")

def get_Auth_Token() -> str:
    if not os.getenv("GITHUB_TOKEN"):
        raise ValueError("GITHUB_TOKEN environment variable not set")
    return os.getenv("GITHUB_TOKEN")