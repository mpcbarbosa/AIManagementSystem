import pytest
from fastapi import HTTPException

def test_create_item_ok(client):
    item_data = {
        "code": "ITEM001",
        "name": "Test Item",
        "price": 10.99
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "ITEM001"
    assert data["name"] == "Test Item"
    assert data["price"] == 10.99
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

def test_create_item_duplicate_code(client):
    # First create
    item_data = {
        "code": "ITEM002",
        "name": "Test Item 2",
        "price": 5.50
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200

    # Try duplicate
    response = client.post("/items/", json=item_data)
    assert response.status_code == 409

def test_create_item_negative_price(client):
    item_data = {
        "code": "ITEM003",
        "name": "Test Item 3",
        "price": -1.0
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 422  # Validation error

def test_get_item(client):
    # Create first
    item_data = {
        "code": "ITEM004",
        "name": "Test Item 4",
        "price": 20.0
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Get
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["code"] == "ITEM004"
    assert data["name"] == "Test Item 4"

def test_get_item_not_found(client):
    response = client.get("/items/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404

def test_get_items_list(client):
    # Create a few
    for i in range(3):
        item_data = {
            "code": f"LIST{i}",
            "name": f"List Item {i}",
            "price": float(i + 1)
        }
        response = client.post("/items/", json=item_data)
        assert response.status_code == 200

    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) >= 3

def test_update_item(client):
    # Create
    item_data = {
        "code": "ITEM005",
        "name": "Test Item 5",
        "price": 15.0
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Update
    update_data = {
        "name": "Updated Item 5",
        "price": 25.0
    }
    response = client.put(f"/items/{item_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Item 5"
    assert data["price"] == 25.0
    assert data["code"] == "ITEM005"  # Unchanged

def test_update_item_not_found(client):
    update_data = {
        "name": "Nonexistent",
        "price": 1.0
    }
    response = client.put("/items/00000000-0000-0000-0000-000000000000", json=update_data)
    assert response.status_code == 404

def test_delete_item(client):
    # Create
    item_data = {
        "code": "ITEM006",
        "name": "Test Item 6",
        "price": 30.0
    }
    response = client.post("/items/", json=item_data)
    assert response.status_code == 200
    item_id = response.json()["id"]

    # Delete
    response = client.delete(f"/items/{item_id}")
    assert response.status_code == 204

    # Get should 404
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 404

def test_delete_item_not_found(client):
    response = client.delete("/items/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404