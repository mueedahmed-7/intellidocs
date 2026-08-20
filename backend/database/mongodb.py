# import os

# from dotenv import load_dotenv
# from pymongo import MongoClient


# load_dotenv()


# MONGODB_URI = os.getenv("MONGODB_URI")
# DATABASE_NAME = os.getenv(
#     "DATABASE_NAME", "RAG-Chatbot",
# )


# if not MONGODB_URI:
#     raise ValueError(
#         "MONGODB_URI is not configured."
#     )


# client = MongoClient(MONGODB_URI)

# db = client[DATABASE_NAME]

# users_collection = db["users"]
# documents_collection = db["documents"]
# chats_collection = db["chats"]
# messages_collection = db["messages"]

import os

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

DATABASE_NAME = os.getenv(
    "DATABASE_NAME",
    "RAG-Chatbot",
)

if not MONGODB_URI:
    raise ValueError(
        "MONGODB_URI is not configured."
    )

client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000,
    socketTimeoutMS=10000,
)

try:
    client.admin.command("ping")
    print("MongoDB connected successfully.")

except ServerSelectionTimeoutError as e:
    print("MongoDB connection failed.")
    print(e)
    raise

db = client[DATABASE_NAME]

users_collection = db["users"]
documents_collection = db["documents"]
chats_collection = db["chats"]
messages_collection = db["messages"]