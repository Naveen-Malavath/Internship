import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('products');
  const [cart, setCart] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('all');

  const products = [
    { id: 1, name: 'Wireless Headphones', price: 79.99, category: 'Electronics', rating: 4.5, stock: 45, sales: 234 },
    { id: 2, name: 'Running Shoes', price: 129.99, category: 'Footwear', rating: 4.8, stock: 32, sales: 189 },
    { id: 3, name: 'Coffee Maker', price: 49.99, category: 'Home', rating: 4.2, stock: 67, sales: 156 },
    { id: 4, name: 'Laptop Stand', price: 34.99, category: 'Electronics', rating: 4.6, stock: 89, sales: 312 },
    { id: 5, name: 'Yoga Mat', price: 24.99, category: 'Sports', rating: 4.4, stock: 120, sales: 278 },
    { id: 6, name: 'Water Bottle', price: 19.99, category: 'Sports', rating: 4.7, stock: 200, sales: 445 }
  ];

  const orders = [
    { id: 1001, customer: 'John Smith', total: 159.98, status: 'Delivered', date: '2024-01-15' },
    { id: 1002, customer: 'Sarah Johnson', total: 79.99, status: 'Shipped', date: '2024-01-18' },
    { id: 1003, customer: 'Mike Davis', total: 204.97, status: 'Processing', date: '2024-01-20' },
    { id: 1004, customer: 'Emily Brown', total: 49.99, status: 'Delivered', date: '2024-01-19' }
  ];

  const addToCart = (product) => {
    setCart([...cart, product]);
  };

  const removeFromCart = (index) => {
    setCart(cart.filter((_, i) => i !== index));
  };

  const filteredProducts = products.filter(p => 
    (selectedCategory === 'all' || p.category === selectedCategory) &&
    (p.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const totalRevenue = orders.reduce((sum, order) => sum + order.total, 0);
  const totalSales = products.reduce((sum, p) => sum + p.sales, 0);
  const avgRating = (products.reduce((sum, p) => sum + p.rating, 0) / products.length).toFixed(1);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">ShopHub</h1>
          <div className="flex gap-2">
            <button 
              onClick={() => setCurrentPage('products')}
              className={`px-4 py-2 rounded transition ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Products
            </button>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('cart')}
              className={`px-4 py-2 rounded transition ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Cart ({cart.length})
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'products' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Product Catalog</h2>
          
          <div className="flex gap-4 mb-6">
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="flex-1 px-4 py-2 bg-slate-800 rounded border border-slate-700 focus:border-blue-500 outline-none"
            />
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-4 py-2 bg-slate-800 rounded border border-slate-700 outline-none"
            >
              <option value="all">All Categories</option>
              <option value="Electronics">Electronics</option>
              <option value="Footwear">Footwear</option>
              <option value="Home">Home</option>
              <option value="Sports">Sports</option>
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map(product => (
              <div key={product.id} className="bg-slate-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold">{product.name}</h3>
                  <span className="text-sm bg-slate-700 px-2 py-1 rounded">{product.category}</span>
                </div>
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-yellow-400">★</span>
                    <span>{product.rating}</span>
                    <span className="text-slate-400 text-sm">({product.sales} sold)</span>
                  </div>
                  <p className="text-slate-400 text-sm">Stock: {product.stock} units</p>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                  <button
                    onClick={() => addToCart(product)}
                    className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition"
                  >
                    Add to Cart
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {currentPage === 'dashboard' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-lg font-semibold mb-2">Total Revenue</h3>
              <p className="text-4xl font-bold">${totalRevenue.toFixed(2)}</p>
            </div>
            <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-lg font-semibold mb-2">Total Sales</h3>
              <p className="text-4xl font-bold">{totalSales}</p>
            </div>
            <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-lg font-semibold mb-2">Avg Rating</h3>
              <p className="text-4xl font-bold">{avgRating} ★</p>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-8">
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

          <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-semibold mb-4">Inventory Overview</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {products.map(product => (
                <div key={product.id} className="flex justify-between items-center p-4 bg-slate-700 rounded">
                  <div>
                    <p className="font-semibold">{product.name}</p>
                    <p className="text-sm text-slate-400">Stock: {product.stock} units</p>
                  </div>
                  <div className="text-right">
                    <p className="font-bold text-blue-400">${product.price}</p>
                    <p className="text-sm text-slate-400">{product.sales} sales</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'cart' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
          
          {cart.length === 0 ? (
            <div className="bg-slate-800 rounded-lg p-12 text-center">
              <p className="text-xl text-slate-400">Your cart is empty</p>
              <button
                onClick={() => setCurrentPage('products')}
                className="mt-4 px-6 py-3 bg-blue-600 rounded hover:bg-blue-700 transition"
              >
                Continue Shopping
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2">
                {cart.map((item, index) => (
                  <div key={index} className="bg-slate-800 rounded-lg p-6 mb-4 flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-semibold">{item.name}</h3>
                      <p className="text-slate-400">{item.category}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-2xl font-bold text-blue-400">${item.price}</span>
                      <button
                        onClick={() => removeFromCart(index)}
                        className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="bg-slate-800 rounded-lg p-6 h-fit">
                <h3 className="text-xl font-semibold mb-4">Order Summary</h3>
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>${cart.reduce((sum, item) => sum + item.price, 0).toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Shipping:</span>
                    <span>$9.99</span>
                  </div>
                  <div className="border-t border-slate-700 pt-2 mt-2">
                    <div className="flex justify-between text-xl font-bold">
                      <span>Total:</span>
                      <span className="text-blue-400">${(cart.reduce((sum, item) => sum + item.price, 0) + 9.99).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
                <button className="w-full py-3 bg-green-600 rounded hover:bg-green-700 transition font-semibold">
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