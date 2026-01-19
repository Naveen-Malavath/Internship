# ShopHub - Full-Stack E-Commerce Platform

A production-ready e-commerce platform built with React, Express.js, and PostgreSQL.

## 🚀 Features

### Frontend
- **Product Catalog**: Browse and search products with filtering
- **Shopping Cart**: Add/remove items, update quantities
- **User Authentication**: Register, login, JWT-based auth
- **Checkout Flow**: Complete order placement
- **Responsive Design**: Mobile-friendly UI
- **State Management**: Context API for cart and auth

### Backend
- **RESTful API**: Express.js with proper routing
- **Authentication**: JWT tokens with bcrypt password hashing
- **CRUD Operations**: Products, orders, users management
- **Input Validation**: Request validation middleware
- **Error Handling**: Centralized error handling
- **Security**: CORS, helmet, rate limiting

### Database
- **PostgreSQL**: Relational database with proper schema
- **Foreign Keys**: Referential integrity
- **Indexes**: Optimized queries
- **Seed Data**: Sample products and users

## 📋 Prerequisites

- Node.js (v16 or higher)
- Docker & Docker Compose
- npm or yarn

## 🛠️ Installation

### Option 1: Using Docker (Recommended)

1. Clone the repository:
```bash
cd shophub
```

2. Start all services:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- PostgreSQL: localhost:5432

### Option 2: Manual Setup

#### Database Setup
```bash
# Start PostgreSQL (Docker)
docker run --name shophub-db -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=shophub -p 5432:5432 -d postgres:15

# Run migrations
cd database
psql -h localhost -U postgres -d shophub -f schema.sql
psql -h localhost -U postgres -d shophub -f seed.sql
```

#### Backend Setup
```bash
cd backend
npm install
cp .env.example .env
# Edit .env with your database credentials
npm run dev
```

#### Frontend Setup
```bash
cd frontend
npm install
npm start
```

## 🔐 Environment Variables

### Backend (.env)
```
PORT=5000
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/shophub
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRES_IN=7d
NODE_ENV=development
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:5000/api
```

## 📚 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user (protected)

### Products
- `GET /api/products` - Get all products (with search/filter)
- `GET /api/products/:id` - Get single product
- `POST /api/products` - Create product (admin)
- `PUT /api/products/:id` - Update product (admin)
- `DELETE /api/products/:id` - Delete product (admin)

### Orders
- `GET /api/orders` - Get user orders (protected)
- `GET /api/orders/:id` - Get single order (protected)
- `POST /api/orders` - Create order (protected)
- `PUT /api/orders/:id` - Update order status (admin)

### Users
- `GET /api/users/profile` - Get user profile (protected)
- `PUT /api/users/profile` - Update user profile (protected)

## 🧪 Testing

### Backend Tests
```bash
cd backend
npm test
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 🏗️ Project Structure

```
shophub/
├── frontend/              # React application
│   ├── src/
│   │   ├── components/    # Reusable components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   ├── context/       # React Context
│   │   ├── styles/        # CSS styles
│   │   └── App.jsx        # Main app component
│   └── package.json
├── backend/               # Express API
│   ├── src/
│   │   ├── routes/        # API routes
│   │   ├── models/        # Database models
│   │   ├── middleware/    # Custom middleware
│   │   ├── controllers/   # Route controllers
│   │   ├── config/        # Configuration
│   │   └── server.js      # Entry point
│   └── package.json
├── database/              # Database files
│   ├── schema.sql         # Database schema
│   └── seed.sql           # Seed data
├── docker-compose.yml     # Docker configuration
└── README.md
```

## 🚢 Deployment

### Using Docker
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
1. Set production environment variables
2. Build frontend: `cd frontend && npm run build`
3. Serve frontend build with nginx or serve
4. Start backend: `cd backend && npm start`

## 🔒 Security Features

- JWT authentication
- Password hashing with bcrypt
- CORS configuration
- Helmet.js security headers
- Rate limiting
- SQL injection prevention
- XSS protection

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 👥 Default Users (Seed Data)

### Admin User
- Email: admin@shophub.com
- Password: admin123

### Regular User
- Email: user@shophub.com
- Password: user123

## 🐛 Known Issues

None at the moment. Please report issues on GitHub.

## 📞 Support

For support, email support@shophub.com or open an issue on GitHub.

## 🎯 Roadmap

- [ ] Payment gateway integration (Stripe)
- [ ] Product reviews and ratings
- [ ] Wishlist functionality
- [ ] Email notifications
- [ ] Admin dashboard
- [ ] Product categories
- [ ] Inventory management
- [ ] Order tracking
- [ ] Coupon codes
- [ ] Multi-language support

---

Made with ❤️ by the ShopHub Team
