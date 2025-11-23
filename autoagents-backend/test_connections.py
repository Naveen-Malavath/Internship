"""Test script to verify Anthropic API and MongoDB connections."""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)
    print(f"✅ Loaded .env file from: {env_path}")
else:
    print(f"❌ .env file not found at {env_path}")
    sys.exit(1)


async def test_anthropic_api():
    """Test Anthropic API connection."""
    print("\n" + "="*60)
    print("TESTING ANTHROPIC API CONNECTION")
    print("="*60)
    
    # Check environment variables
    api_key = os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-20250514")
    
    if not api_key:
        print("❌ CLAUDE_API_KEY or ANTHROPIC_API_KEY not found in environment")
        return False
    
    print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    print(f"✅ Using model: {model}")
    
    # Test API connection
    try:
        from anthropic import AsyncAnthropic
        
        client = AsyncAnthropic(api_key=api_key)
        print("\n🔄 Testing API call...")
        
        message = await client.messages.create(
            model=model,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'Hello, AutoAgents!' in one sentence."}
            ]
        )
        
        response_text = message.content[0].text
        print(f"✅ API Response: {response_text}")
        print("\n✅ ANTHROPIC API CONNECTION SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"\n❌ ANTHROPIC API CONNECTION FAILED!")
        print(f"Error: {type(e).__name__}: {str(e)}")
        return False


async def test_mongodb_connection():
    """Test MongoDB connection."""
    print("\n" + "="*60)
    print("TESTING MONGODB CONNECTION")
    print("="*60)
    
    # Check environment variables
    mongo_uri = os.getenv("MONGO_URI") or os.getenv("MONGODB_URL")
    db_name = os.getenv("MONGO_DB_NAME") or os.getenv("MONGODB_DB_NAME")
    
    if not mongo_uri:
        print("❌ MONGO_URI or MONGODB_URL not found in environment")
        return False
    
    if not db_name:
        print("❌ MONGO_DB_NAME or MONGODB_DB_NAME not found in environment")
        return False
    
    # Mask password for display
    masked_uri = mongo_uri
    if "@" in mongo_uri and ":" in mongo_uri:
        parts = mongo_uri.split("@")
        if len(parts) == 2:
            user_pass = parts[0].split("//")[-1]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                masked_uri = mongo_uri.replace(user_pass, f"{user}:***")
    
    print(f"✅ MongoDB URI: {masked_uri}")
    print(f"✅ Database Name: {db_name}")
    
    # Test connection
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        print("\n🔄 Connecting to MongoDB...")
        
        # Adjust timeout based on connection type
        timeout_ms = 30000 if "mongodb+srv://" in mongo_uri else 5000
        client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=timeout_ms)
        
        # Test connection with ping
        await client.admin.command("ping")
        print("✅ MongoDB ping successful!")
        
        # Try to access database
        db = client[db_name]
        collections = await db.list_collection_names()
        print(f"✅ Database '{db_name}' accessible")
        print(f"✅ Collections: {collections if collections else '(empty - this is normal for a new database)'}")
        
        # Close connection
        client.close()
        
        print("\n✅ MONGODB CONNECTION SUCCESSFUL!")
        return True
        
    except Exception as e:
        print(f"\n❌ MONGODB CONNECTION FAILED!")
        print(f"Error: {type(e).__name__}: {str(e)}")
        
        # Provide helpful suggestions
        if "localhost" in mongo_uri or "127.0.0.1" in mongo_uri:
            print("\n💡 Troubleshooting for localhost:")
            print("   1. Ensure MongoDB is installed and running locally")
            print("   2. Run: net start MongoDB (Windows) or brew services start mongodb-community (Mac)")
            print("   3. Or use MongoDB Atlas by updating MONGODB_URL in .env")
        elif "mongodb+srv://" in mongo_uri:
            print("\n💡 Troubleshooting for MongoDB Atlas:")
            print("   1. Check your internet connection")
            print("   2. Verify your IP is whitelisted in MongoDB Atlas")
            print("   3. Confirm your username and password are correct")
            print("   4. Ensure your cluster is running")
        
        return False


async def main():
    """Run all connection tests."""
    print("="*60)
    print("AUTOAGENTS CONNECTION TEST")
    print("="*60)
    
    # Run tests
    anthropic_ok = await test_anthropic_api()
    mongodb_ok = await test_mongodb_connection()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Anthropic API: {'✅ PASS' if anthropic_ok else '❌ FAIL'}")
    print(f"MongoDB:       {'✅ PASS' if mongodb_ok else '❌ FAIL'}")
    print("="*60)
    
    if anthropic_ok and mongodb_ok:
        print("\n🎉 ALL CONNECTIONS SUCCESSFUL!")
        print("\nYou can now start the backend server:")
        print("  cd autoagents-backend")
        print("  .\\start_backend.ps1")
        return 0
    else:
        print("\n⚠️  SOME CONNECTIONS FAILED - Please fix the issues above")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

