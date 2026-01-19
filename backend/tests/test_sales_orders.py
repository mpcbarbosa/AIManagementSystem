import pytest
from fastapi import HTTPException
import uuid

from app.models.customer import Customer
from app.models.contact import Contact
from app.models.address import Address
from app.models.item import Item


def test_create_sales_order(client, db):
    # Create test data
    customer = Customer(name="Test Customer")
    db.add(customer)
    db.flush()  # to get id
    customer_id = str(customer.id)

    contact = Contact(customer_id=customer.id, phone="123456789", name="Test Contact")
    db.add(contact)
    db.flush()
    contact_id = str(contact.id)

    address = Address(customer_id=customer.id, alias="Test Address", street="Test St", city="Test City")
    db.add(address)
    db.flush()
    address_id = str(address.id)

    item1 = Item(code="TEST004", name="Test Item 1", price=10.0)
    item2 = Item(code="TEST005", name="Test Item 2", price=20.0)
    db.add(item1)
    db.add(item2)
    db.flush()
    item1_id = str(item1.id)
    item2_id = str(item2.id)
    db.commit()

    order_data = {
        "customer_id": customer_id,
        "contact_id": contact_id,
        "address_id": address_id,
        "items": [
            {"item_id": item1_id, "quantity": 2},
            {"item_id": item2_id, "quantity": 1}
        ]
    }
    response = client.post("/sales-orders/", json=order_data)
    assert response.status_code == 200
    data = response.json()
    assert data["customer_id"] == customer_id
    assert data["contact_id"] == contact_id
    assert data["address_id"] == address_id
    assert len(data["items"]) == 2
    assert data["order_total"] == 40.0  # 2*10 + 1*20
    assert "id" in data


def test_get_sales_order(client, db):
    # Create test data as above
    customer = Customer(name="Test Customer 2")
    db.add(customer)
    db.flush()
    customer_id = str(customer.id)

    contact = Contact(customer_id=customer.id, phone="987654321", name="Test Contact")
    db.add(contact)
    db.flush()
    contact_id = str(contact.id)

    address = Address(customer_id=customer.id, alias="Test Address", street="Test St", city="Test City")
    db.add(address)
    db.flush()
    address_id = str(address.id)

    item = Item(code="TEST003", name="Test Item", price=15.0)
    db.add(item)
    db.flush()
    item_id = str(item.id)
    db.commit()

    order_data = {
        "customer_id": customer_id,
        "contact_id": contact_id,
        "address_id": address_id,
        "items": [{"item_id": item_id, "quantity": 3}]
    }
    response = client.post("/sales-orders/", json=order_data)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Get
    response = client.get(f"/sales-orders/{order_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["order_total"] == 45.0


def test_update_sales_order(client, db):
    # Create initial order
    customer = Customer(name="Test Customer 3")
    db.add(customer)
    db.flush()
    customer_id = str(customer.id)

    contact = Contact(customer_id=customer.id, phone="111111111", name="Test Contact")
    db.add(contact)
    db.flush()
    contact_id = str(contact.id)

    address = Address(customer_id=customer.id, alias="Test Address", street="Test St", city="Test City")
    db.add(address)
    db.flush()
    address_id = str(address.id)

    item1 = Item(code="TEST001", name="Test Item 1", price=10.0)
    item2 = Item(code="TEST002", name="Test Item 2", price=20.0)
    db.add(item1)
    db.add(item2)
    db.flush()
    item1_id = str(item1.id)
    item2_id = str(item2.id)
    db.commit()

    order_data = {
        "customer_id": customer_id,
        "contact_id": contact_id,
        "address_id": address_id,
        "items": [{"item_id": item1_id, "quantity": 1}]
    }
    response = client.post("/sales-orders/", json=order_data)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Update
    update_data = {
        "customer_id": customer_id,
        "contact_id": contact_id,
        "address_id": address_id,
        "items": [
            {"item_id": item1_id, "quantity": 2},
            {"item_id": item2_id, "quantity": 1}
        ]
    }
    response = client.put(f"/sales-orders/{order_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["order_total"] == 40.0


def test_delete_sales_order(client, db):
    # Create order
    customer = Customer(name="Test Customer 4")
    db.add(customer)
    db.flush()
    customer_id = str(customer.id)

    contact = Contact(customer_id=customer.id, phone="222222222", name="Test Contact")
    db.add(contact)
    db.flush()
    contact_id = str(contact.id)

    address = Address(customer_id=customer.id, alias="Test Address", street="Test St", city="Test City")
    db.add(address)
    db.flush()
    address_id = str(address.id)

    item = Item(code="TEST006", name="Test Item", price=10.0)
    db.add(item)
    db.flush()
    item_id = str(item.id)
    db.commit()

    order_data = {
        "customer_id": customer_id,
        "contact_id": contact_id,
        "address_id": address_id,
        "items": [{"item_id": item_id, "quantity": 1}]
    }
    response = client.post("/sales-orders/", json=order_data)
    assert response.status_code == 200
    order_id = response.json()["id"]

    # Delete
    response = client.delete(f"/sales-orders/{order_id}")
    assert response.status_code == 204

    # Get should 404
    response = client.get(f"/sales-orders/{order_id}")
    assert response.status_code == 404