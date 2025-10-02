"""
Seed script to populate database with sample data
Run this once: python seed_data.py
"""
import requests
from datetime import datetime, timedelta
import random

BASE_URL = "http://127.0.0.1:8000"

# Sample users
USERS = [
    {
        "email": "alice@example.com",
        "password": "alice123",
        "full_name": "Alice Johnson"
    },
    {
        "email": "bob@example.com",
        "password": "smithysmudge",
        "full_name": "Bob Smith"
    },
    {
        "email": "charlie@example.com",
        "password": "charlie123",
        "full_name": "Charlie Davis"
    },
    {
        "email": "diana@example.com",
        "password": "diana123",
        "full_name": "Diana Martinez"
    },
    {
        "email": "eve@example.com",
        "password": "eve123456",
        "full_name": "Eve Wilson"
    }
]

# Transaction templates
INCOME_CATEGORIES = [
    {"category": "Salary", "amount_range": (3000, 6000)},
    {"category": "Freelance", "amount_range": (500, 2000)},
    {"category": "Investment", "amount_range": (100, 1000)},
    {"category": "Bonus", "amount_range": (500, 2000)},
]

EXPENSE_CATEGORIES = [
    {"category": "Rent", "amount_range": (800, 1500)},
    {"category": "Food", "amount_range": (200, 600)},
    {"category": "Transport", "amount_range": (50, 200)},
    {"category": "Entertainment", "amount_range": (50, 300)},
    {"category": "Utilities", "amount_range": (100, 300)},
    {"category": "Shopping", "amount_range": (100, 500)},
    {"category": "Healthcare", "amount_range": (50, 400)},
]

def register_user(user):
    """Register a new user"""
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=user)
        if response.status_code == 201:
            print(f"Registered: {user['email']}")
            return True
        elif response.status_code == 400:
            print(f"Already exists: {user['email']}")
            return True
        else:
            print(f"Failed to register {user['email']}: {response.text}")
            return False
    except Exception as e:
        print(f"Error registering {user['email']}: {e}")
        return False

def login_user(email, password):
    """Login and get access token"""
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": email, "password": password}
        )
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"Logged in: {email}")
            return token
        else:
            print(f"Failed to login {email}: {response.text}")
            return None
    except Exception as e:
        print(f"Error logging in {email}: {e}")
        return None

def create_transaction(token, transaction):
    """Create a transaction for user"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(
            f"{BASE_URL}/transactions/",
            json=transaction,
            headers=headers
        )
        if response.status_code == 201:
            return True
        else:
            print(f"Failed to create transaction: {response.text}")
            return False
    except Exception as e:
        print(f"Error creating transaction: {e}")
        return False

def generate_transactions(num_transactions=10):
    """Generate random transactions for the last 30 days"""
    transactions = []
    base_date = datetime.now()
    
    # Generate 2-3 income transactions
    for _ in range(random.randint(2, 3)):
        income_cat = random.choice(INCOME_CATEGORIES)
        amount = round(random.uniform(*income_cat["amount_range"]), 2)
        days_ago = random.randint(1, 30)
        
        transactions.append({
            "amount": amount,
            "type": "income",
            "category": income_cat["category"],
            "description": f"{income_cat['category']} payment",
            "date": (base_date - timedelta(days=days_ago)).isoformat()
        })
    
    # Generate 7-12 expense transactions
    for _ in range(random.randint(5, 10)):
        expense_cat = random.choice(EXPENSE_CATEGORIES)
        amount = round(random.uniform(*expense_cat["amount_range"]), 2)
        days_ago = random.randint(1, 30)
        
        transactions.append({
            "amount": amount,
            "type": "expense",
            "category": expense_cat["category"],
            "description": f"{expense_cat['category']} expense",
            "date": (base_date - timedelta(days=days_ago)).isoformat()
        })
    
    return transactions

def seed_database():
    """Main function to seed the database"""
    print("=" * 50)
    print("Starting Database Seeding...")
    print("=" * 50)
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health")
        print("Server is running\n")
    except:
        print("Server is not running! Start it with: uvicorn app.main:app --reload")
        return
    
    # Register all users
    print("\nRegistering Users...")
    print("-" * 50)
    for user in USERS:
        register_user(user)
    
    # Create transactions for each user
    print("\nCreating Transactions.....")
    print("-" * 50)
    
    for user in USERS:
        print(f"\n👤 User: {user['email']}")
        
        # Login
        token = login_user(user["email"], user["password"])
        if not token:
            continue
        
        # Generate and create transactions
        transactions = generate_transactions()
        success_count = 0
        
        for transaction in transactions:
            if create_transaction(token, transaction):
                success_count += 1
        
        print(f"Created {success_count}/{len(transactions)} transactions")
    
    print("\n" + "=" * 50)
    print("-------- Database Seeding Complete! --------")
    print("=" * 50)
    print("\nSummary:")
    print(f" Users created: {len(USERS)}")
    print(f" Transactions per user: ~10-15")
    print("\nLogin Credentials:")
    for user in USERS:
        print(f"   • {user['email']} / {user['password']}")
    print("\nTest in Swagger: http://127.0.0.1:8000/docs")
    print("=" * 50)

if __name__ == "__main__":
    seed_database()