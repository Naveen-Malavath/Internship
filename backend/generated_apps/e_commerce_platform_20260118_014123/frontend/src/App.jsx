import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('products');
  const [cart, setCart] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('all');

  const products = [
    { id: 1, name: 'Wireless Headphones', price: 79.99, category: 'Electronics', rating: 4.5, stock: 45, sales: 234 },
    { id: 2, name: 'Smart Watch', price: 199.99, category: 'Electronics', rating: 4.8, stock: 23, sales: 189 },
    { id: 3, name: 'Running Shoes', price: 89.99, category: 'Sports', rating: 4.3, stock: 67, sales: 312 },
    { id: 4, name: 'Yoga Mat', price: 29.99, category: 'Sports', rating: 4.6, stock: 89, sales: 456 },
    { id: 5, name: 'Coffee Maker', price: 149.99, category: 'Home', rating: 4.7, stock: 34, sales: 178 },
    { id: 6, name: 'Desk Lamp', price: 39.99, category: 'Home', rating: 4.4, stock: 56, sales: 267 }
  ];

  const orders = [
    { id: 1001, customer: 'John Doe', total: 279.98, status: 'Delivered', date: '2024-01-15' },
    { id: 1002, customer: 'Jane Smith', total: 89.99, status: 'Shipped', date: '2024-01-16' },
    { id: 1003, customer: 'Bob Johnson', total: 199.99, status: 'Processing', date: '2024-01-17' }
  ];

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  const removeFromCart = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const filteredProducts = products.filter(p => 
    (selectedCategory === 'all' || p.category === selectedCategory) &&
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalRevenue = products.reduce((sum, p) => sum + (p.price * p.sales), 0);
  const totalOrders = orders.length;
  const avgOrderValue = totalRevenue / totalOrders;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">ShopHub</h1>
          <div className="flex gap-2">
            <button 
              onClick={() => setCurrentPage('products')}
              className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Products
            </button>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('cart')}
              className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Cart ({cart.length})
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'products' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Product Catalog</h2>
          
          <div className="mb-6 flex gap-4">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 bg-slate-800 rounded border border-slate-700"
            />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 bg-slate-800 rounded border border-slate-700"
            >
              <option value="all">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Sports">Sports</option>
              <option value="Home">Home</option>
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map(product => (
              <div key={product.id} className="bg-slate-800 p-6 rounded-lg shadow-lg">
                <div className="mb-4">
                  <h3 className="text-xl font-semibold mb-2">{product.name}</h3>
                  <p className="text-slate-400 text-sm">{product.category}</p>
                </div>
                <div className="mb-4">
                  <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                  <div className="flex items-center mt-2">
                    <span className="text-yellow-400">★</span>
                    <span className="ml-1">{product.rating}</span>
                  </div>
                </div>
                <button
                  onClick={() => addToCart(product)}
                  className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded"
                >
                  Add to Cart
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {currentPage === 'dashboard' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 text-sm mb-2">Total Revenue</h3>
              <p className="text-3xl font-bold text-green-400">${totalRevenue.toFixed(2)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 text-sm mb-2">Total Orders</h3>
              <p className="text-3xl font-bold text-blue-400">{totalOrders}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 text-sm mb-2">Avg Order Value</h3>
              <p className="text-3xl font-bold text-purple-400">${avgOrderValue.toFixed(2)}</p>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg mb-8">
            <h3 className="text-xl font-semibold mb-4">Inventory Status</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2">Product</th>
                  <th className="text-left py-2">Category</th>
                  <th className="text-left py-2">Stock</th>
                  <th className="text-left py-2">Sales</th>
                  <th className="text-left py-2">Revenue</th>
                </tr>
              </thead>
              <tbody>
                {products.map(product => (
                  <tr key={product.id} className="border-b border-slate-700">
                    <td className="py-3">{product.name}</td>
                    <td className="py-3">{product.category}</td>
                    <td className="py-3">
                      <span className={product.stock < 30 ? 'text-red-400' : 'text-green-400'}>
                        {product.stock}
                      </span>
                    </td>
                    <td className="py-3">{product.sales}</td>
                    <td className="py-3">${(product.price * product.sales).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Recent Orders</h3>
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-2">Order ID</th>
                  <th className="text-left py-2">Customer</th>
                  <th className="text-left py-2">Total</th>
                  <th className="text-left py-2">Status</th>
                  <th className="text-left py-2">Date</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id} className="border-b border-slate-700">
                    <td className="py-3">#{order.id}</td>
                    <td className="py-3">{order.customer}</td>
                    <td className="py-3">${order.total}</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-sm ${
                        order.status === 'Delivered' ? 'bg-green-600' :
                        order.status === 'Shipped' ? 'bg-blue-600' : 'bg-yellow-600'
                      }`}>
                        {order.status}
                      </span>
                    </td>
                    <td className="py-3">{order.date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {currentPage === 'cart' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
          
          {cart.length === 0 ? (
            <div className="bg-slate-800 p-12 rounded-lg text-center">
              <p className="text-xl text-slate-400">Your cart is empty</p>
            </div>
          ) : (
            <div>
              <div className="bg-slate-800 p-6 rounded-lg mb-6">
                {cart.map((item, index) => (
                  <div key={index} className="flex justify-between items-center py-4 border-b border-slate-700">
                    <div>
                      <h3 className="font-semibold">{item.name}</h3>
                      <p className="text-slate-400">{item.category}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xl font-bold">${item.price}</span>
                      <button
                        onClick={() => removeFromCart(index)}
                        className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="flex justify-between items-center mb-4">
                  <span className="text-xl">Total:</span>
                  <span className="text-2xl font-bold text-blue-400">
                    ${cart.reduce((sum, item) => sum + item.price, 0).toFixed(2)}
                  </span>
                </div>
                <button className="w-full bg-green-600 hover:bg-green-700 py-3 rounded text-lg font-semibold">
                  Proceed to Checkout
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

App;

export default App;