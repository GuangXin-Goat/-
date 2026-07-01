#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
from decimal import Decimal
from datetime import date, timedelta
from random import randint

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth.models import User
from apps.products.models import Category, Product
from apps.sales.models import Customer, Lead, Opportunity
from apps.inventory.models import Supplier, Warehouse, InventoryItem


def create_users():
    print("Create users...")
    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@elevator.com", "admin123")
        print("  - admin / admin123")
    if not User.objects.filter(username="sales1").exists():
        User.objects.create_user("sales1", "sales1@elevator.com", "sales123")
        print("  - sales1 / sales123")
    if not User.objects.filter(username="warehouse1").exists():
        User.objects.create_user("warehouse1", "wh1@elevator.com", "wh123")
        print("  - warehouse1 / wh123")


def seed():
    create_users()
    cats = ["passenger", "freight", "panoramic", "hospital", "home"]
    names = ["Passenger", "Freight", "Panoramic", "Hospital", "Home"]
    for slug, name in zip(cats, names):
        Category.objects.get_or_create(slug=slug, defaults={"name": name + " Elevator", "sort_order": 1})

    products = [
        ("EL-P-3000", "Elite Passenger", "passenger", 2.50, 1600, 280000, True),
        ("EL-P-2000", "Classic Passenger", "passenger", 1.75, 1350, 198000, False),
        ("EL-F-5000", "Heavy Freight", "freight", 1.00, 5000, 420000, True),
        ("EL-F-3000", "Standard Freight", "freight", 0.75, 3000, 320000, False),
        ("EL-PN-1600", "Panoramic", "panoramic", 1.75, 1600, 520000, True),
        ("EL-H-2000", "Hospital", "hospital", 1.50, 2000, 380000, False),
        ("EL-HM-320", "Home Lift", "home", 0.40, 320, 128000, True),
    ]
    for model, name, ltype, speed, cap, price, feat in products:
        cat = Category.objects.get(slug=ltype)
        Product.objects.get_or_create(model_number=model, defaults={
            "category": cat, "name": name, "slug": model.lower(), "lift_type": ltype,
            "rated_speed": speed, "rated_capacity": cap, "base_price": price, "is_featured": feat,
            "sort_order": 1, "summary": name + " elevator product",
        })

    for supplier in [("Shanghai Yongda", "Wang", "13800138001"), ("Guangzhou OTIS", "Li", "13900139002")]:
        Supplier.objects.get_or_create(name=supplier[0], defaults={"contact_person": supplier[1], "phone": supplier[2]})

    Warehouse.objects.get_or_create(name="Main Warehouse", defaults={"location": "Building A"})
    Warehouse.objects.get_or_create(name="Parts Warehouse", defaults={"location": "Building B"})

    sales_user = User.objects.filter(username="sales1").first()
    for company in ["Hengda Real Estate", "Wanda Commercial"]:
        Customer.objects.get_or_create(company_name=company, defaults={
            "company_type": "developer", "contact_person": "Manager", "phone": "13800000000",
            "assigned_to": sales_user
        })

    wh = Warehouse.objects.first()
    for i, p in enumerate(Product.objects.all()):
        InventoryItem.objects.get_or_create(sku="INV-" + p.model_number, defaults={
            "product": p, "name": p.name + " (Unit)", "category": "elevator", "unit": "Unit",
            "warehouse": wh, "quantity": randint(1, 10), "min_quantity": 2,
            "cost_price": p.base_price * Decimal("0.65"), "selling_price": p.base_price
        })

    for sku, name, qty, price in [("ACC-001", "Guide Rail", 50, 350), ("ACC-002", "Steel Rope", 500, 12)]:
        InventoryItem.objects.get_or_create(sku=sku, defaults={
            "name": name, "category": "part", "unit": "Pcs", "warehouse": wh,
            "quantity": qty, "min_quantity": 10, "cost_price": price
        })

    print("Seed complete!")
    print("  Admin: admin / admin123")
    print("  Sales: sales1 / sales123")
    print("  Warehouse: warehouse1 / wh123")

if __name__ == "__main__":
    seed()
