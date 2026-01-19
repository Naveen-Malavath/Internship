# ShopHub Backend API

Express.js REST API for the ShopHub e-commerce platform.

## Features

- JWT Authentication
- User Management
- Product CRUD Operations
- Order Management
- Shopping Cart
- Input Validation
- Error Handling Middleware
- Security Headers (Helmet)
- CORS Configuration

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (protected)

### Products
- `GET /api/products` - Get all products (with search & pagination)
- `GET /api/products/:id` - Get single product
- `POST /api/products` - Create product (admin only)
- `PUT /api/products/:id` - Update product (admin only)
- `DELETE /api/products/:id` - Delete product (admin only)

### Orders
- `GET /api/orders` - Get user orders (protected)
- `GET /api/orders/:id` - Get single order (protected)
- `POST /api/orders` - Create order (protected)
- `PUT /api/orders/:id/status` - Update order status (admin only)

### Users
- `GET /api/users/profile` - Get user profile (protected)
- `PUT /api/users/profile` - Update user profile (protected)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```
PORT=5000
DATABASE_URL=postgresql://shophub:shophub123@localhost:5432/shophub
JWT_SECRET=your_jwt_secret_key_here
JWT_EXPIRE=7d
NODE_ENV=development
```

3. Run the server:
```bash
npm run dev
```

## Environment Variables

- `PORT` - Server port (default: 5000)
- `DATABASE_URL` - PostgreSQL connection string
- `JWT_SECRET` - Secret key for JWT tokens
- `JWT_EXPIRE` - JWT token expiration time
- `NODE_ENV` - Environment (development/production)
