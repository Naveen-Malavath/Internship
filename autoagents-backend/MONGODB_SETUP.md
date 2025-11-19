# MongoDB Setup Guide

## Problem
The application is trying to connect to MongoDB at `localhost:27017` but the connection is being refused because MongoDB is not running.

## Solution Options

### Option 1: MongoDB Atlas (Cloud - Recommended)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)
2. Create a free account and cluster
3. Get your connection string (it will look like: `mongodb+srv://username:password@cluster.mongodb.net/`)
4. Update your `.env` file:
   ```
   MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGO_DB_NAME=autoagents_db
   ```
5. Make sure to add your IP address to the Atlas whitelist (or use `0.0.0.0/0` for development)

### Option 2: Local MongoDB Installation

#### Windows Installation:

1. Download MongoDB Community Server from: https://www.mongodb.com/try/download/community
2. Run the installer and follow the setup wizard
3. MongoDB will install as a Windows service by default
4. Start MongoDB service:
   ```powershell
   # Check if service exists
   Get-Service -Name MongoDB
   
   # Start the service
   Start-Service -Name MongoDB
   ```
5. Verify it's running:
   ```powershell
   Test-NetConnection -ComputerName localhost -Port 27017
   ```

#### Alternative: Run MongoDB via Docker

If you have Docker installed:
```powershell
docker run -d -p 27017:27017 --name mongodb mongo:latest
```

### Option 3: Make MongoDB Optional (Development Only)

If you want to continue development without MongoDB, you can modify the code to handle missing MongoDB gracefully. However, this will prevent data persistence.

## Verify Connection

After setting up MongoDB, restart your FastAPI application and the connection should work.


