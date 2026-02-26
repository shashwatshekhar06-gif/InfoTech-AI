"""
Razorpay Payment Integration for InfoFetch AI
"""
import razorpay
import os
import hashlib
import hmac
from typing import Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv("api.env")

# Razorpay configuration
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_YOUR_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "YOUR_KEY_SECRET")

# Initialize Razorpay client
try:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
    RAZORPAY_AVAILABLE = True
    print("✅ Razorpay client initialized successfully")
except Exception as e:
    razorpay_client = None
    RAZORPAY_AVAILABLE = False
    print(f"⚠️ Razorpay initialization failed: {e}")

# Plan pricing (in paise - INR smallest unit)
PLAN_PRICING = {
    'Plus': {
        'amount': 1900,  # ₹19.00
        'currency': 'INR',
        'display': '₹19/month'
    },
    'Premium': {
        'amount': 4900,  # ₹49.00
        'currency': 'INR',
        'display': '₹49/month'
    }
}

def create_razorpay_order(plan_name: str, user_id: int, username: str) -> Optional[Dict]:
    """
    Create a Razorpay order for payment
    
    Args:
        plan_name: Name of the plan (Plus/Premium)
        user_id: User's database ID
        username: User's username
        
    Returns:
        Dict with order details or None if failed
    """
    if not RAZORPAY_AVAILABLE or razorpay_client is None:
        print("❌ Razorpay client not available")
        return None
    
    if plan_name not in PLAN_PRICING:
        print(f"❌ Invalid plan name: {plan_name}")
        return None
    
    plan_info = PLAN_PRICING[plan_name]
    
    try:
        # Create Razorpay order
        order_data = {
            'amount': plan_info['amount'],
            'currency': plan_info['currency'],
            'receipt': f'order_{user_id}_{plan_name}',
            'notes': {
                'user_id': str(user_id),
                'username': username,
                'plan': plan_name
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        print(f"✅ Razorpay order created: {order['id']}")
        
        return {
            'order_id': order['id'],
            'amount': plan_info['amount'],
            'currency': plan_info['currency'],
            'key_id': RAZORPAY_KEY_ID,
            'plan_name': plan_name,
            'display_amount': plan_info['display']
        }
        
    except Exception as e:
        print(f"❌ Error creating Razorpay order: {e}")
        return None

def verify_razorpay_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """
    Verify Razorpay payment signature for security
    
    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Razorpay signature
        
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        # Create the message to verify
        message = f"{order_id}|{payment_id}"
        
        # Generate HMAC SHA256 signature
        generated_signature = hmac.new(
            RAZORPAY_KEY_SECRET.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        is_valid = hmac.compare_digest(generated_signature, signature)
        
        if is_valid:
            print(f"✅ Payment signature verified for order: {order_id}")
        else:
            print(f"❌ Invalid payment signature for order: {order_id}")
        
        return is_valid
        
    except Exception as e:
        print(f"❌ Error verifying signature: {e}")
        return False

def get_payment_details(payment_id: str) -> Optional[Dict]:
    """
    Fetch payment details from Razorpay
    
    Args:
        payment_id: Razorpay payment ID
        
    Returns:
        Dict with payment details or None if failed
    """
    if not RAZORPAY_AVAILABLE or razorpay_client is None:
        return None
    
    try:
        payment = razorpay_client.payment.fetch(payment_id)
        return payment
    except Exception as e:
        print(f"❌ Error fetching payment details: {e}")
        return None

# Test configuration on import
if __name__ == "__main__":
    print("\n" + "="*70)
    print("🧪 TESTING RAZORPAY CONFIGURATION")
    print("="*70)
    print(f"Key ID: {RAZORPAY_KEY_ID[:20]}..." if len(RAZORPAY_KEY_ID) > 20 else RAZORPAY_KEY_ID)
    print(f"Client Available: {RAZORPAY_AVAILABLE}")
    print("="*70 + "\n")