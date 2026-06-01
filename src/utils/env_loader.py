"""[BOILERPLATE] Environment variable loading.

Do not modify per client.
"""
import os

from dotenv import load_dotenv

load_dotenv()

# Universal
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "chatbot")
PINECONE_API = os.getenv("PINECONE_API")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE")

# Gupshup
GUPSHUP_API_KEY = os.getenv("GUPSHUP_API_KEY")
GUPSHUP_APP_NAME = os.getenv("GUPSHUP_APP_NAME")
GUPSHUP_SOURCE = os.getenv("GUPSHUP_SOURCE")
GUPSHUP_APP_ID = os.getenv("GUPSHUP_APP_ID")

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",")

# App
APP_TITLE = os.getenv("APP_TITLE", "Chatbot Backend")
ENV_MODE = os.getenv("ENV_MODE", "dev")
