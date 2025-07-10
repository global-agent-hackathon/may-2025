from typing import List, Dict, Any
import json
from bson import json_util, ObjectId
from pymongo import MongoClient
import razorpay
from dotenv import load_dotenv
import os
from datetime import datetime
from agno.agent import Agent

load_dotenv()

razorpay_client = razorpay.Client(auth=(
    os.getenv('RAZORPAY_KEY_ID'),
    os.getenv('RAZORPAY_KEY_SECRET')
))

MONGO_URI = os.getenv('MONGODB_URI')

def get_mongo_client():
    return MongoClient(MONGO_URI)

def get_products() -> str:
    """
    Use this function to get all products from MongoDB collection.

    Returns:
        str: JSON string of products.
    """
    client = get_mongo_client()
    db = client['kippr']
    collection = db['products']

    products = list(collection.find())
    client.close()
    
    return json.dumps(products, default=json_util.default)

def get_product(product_id: str) -> str:
    """
    Use this function to get a specific product by its ID from MongoDB collection.

    Args:
        product_id (str): The ID of the product to retrieve.

    Returns:
        str: JSON string of the product. Returns empty object if product not found.
    """
    client = get_mongo_client()
    db = client['kippr']
    collection = db['products']

    try:
        product = collection.find_one({"_id": ObjectId(product_id)})
        if product is None:
            return json.dumps({})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        client.close()
    
    return json.dumps(product, default=json_util.default)

def get_orders(agent: Agent) -> str:
    """
    Use this function to get all orders for a specific user from MongoDB collection.

    Returns:
        str: JSON string of the user's orders. Returns empty array if no orders found.
    """
    client = get_mongo_client()
    db = client['kippr']
    collection = db['orders']

    user_id = agent.user_id

    try:
        orders = list(collection.find({"userId": user_id}))  # Note: userId is now a string
        if not orders:
            return json.dumps([])
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        client.close()
    
    return json.dumps(orders, default=json_util.default)

def get_order(agent: Agent, order_id: str) -> str:
    """
    Use this function to get a specific order for a user from MongoDB collection.

    Args:
        order_id (str): The ID of the order to retrieve.

    Returns:
        str: JSON string of the order. Returns empty object if order not found.
    """
    client = get_mongo_client()
    db = client['kippr']
    collection = db['orders']

    user_id = agent.user_id

    try:
        order = collection.find_one({
            "_id": ObjectId(order_id),
            "userId": user_id
        })
        if order is None:
            return json.dumps({})
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        client.close()
    
    return json.dumps(order, default=json_util.default)

def create_order(agent: Agent, products: List[Dict[str, Any]], customer: Dict[str, str]) -> str:
    """
    Use this tool to create an order.

    Args:
        products (List[Dict[str, Any]]): List of products with their IDs and quantities.
            Each product in the list should be a dictionary with the following structure:
            {
                "productId": str,  # The ID of the product
                "quantity": int    # The quantity of the product (must be > 0)
            }
        customer (Dict[str, str]): Customer information with the following structure:
            {
                "name": str,   # Customer's full name
                "email": str   # Customer's email address
            }

    Returns:
        str: JSON string containing order details and Razorpay payment link URL.
    """
    client = get_mongo_client()
    try:
        db = client['kippr']
        products_collection = db['products']
        orders_collection = db['orders']

        user_id = agent.user_id

        total_amount = 0
        order_items = []
        
        for item in products:
            product_id = item.get('productId')
            quantity = item.get('quantity', 1)
            
            if not product_id or not isinstance(quantity, int) or quantity <= 0:
                return json.dumps({"error": "Invalid product data"})
            
            product = products_collection.find_one({"_id": ObjectId(product_id)})
            if not product:
                return json.dumps({"error": f"Product not found: {product_id}"})
            
            if product.get('stock', 0) < quantity:
                return json.dumps({"error": f"Insufficient stock for product: {product_id}"})
            
            item_total = product.get('price', 0) * quantity
            total_amount += item_total
            
            order_items.append({
                "productId": ObjectId(product_id),
                "quantity": quantity,
                "price": product.get('price', 0),
                "total": item_total,
                "name": product.get('name', '')
            })

        payment_data = {
            "amount": total_amount * 100,
            "currency": "INR",
            "accept_partial": False,
            "description": "Order Payment",
            "customer": {
                "name": customer['name'],
                "email": customer['email']
            },
            "notify": {
                "email": True
            },
            "reminder_enable": True,
            "notes": {
                "userId": user_id
            }
        }
        
        payment_link = razorpay_client.payment_link.create(data=payment_data)

        order_data = {
            "userId": user_id,
            "customer": {
                "name": customer['name'],
                "email": customer['email']
            },
            "items": order_items,
            "totalAmount": total_amount,
            "status": "pending",
            "paymentLinkId": payment_link['id'],
            "paymentLink": payment_link['short_url'],
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow()
        }
        
        order_result = orders_collection.insert_one(order_data)

        for item in products:
            products_collection.update_one(
                {"_id": ObjectId(item['productId'])},
                {"$inc": {"stock": -item['quantity']}}
            )

        created_order = orders_collection.find_one({"_id": order_result.inserted_id})
        return json.dumps(created_order, default=json_util.default)

    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        client.close()
