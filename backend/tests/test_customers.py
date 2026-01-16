import pytest
from fastapi import HTTPException

def test_create_customer_no_addresses_contacts(client):
    customer_data = {
        "name": "Test Customer",
        "addresses": [],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Customer"
    assert data["addresses"] == []
    assert data["contacts"] == []
    assert "id" in data

def test_create_customer_with_addresses(client):
    customer_data = {
        "name": "Test Customer 2",
        "addresses": [
            {
                "alias": "Home",
                "street": "123 Main St",
                "city": "Anytown"
            }
        ],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Customer 2"
    assert len(data["addresses"]) == 1
    assert data["addresses"][0]["alias"] == "Home"
    assert data["addresses"][0]["street"] == "123 Main St"
    assert data["addresses"][0]["city"] == "Anytown"
    assert data["contacts"] == []

def test_create_customer_duplicate_address_alias(client):
    # First create a customer with an address
    customer_data = {
        "name": "Test Customer 3",
        "addresses": [
            {
                "alias": "Work",
                "street": "456 Office St",
                "city": "Business City"
            }
        ],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200

    # Try to create another customer with same alias (but different customer, so should be ok? Wait, alias is per customer.
    # Wait, the constraint is unique per customer on alias_normalized.
    # So for same customer, duplicate alias should fail.

    # Actually, the test is "Duplicate address alias conflict", probably meaning within the same request or for same customer.

    # Looking back: "Duplicate address alias conflict" - likely when creating with two addresses with same alias.

    customer_data = {
        "name": "Test Customer 4",
        "addresses": [
            {
                "alias": "Home",
                "street": "123 Main St",
                "city": "Anytown"
            },
            {
                "alias": "home",  # same normalized
                "street": "789 Other St",
                "city": "Othertown"
            }
        ],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 409  # Conflict

def test_get_customer(client):
    # First create
    customer_data = {
        "name": "Test Customer 5",
        "addresses": [],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    customer_id = response.json()["id"]

    # Then get
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Customer 5"

def test_update_customer(client):
    # Create
    customer_data = {
        "name": "Test Customer 6",
        "addresses": [
            {
                "alias": "Old Address",
                "street": "Old St",
                "city": "Old City"
            }
        ],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    customer_id = response.json()["id"]

    # Update
    update_data = {
        "name": "Updated Customer 6",
        "addresses": [
            {
                "alias": "New Address",
                "street": "New St",
                "city": "New City"
            }
        ],
        "contacts": []
    }
    response = client.put(f"/customers/{customer_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Customer 6"
    assert len(data["addresses"]) == 1
    assert data["addresses"][0]["alias"] == "New Address"

def test_delete_customer(client):
    # Create
    customer_data = {
        "name": "Test Customer 7",
        "addresses": [],
        "contacts": []
    }
    response = client.post("/customers/", json=customer_data)
    assert response.status_code == 200
    customer_id = response.json()["id"]

    # Delete
    response = client.delete(f"/customers/{customer_id}")
    assert response.status_code == 204

    # Get should 404
    response = client.get(f"/customers/{customer_id}")
    assert response.status_code == 404