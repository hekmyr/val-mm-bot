import os
from dotenv import load_dotenv
from convex import ConvexClient

# Load environment variables from .env.local before reading them
load_dotenv(".env.local")

CONVEX_URL = os.getenv("CONVEX_URL")

if not CONVEX_URL:
    raise ValueError("CONVEX_URL environment variable not set")

client = ConvexClient(CONVEX_URL)
