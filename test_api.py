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

GET_ITEM_SCHEMA = {
    "type": "array",
    "items": CREATE_SCHEMA  # GET /item/{id} возвращает массив с одним элементом
}

STATS_SCHEMA = {
    "type": "array",
    "items": {
        "type": "object",
        "required": ["likes", "viewCount", "contacts"],
        "properties": {
            "likes": {"type": "integer"},
            "viewCount": {"type": "integer"},
            "contacts": {"type": "integer"}
        }
    }
}


# Класс-клиент для взаимодействия с API
class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def create_item(self, payload: dict) -> requests.Response:
        """POST /api/1/item — создание объявления"""
        return requests.post(f"{self.base_url}/item", json=payload)

    def get_item(self, item_id: str) -> requests.Response:
        """GET /api/1/item/{id} — получение объявления по ID"""
        return requests.get(f"{self.base_url}/item/{item_id}")

    def get_items_by_seller(self, seller_id: int) -> requests.Response:
        """GET /api/1/{sellerID}/item — получение всех объявлений продавца"""
        return requests.get(f"{self.base_url}/{seller_id}/item")

    def get_stats(self, item_id: str) -> requests.Response:
        """GET /api/1/statistic/{id} — получение статистики по объявлению"""
        return requests.get(f"{self.base_url}/statistic/{item_id}")

