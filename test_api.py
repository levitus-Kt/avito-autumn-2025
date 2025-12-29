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


#Фикстуры
@pytest.fixture(scope="module")
def api_client() -> ApiClient:
    """
    Фикстура для создания единого клиента на весь модуль (экономия ресурсов)
    """
    return ApiClient(BASE_URL)


@pytest.fixture(scope="module")
def seller_id() -> int:
    """
    Генерация уникального sellerID в рекомендованном диапазоне
    """
    return random.randint(111111, 999999)


@pytest.fixture
def create_payload(seller_id: int) -> dict:
    """
    Базовый payload для создания объявления
    """
    return {
        "sellerID": seller_id,
        "name": f"Test Item {random.randint(1, 10000)}",  # Уникальное имя
        "price": random.randint(100, 50000),
        "statistics": {
            "likes": random.randint(0, 100),
            "viewCount": random.randint(0, 200),
            "contacts": random.randint(0, 50)
        }
    }


# Тесты
def test_create_item_success(api_client: ApiClient, create_payload: dict):
    """Проверка успешного создания объявления с валидными данными"""
    response = api_client.create_item(create_payload)
    assert response.status_code == 200, f"Ожидали 200, получили {response.status_code}: {response.text}"

    data = response.json()
    validate(instance=data, schema=CREATE_SCHEMA)  # Проверка контракта
    assert data["sellerId"] == create_payload["sellerID"]


def test_create_item_missing_field(api_client: ApiClient, create_payload: dict):
    """Негативный тест: отсутствие обязательного поля (name)"""
    del create_payload["name"] 
    response = api_client.create_item(create_payload)
    assert response.status_code == 400, f"Ожидали 400 при отсутствии поля, получили {response.status_code}"


def test_get_item_success(api_client: ApiClient, create_payload: dict):
    """Проверка получения объявления по ID после создания"""
    # Создаём объявление
    create_resp = api_client.create_item(create_payload)
    assert create_resp.status_code == 200
    item_id = create_resp.json()["id"]

    # Получаем по ID
    response = api_client.get_item(item_id)
    assert response.status_code == 200

    data = response.json()
    validate(instance=data, schema=GET_ITEM_SCHEMA)
    assert len(data) == 1
    assert data[0]["id"] == item_id
    assert data[0]["sellerId"] == create_payload["sellerID"]


def test_get_item_not_found(api_client: ApiClient):
    """Проверка поведения при запросе несуществующего ID"""
    response = api_client.get_item("non_existent_id_12345")
    assert response.status_code == 404


def test_get_items_by_seller_success(api_client: ApiClient, seller_id: int, create_payload: dict):
    """Проверка получения списка объявлений одного продавца (несколько объявлений)"""
    # Создаём первое объявление
    api_client.create_item(create_payload)
    time.sleep(0.5)

    # Создаём второе объявление с тем же sellerID
    second_payload = create_payload.copy()
    second_payload["name"] = f"Second Item {random.randint(1, 10000)}"
    api_client.create_item(second_payload)

    time.sleep(0.5)

    # Получаем все объявления продавца
    response = api_client.get_items_by_seller(seller_id)
    assert response.status_code == 200

    data = response.json()
    validate(instance=data, schema=GET_ITEM_SCHEMA)
    assert len(data) >= 2


def test_get_items_by_seller_no_items(api_client: ApiClient):
    """Проверка получения пустого списка для продавца без объявлений"""
    new_seller_id = random.randint(111111, 999999)  # Гарантированно новый
    response = api_client.get_items_by_seller(new_seller_id)
    assert response.status_code == 200
    assert response.json() == []