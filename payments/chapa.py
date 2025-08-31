import requests
import json
import hashlib
import hmac
import os
from datetime import datetime
from typing import Dict, Optional, Any

class ChapaPayment:
    """Chapa.co payment integration class"""
    
    def __init__(self):
        self.base_url = "https://api.chapa.co/v1"
        self.secret_key = os.getenv("CHAPA_SECRET_KEY")
        self.webhook_secret = os.getenv("CHAPA_WEBHOOK_SECRET")
        
        if not self.secret_key:
            raise ValueError("CHAPA_SECRET_KEY environment variable is required")
    
    def create_payment(self, 
                      amount: float, 
                      currency: str = "USD",
                      email: str = None,
                      first_name: str = None,
                      last_name: str = None,
                      tx_ref: str = None,
                      callback_url: str = None,
                      return_url: str = None,
                      customizations: Dict[str, str] = None) -> Dict[str, Any]:
        """
        Create a new payment transaction
        
        Args:
            amount: Payment amount
            currency: Currency code (USD, EUR, ETB, etc.)
            email: Customer email
            first_name: Customer first name
            last_name: Customer last name
            tx_ref: Unique transaction reference
            callback_url: Webhook URL for payment updates
            return_url: URL to redirect after payment
            customizations: Custom title and description
            
        Returns:
            Dictionary containing payment response
        """
        
        if not tx_ref:
            tx_ref = f"tx_ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(str(datetime.now())) % 10000}"
        
        payload = {
            "amount": str(amount),
            "currency": currency,
            "email": email,
            "first_name": first_name,
            "last_name": last_name,
            "tx_ref": tx_ref,
            "callback_url": callback_url,
            "return_url": return_url
        }
        
        if customizations:
            payload.update(customizations)
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/transaction/initialize",
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "checkout_url": result["data"]["checkout_url"],
                    "tx_ref": tx_ref,
                    "amount": amount,
                    "currency": currency
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "Payment initialization failed")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def verify_payment(self, tx_ref: str) -> Dict[str, Any]:
        """
        Verify a payment transaction
        
        Args:
            tx_ref: Transaction reference to verify
            
        Returns:
            Dictionary containing verification result
        """
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/transaction/verify/{tx_ref}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") == "success":
                payment_data = result["data"]
                return {
                    "status": "success",
                    "verified": True,
                    "amount": payment_data.get("amount"),
                    "currency": payment_data.get("currency"),
                    "status": payment_data.get("status"),
                    "email": payment_data.get("email"),
                    "first_name": payment_data.get("first_name"),
                    "last_name": payment_data.get("last_name"),
                    "created_at": payment_data.get("created_at")
                }
            else:
                return {
                    "status": "error",
                    "verified": False,
                    "message": result.get("message", "Verification failed")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "verified": False,
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "verified": False,
                "message": f"Unexpected error: {str(e)}"
            }
    
    def get_banks(self, country: str = "ET") -> Dict[str, Any]:
        """
        Get list of banks for a specific country
        
        Args:
            country: Country code (ET for Ethiopia, NG for Nigeria, etc.)
            
        Returns:
            Dictionary containing list of banks
        """
        
        headers = {
            "Authorization": f"Bearer {self.secret_key}"
        }
        
        try:
            response = requests.get(
                f"{self.base_url}/banks?country={country}",
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("status") == "success":
                return {
                    "status": "success",
                    "banks": result.get("data", [])
                }
            else:
                return {
                    "status": "error",
                    "message": result.get("message", "Failed to fetch banks")
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"Network error: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
    
    def verify_webhook(self, payload: str, signature: str) -> bool:
        """
        Verify webhook signature for security
        
        Args:
            payload: Raw webhook payload
            signature: Webhook signature header
            
        Returns:
            True if signature is valid, False otherwise
        """
        
        if not self.webhook_secret:
            return False
        
        expected_signature = hmac.new(
            self.webhook_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(expected_signature, signature)
    
    def process_webhook(self, payload: Dict[str, Any], signature: str) -> Dict[str, Any]:
        """
        Process incoming webhook from Chapa
        
        Args:
            payload: Webhook payload data
            signature: Webhook signature for verification
            
        Returns:
            Dictionary containing webhook processing result
        """
        
        # Verify webhook signature
        if not self.verify_webhook(json.dumps(payload), signature):
            return {
                "status": "error",
                "message": "Invalid webhook signature"
            }
        
        # Extract payment information
        tx_ref = payload.get("tx_ref")
        status = payload.get("status")
        amount = payload.get("amount")
        currency = payload.get("currency")
        
        if not tx_ref:
            return {
                "status": "error",
                "message": "Missing transaction reference"
            }
        
        # Process based on payment status
        if status == "success":
            # Payment successful - update your database
            return {
                "status": "success",
                "message": "Payment processed successfully",
                "tx_ref": tx_ref,
                "amount": amount,
                "currency": currency,
                "action": "payment_success"
            }
        elif status == "failed":
            # Payment failed
            return {
                "status": "success",
                "message": "Payment failed",
                "tx_ref": tx_ref,
                "action": "payment_failed"
            }
        else:
            # Other statuses
            return {
                "status": "success",
                "message": f"Payment status: {status}",
                "tx_ref": tx_ref,
                "action": "status_update"
            }

# Convenience function for backward compatibility
def process_payment(amount: float, currency: str = "USD", **kwargs) -> Dict[str, Any]:
    """Legacy function for backward compatibility"""
    try:
        chapa = ChapaPayment()
        return chapa.create_payment(amount, currency, **kwargs)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Payment initialization failed: {str(e)}"
        }
