import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('products');
  const [cart, setCart] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('all');

  const products = [
    { id: 1, name: 'Wireless Headphones', price: 79.99, category: 'Electronics', rating: 4.5, stock: 45, sales: 234 },
    { id: 2, name: 'Running Shoes', price: 129.99, category: 'Sports', rating: 4.8, stock: 23, sales: 189 },
    { id: 3, name: 'Coffee Maker', price: 49.99, category: 'Home', rating: 4.2, stock: 67, sales: 312 },
    { id: 4, name: 'Yoga Mat', price: 29.99, category: 'Sports', rating: 4.6, stock: 89, sales: 156 },
    { id: 5, name: 'Smart Watch', price: 199.99, category: 'Electronics', rating: 4.7, stock: 34, sales: 278 },
    { id: 6, name: 'Blender', price: 69.99, category: 'Home', rating: 4.4, stock: 52, sales: 201 }
  ];

  const orders = [
    { id: 1001, customer: 'John Doe', total: 209.98, status: 'Shipped', date: '2024-01-15' },
    { id: 1002, customer: 'Jane Smith', total: 79.99, status: 'Processing', date: '2024-01-16' },
    { id: 1003, customer: 'Bob Johnson', total: 359.97, status: 'Delivered', date: '2024-01-14' }
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

  const totalRevenue = orders.reduce((sum, order) => sum + order.total, 0);
  const totalProducts = products.reduce((sum, product) => sum + product.stock, 0);
  const totalOrders = orders.length;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">ShopHub</h1>
          <div className="flex gap-2">
            <button 
              onClick={() => setCurrentPage('products')}
              className={`px-4 py-2 rounded transition ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Products ({filteredProducts.length})
            </button>
            <button 
              onClick={() => setCurrentPage('cart')}
              className={`px-4 py-2 rounded transition ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Cart ({cart.length})
            </button>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Admin Dashboard
            </button>
          </div>
        </div>
      </nav>

      <div className="container mx-auto px-4">
        {currentPage === 'products' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Product Catalog</h2>
            
            <div className="mb-6 flex gap-4">
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
                className="px-4 py-2 bg-slate-800 rounded border border-slate-700 focus:border-blue-500 outline-none"
              >
                <option value="all">All Categories</option>
                <option value="Electronics">Electronics</option>
                <option value="Sports">Sports</option>
                <option value="Home">Home</option>
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProducts.map(product => (
                <div key={product.id} className="bg-slate-800 rounded-lg p-6 shadow-lg hover:shadow-xl transition">
                  <h3 className="text-xl font-semibold mb-2">{product.name}</h3>
                  <p className="text-slate-400 text-sm mb-2">{product.category}</p>
                  <div className="flex items-center mb-3">
                    <span className="text-yellow-400 mr-2">★</span>
                    <span>{product.rating}</span>
                    <span className="text-slate-500 ml-2">({product.sales} sold)</span>
                  </div>
                  <p className="text-2xl font-bold text-blue-400 mb-4">${product.price}</p>
                  <p className="text-sm text-slate-400 mb-4">Stock: {product.stock}</p>
                  <button
                    onClick={() => addToCart(product)}
                    className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition"
                  >
                    Add to Cart
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentPage === 'cart' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
            {cart.length === 0 ? (
              <div className="bg-slate-800 rounded-lg p-12 text-center">
                <p className="text-xl text-slate-400">Your cart is empty</p>
              </div>
            ) : (
              <div>
                <div className="bg-slate-800 rounded-lg overflow-hidden mb-6">
                  {cart.map((item, index) => (
                    <div key={index} className="flex justify-between items-center p-4 border-b border-slate-700 last:border-b-0">
                      <div>
                        <h3 className="font-semibold">{item.name}</h3>
                        <p className="text-slate-400">{item.category}</p>
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="text-xl font-bold text-blue-400">${item.price}</p>
                        <button
                          onClick={() => removeFromCart(index)}
                          className="bg-red-600 hover:bg-red-700 px-3 py-1 rounded text-sm transition"
                        >
                          Remove
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-slate-800 rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl">Total:</span>
                    <span className="text-3xl font-bold text-blue-400">
                      ${cart.reduce((sum, item) => sum + item.price, 0).toFixed(2)}
                    </span>
                  </div>
                  <button className="w-full bg-green-600 hover:bg-green-700 px-6 py-3 rounded text-lg font-semibold transition">
                    Proceed to Checkout
                  </button>
                </div>
              </div>
            )}
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
                <h3 className="text-lg font-semibold mb-2">Total Products</h3>
                <p className="text-3xl font-bold">{totalProducts}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-600 to-purple-800 rounded-lg p-6 shadow-lg">
                <h3 className="text-lg font-semibold mb-2">Total Orders</h3>
                <p className="text-3xl font-bold">{totalOrders}</p>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-800 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4">Inventory Status</h3>
                <div className="space-y-3">
                  {products.map(product => (
                    <div key={product.id} className="flex justify-between items-center">
                      <span className="text-sm">{product.name}</span>
                      <span className={`px-3 py-1 rounded text-sm ${product.stock > 50 ? 'bg-green-600' : product.stock > 20 ? 'bg-yellow-600' : 'bg-red-600'}`}>
                        {product.stock} units
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-slate-800 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4">Recent Orders</h3>
                <div className="space-y-3">
                  {orders.map(order => (
                    <div key={order.id} className="border-b border-slate-700 pb-3 last:border-b-0">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-semibold">#{order.id}</span>
                        <span className={`px-2 py-1 rounded text-xs ${order.status === 'Delivered' ? 'bg-green-600' : order.status === 'Shipped' ? 'bg-blue-600' : 'bg-yellow-600'}`}>
                          {order.status}
                        </span>
                      </div>
                      <p className="text-sm text-slate-400">{order.customer}</p>
                      <div className="flex justify-between items-center mt-1">
                        <span className="text-sm text-slate-500">{order.date}</span>
                        <span className="font-bold text-blue-400">${order.total}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

App;

export default App;