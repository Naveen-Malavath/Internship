import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('products');
  const [cart, setCart] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('all');

  const products = [
    { id: 1, name: 'Wireless Headphones', price: 99.99, category: 'Electronics', rating: 4.5, stock: 45, sales: 234 },
    { id: 2, name: 'Smart Watch', price: 249.99, category: 'Electronics', rating: 4.8, stock: 23, sales: 189 },
    { id: 3, name: 'Running Shoes', price: 79.99, category: 'Sports', rating: 4.3, stock: 67, sales: 312 },
    { id: 4, name: 'Yoga Mat', price: 29.99, category: 'Sports', rating: 4.6, stock: 89, sales: 421 },
    { id: 5, name: 'Coffee Maker', price: 129.99, category: 'Home', rating: 4.7, stock: 34, sales: 156 },
    { id: 6, name: 'Desk Lamp', price: 39.99, category: 'Home', rating: 4.4, stock: 56, sales: 278 }
  ];

  const orders = [
    { id: 1001, customer: 'John Doe', total: 249.99, status: 'Delivered', date: '2024-01-15' },
    { id: 1002, customer: 'Jane Smith', total: 109.98, status: 'Shipped', date: '2024-01-16' },
    { id: 1003, customer: 'Bob Johnson', total: 79.99, status: 'Processing', date: '2024-01-17' }
  ];

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const filteredProducts = products.filter(p => 
    (selectedCategory === 'all' || p.category === selectedCategory) &&
    p.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalRevenue = orders.reduce((sum, order) => sum + order.total, 0);
  const totalProducts = products.reduce((sum, p) => sum + p.stock, 0);
  const totalOrders = orders.length;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">ShopHub</h1>
          <div className="flex gap-2">
            <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700'}`}>Products</button>
            <button onClick={() => setCurrentPage('dashboard')} className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}>Dashboard</button>
            <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700'} relative`}>
              Cart
              {cart.length > 0 && <span className="absolute -top-2 -right-2 bg-red-500 text-xs rounded-full w-5 h-5 flex items-center justify-center">{cart.length}</span>}
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4">
        {currentPage === 'products' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Product Catalog</h2>
            <div className="mb-6 flex gap-4">
              <input type="text" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="flex-1 px-4 py-2 bg-slate-800 rounded border border-slate-700 focus:border-blue-500 outline-none" />
              <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="px-4 py-2 bg-slate-800 rounded border border-slate-700 outline-none">
                <option value="all">All Categories</option>
                <option value="Electronics">Electronics</option>
                <option value="Sports">Sports</option>
                <option value="Home">Home</option>
              </select>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map(product => (
                <div key={product.id} className="bg-slate-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="text-xl font-semibold">{product.name}</h3>
                    <span className="text-xs bg-slate-700 px-2 py-1 rounded">{product.category}</span>
                  </div>
                  <div className="mb-3">
                    <span className="text-yellow-400">★</span>
                    <span className="ml-1">{product.rating}</span>
                    <span className="text-slate-400 ml-2">({product.sales} sold)</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                    <button onClick={() => addToCart(product)} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700 transition">Add to Cart</button>
                  </div>
                  <div className="mt-3 text-sm text-slate-400">Stock: {product.stock} units</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentPage === 'dashboard' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 shadow-lg">
                <h3 className="text-lg font-semibold mb-2">Total Revenue</h3>
                <p className="text-3xl font-bold">${totalRevenue.toFixed(2)}</p>
              </div>
              <div className="bg-gradient-to-br from-green-600 to-green-800 rounded-lg p-6 shadow-lg">
                <h3 className="text-lg font-semibold mb-2">Total Orders</h3>
                <p className="text-3xl font-bold">{totalOrders}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-6 shadow-lg">
                <h3 className="text-lg font-semibold mb-2">Total Inventory</h3>
                <p className="text-3xl font-bold">{totalProducts}</p>
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-6">
              <h3 className="text-xl font-bold mb-4">Recent Orders</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-2">Order ID</th>
                      <th className="text-left py-3 px-2">Customer</th>
                      <th className="text-left py-3 px-2">Date</th>
                      <th className="text-left py-3 px-2">Total</th>
                      <th className="text-left py-3 px-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map(order => (
                      <tr key={order.id} className="border-b border-slate-700">
                        <td className="py-3 px-2">#{order.id}</td>
                        <td className="py-3 px-2">{order.customer}</td>
                        <td className="py-3 px-2">{order.date}</td>
                        <td className="py-3 px-2">${order.total}</td>
                        <td className="py-3 px-2">
                          <span className={`px-2 py-1 rounded text-xs ${order.status === 'Delivered' ? 'bg-green-600' : order.status === 'Shipped' ? 'bg-blue-600' : 'bg-yellow-600'}`}>{order.status}</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-xl font-bold mb-4">Top Products by Sales</h3>
              <div className="space-y-3">
                {products.sort((a, b) => b.sales - a.sales).slice(0, 5).map(product => (
                  <div key={product.id} className="flex justify-between items-center">
                    <span>{product.name}</span>
                    <div className="flex items-center gap-4">
                      <div className="w-48 bg-slate-700 rounded-full h-2">
                        <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${(product.sales / 500) * 100}%` }}></div>
                      </div>
                      <span className="text-slate-400">{product.sales}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {currentPage === 'cart' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
            {cart.length === 0 ? (
              <div className="bg-slate-800 rounded-lg p-12 text-center">
                <p className="text-xl text-slate-400">Your cart is empty</p>
                <button onClick={() => setCurrentPage('products')} className="mt-4 px-6 py-3 bg-blue-600 rounded hover:bg-blue-700 transition">Browse Products</button>
              </div>
            ) : (
              <div>
                <div className="space-y-4 mb-6">
                  {cart.map(item => (
                    <div key={item.id} className="bg-slate-800 rounded-lg p-4 flex justify-between items-center">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold">{item.name}</h3>
                        <p className="text-slate-400">Quantity: {item.quantity}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-xl font-bold">${(item.price * item.quantity).toFixed(2)}</span>
                        <button onClick={() => removeFromCart(item.id)} className="px-4 py-2 bg-red-600 rounded hover:bg-red-700 transition">Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-slate-800 rounded-lg p-6">
                  <div className="flex justify-between items-center text-2xl font-bold mb-4">
                    <span>Total:</span>
                    <span className="text-blue-400">${cart.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2)}</span>
                  </div>
                  <button className="w-full py-3 bg-green-600 rounded hover:bg-green-700 transition text-lg font-semibold">Proceed to Checkout</button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

App;

export default App;