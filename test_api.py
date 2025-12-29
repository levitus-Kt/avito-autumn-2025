import random
import time
import pytest
import requests
from jsonschema import validate


BASE_URL = "https://qa-internship.avito.com/api/1"


# JSON-схемы валидации ответов
CREATE_SCHEMA = {
    "type": "object",
    "required": ["id", "sellerId", "name", "price", "statistics", "createdAt"],
    "properties": {
        "id": {"type": "string"},
        "sellerId": {"type": "integer"},
        "name": {"type": "string"},
        "price": {"type": "integer"},
        "createdAt": {"type": "string"},
        "statistics": {
            "type": "object",
            "required": ["likes", "viewCount", "contacts"],
            "properties": {
                "likes": {"type": "integer"},
                "viewCount": {"type": "integer"},
                "contacts": {"type": "integer"}
            }
        }
    }
}
