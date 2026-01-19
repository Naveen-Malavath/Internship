import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('products');
  const [cart, setCart] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('all');

  const products = [
    { id: 1, name: 'Wireless Headphones', price: 89.99, category: 'Electronics', rating: 4.5, stock: 45, sales: 234 },
    { id: 2, name: 'Smart Watch', price: 199.99, category: 'Electronics', rating: 4.8, stock: 32, sales: 189 },
    { id: 3, name: 'Yoga Mat', price: 29.99, category: 'Sports', rating: 4.2, stock: 78, sales: 156 },
    { id: 4, name: 'Coffee Maker', price: 79.99, category: 'Home', rating: 4.6, stock: 23, sales: 98 },
    { id: 5, name: 'Running Shoes', price: 119.99, category: 'Sports', rating: 4.7, stock: 56, sales: 267 },
    { id: 6, name: 'Laptop Stand', price: 49.99, category: 'Electronics', rating: 4.3, stock: 67, sales: 145 },
  ];

  const orders = [
    { id: 1001, customer: 'John Doe', total: 289.97, status: 'Shipped', date: '2024-01-15' },
    { id: 1002, customer: 'Jane Smith', total: 119.99, status: 'Processing', date: '2024-01-16' },
    { id: 1003, customer: 'Bob Johnson', total: 449.95, status: 'Delivered', date: '2024-01-14' },
    { id: 1004, customer: 'Alice Brown', total: 79.99, status: 'Pending', date: '2024-01-17' },
  ];

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => item.id === product.id ? {...item, quantity: item.quantity + 1} : item));
    } else {
      setCart([...cart, {...product, quantity: 1}]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const filteredProducts = products.filter(product => 
    (selectedCategory === 'all' || product.category === selectedCategory) &&
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalRevenue = orders.reduce((sum, order) => sum + order.total, 0);
  const totalProducts = products.reduce((sum, product) => sum + product.stock, 0);
  const totalOrders = orders.length;
  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">E-Commerce Platform</h1>
          <div className="flex gap-2">
            <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700'}`}>Products</button>
            <button onClick={() => setCurrentPage('dashboard')} className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}>Dashboard</button>
            <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700'} relative`}>
              Cart ({cart.length})
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'products' && (
        <div className="container mx-auto p-8">
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
                <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                <p className="text-gray-400 mb-2">{product.category}</p>
                <div className="flex items-center mb-3">
                  <span className="text-yellow-400 mr-2">★ {product.rating}</span>
                  <span className="text-gray-500 text-sm">Stock: {product.stock}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                  <button onClick={() => addToCart(product)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded transition">Add to Cart</button>
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
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-gray-400 text-sm uppercase mb-2">Total Revenue</h3>
              <p className="text-3xl font-bold text-green-400">${totalRevenue.toFixed(2)}</p>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-gray-400 text-sm uppercase mb-2">Total Products</h3>
              <p className="text-3xl font-bold text-blue-400">{totalProducts}</p>
            </div>
            <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
              <h3 className="text-gray-400 text-sm uppercase mb-2">Total Orders</h3>
              <p className="text-3xl font-bold text-purple-400">{totalOrders}</p>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 shadow-lg mb-8">
            <h3 className="text-xl font-bold mb-4">Recent Orders</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4">Order ID</th>
                    <th className="text-left py-3 px-4">Customer</th>
                    <th className="text-left py-3 px-4">Total</th>
                    <th className="text-left py-3 px-4">Status</th>
                    <th className="text-left py-3 px-4">Date</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <tr key={order.id} className="border-b border-slate-700 hover:bg-slate-700">
                      <td className="py-3 px-4">#{order.id}</td>
                      <td className="py-3 px-4">{order.customer}</td>
                      <td className="py-3 px-4">${order.total}</td>
                      <td className="py-3 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs ${order.status === 'Delivered' ? 'bg-green-600' : order.status === 'Shipped' ? 'bg-blue-600' : order.status === 'Processing' ? 'bg-yellow-600' : 'bg-gray-600'}`}>
                          {order.status}
                        </span>
                      </td>
                      <td className="py-3 px-4">{order.date}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
          <div className="bg-slate-800 rounded-lg p-6 shadow-lg">
            <h3 className="text-xl font-bold mb-4">Top Selling Products</h3>
            <div className="space-y-3">
              {products.sort((a, b) => b.sales - a.sales).slice(0, 5).map(product => (
                <div key={product.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                  <span>{product.name}</span>
                  <span className="text-blue-400 font-bold">{product.sales} sales</span>
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
              <p className="text-xl text-gray-400">Your cart is empty</p>
              <button onClick={() => setCurrentPage('products')} className="mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded">Continue Shopping</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                {cart.map(item => (
                  <div key={item.id} className="bg-slate-800 rounded-lg p-6 flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-bold">{item.name}</h3>
                      <p className="text-gray-400">Quantity: {item.quantity}</p>
                      <p className="text-blue-400 font-bold mt-2">${item.price} each</p>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold mb-2">${(item.price * item.quantity).toFixed(2)}</p>
                      <button onClick={() => removeFromCart(item.id)} className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded">Remove</button>
                    </div>
                  </div>
                ))}
              </div>
              <div className="bg-slate-800 rounded-lg p-6 h-fit">
                <h3 className="text-xl font-bold mb-4">Order Summary</h3>
                <div className="space-y-3 mb-6">
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>${cartTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Shipping:</span>
                    <span>$10.00</span>
                  </div>
                  <div className="border-t border-slate-700 pt-3 flex justify-between text-xl font-bold">
                    <span>Total:</span>
                    <span className="text-blue-400">${(cartTotal + 10).toFixed(2)}</span>
                  </div>
                </div>
                <button className="w-full px-6 py-3 bg-green-600 hover:bg-green-700 rounded font-bold">Proceed to Checkout</button>
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