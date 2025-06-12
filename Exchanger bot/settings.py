from dotenv import load_dotenv
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")
CURRENCY_API_URL = os.getenv("CURRENCY_API_URL")
DATABASE = "./data.json"