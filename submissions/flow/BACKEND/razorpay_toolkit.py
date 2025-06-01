from datetime import datetime
from agno.tools import Toolkit
import base64
import requests
from typing import Dict, Optional
import json

class RazorpayPaymentLink(Toolkit):
    def __init__(self):
        super().__init__(name="razorpay_toolkit")
        self.register(self.generate_payment_link)

    def _get_auth(self, api_key: str, api_secret: str) -> str:
        auth = f"{api_key}:{api_secret}"
        return "Basic " + base64.b64encode(auth.encode()).decode()

    # ⛔ REMOVE async here - requests is not async
    def generate_payment_link(
        self,
        api_key: str,
        api_secret: str,
        description: str,
        customer_name: str,
        customer_email: str,
        amount: Optional[int] = None,
        currency: Optional[str] = "INR"
    ) -> str:  # ✅ return a string, not a dict
        """Generate Razorpay payment link with dynamic credentials"""
        payload = {
            "amount": int((amount or 10)),  # Convert to paise
            "currency": currency,
            "description": description,
            "customer": {
                "name": customer_name,
                "email": customer_email
            }
        }
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._get_auth(api_key, api_secret)
        }

        try:
            response = requests.post(
                "https://api.razorpay.com/v1/payment_links",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()

            # ✅ Return only short_url directly
            return data["short_url"]

        except Exception as e:
            # ✅ In case of error, raise it properly so agent catches
            raise Exception(f"Razorpay API failed: {str(e)}")

        

class RazorpayTrackerToolkit(Toolkit):
    def __init__(self):
        super().__init__(name="razorpay_tracker_toolkit")
        self.register(self.get_payment_links)

    def _get_auth(self, api_key: str, api_secret: str) -> str:
        """Generate Basic Auth header"""
        auth = f"{api_key}:{api_secret}"
        return "Basic " + base64.b64encode(auth.encode()).decode()

    def get_payment_links(
        self,
        api_key: str,
        api_secret: str,
        limit: Optional[int] = 10,
        status: Optional[str] = None
    ) -> str:
        """Fetch payment links from Razorpay API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": self._get_auth(api_key, api_secret)
        }
        
        params = {"count": min(limit, 100)}
        if status:
            params["status"] = status

        try:
            response = requests.get(
                "https://api.razorpay.com/v1/payment_links",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            # Process and simplify the response
            payment_links = data.get("payment_links", [])
            simplified_links = [
                {
                    "id": link["id"],
                    "description": link["description"],
                    "amount": link["amount"] / 100,  # convert paise to INR
                    "customer_name": link["customer"].get("name"),
                    "customer_email": link["customer"].get("email"),
                    "customer_contact": link["customer"].get("contact"),
                    "status": link["status"],
                    "short_url": link["short_url"]
                }
                for link in payment_links
            ]
            
            return json.dumps({"payment_links": simplified_links})
        except requests.RequestException as e:
            return json.dumps({"error": str(e)})