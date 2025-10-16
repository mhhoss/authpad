import os
from databases import Database
from dotenv import load_dotenv


load_dotenv()
DB_URL = os.getenv("DB_URL")
db = Database(DB_URL)

