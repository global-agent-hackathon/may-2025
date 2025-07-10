from pymongo import MongoClient
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get MongoDB URI from environment variables
MONGODB_URI = os.getenv('MONGODB_URI')

# Connect to MongoDB
client = MongoClient(MONGODB_URI)
db = client['kippr']
products_collection = db['products']

# List of products
products = [
    {
        "name": "Almonds Pack",
        "description": "Premium quality raw almonds rich in protein and fiber. Net weight: 100g.",
        "price": 129,
        "image": "https://example.com/images/almonds.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Cashew Nuts Pack",
        "description": "Whole raw cashew nuts, naturally sweet and creamy. Net weight: 100g.",
        "price": 139,
        "image": "https://example.com/images/cashews.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Walnuts Pack",
        "description": "Fresh raw walnut halves, packed with Omega-3. Net weight: 100g.",
        "price": 159,
        "image": "https://example.com/images/walnuts.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Pistachios Pack",
        "description": "Natural shelled pistachios – rich in nutrients & low in calories. Net weight: 100g.",
        "price": 149,
        "image": "https://example.com/images/pistachios.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Raisins Pack",
        "description": "Naturally sweet raisins, perfect for snacking and baking. Net weight: 100g.",
        "price": 89,
        "image": "https://example.com/images/raisins.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Mixed Dry Fruits Pack",
        "description": "Healthy mix of almonds, cashews, pistachios, walnuts, and raisins. Net weight: 250g.",
        "price": 279,
        "image": "https://example.com/images/mixed.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Cut Apple Pack",
        "description": "Freshly cut apple slices, ready to eat. Great for snacking on the go. Net weight: 150g.",
        "price": 79,
        "image": "https://example.com/images/apple.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Cut Papaya Pack",
        "description": "Ripe and juicy papaya cubes, full of fiber and antioxidants. Net weight: 200g.",
        "price": 69,
        "image": "https://example.com/images/papaya.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Cut Watermelon Pack",
        "description": "Hydrating and sweet watermelon chunks. Net weight: 250g.",
        "price": 59,
        "image": "https://example.com/images/watermelon.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Cut Pineapple Pack",
        "description": "Fresh golden pineapple cubes – sweet and tangy. Net weight: 200g.",
        "price": 69,
        "image": "https://example.com/images/pineapple.png",
        "stock": 100,
        "currency": "INR"
    },
    {
        "name": "Fruit Combo Pack",
        "description": "A colorful mix of apple, papaya, watermelon & pineapple slices. Net weight: 300g.",
        "price": 129,
        "image": "https://example.com/images/fruit-mix.png",
        "stock": 100,
        "currency": "INR"
    }
]

# Insert all products into the MongoDB collection
result = products_collection.insert_many(products)
print(f"Inserted {len(result.inserted_ids)} products into MongoDB.")

# Close the connection
client.close()