import React from 'react';

const { useState, useEffect } = React;

const App = () => {
  const [page, setPage] = useState('products');
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState('all');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');
  const [stats, setStats] = useState({ totalRevenue: 0, totalOrders: 0, totalProducts: 0 });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [productsRes, ordersRes] = await Promise.all([
        fetch('/api/products'),
        fetch('/api/orders')
      ]);
      
      if (!productsRes.ok || !ordersRes.ok) throw new Error('Failed to fetch data');
      
      const productsData = await productsRes.json();
      const ordersData = await ordersRes.json();
      
      setProducts(Array.isArray(productsData) ? productsData : []);
      setOrders(Array.isArray(ordersData) ? ordersData : []);
      
      const revenue = ordersData.reduce((sum, order) => sum + (order.total || 0), 0);
      setStats({
        totalRevenue: revenue,
        totalOrders: ordersData.length,
        totalProducts: productsData.length
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const email = formData.get('email');
    const password = formData.get('password');
    
    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setShowAuthModal(false);
      } else {
        alert('Authentication failed');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const addToCart = (product) => {
    const existing = cart.find(item => item.id === product.id);
    if (existing) {
      setCart(cart.map(item => 
        item.id === product.id ? { ...item, quantity: item.quantity + 1 } : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const checkout = async () => {
    if (!user) {
      setShowAuthModal(true);
      return;
    }
    
    const total = cart.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0);
    
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          userId: user.id,
          items: cart,
          total,
          status: 'pending'
        })
      });
      
      if (res.ok) {
        const newOrder = await res.json();
        setOrders([...orders, newOrder]);
        setCart([]);
        setPage('orders');
        alert('Order placed successfully!');
      }
    } catch (err) {
      alert('Checkout failed: ' + err.message);
    }
  };

  const addProduct = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const newProduct = {
      name: formData.get('name'),
      price: parseFloat(formData.get('price')),
      category: formData.get('category'),
      stock: parseInt(formData.get('stock')),
      rating: 0,
      reviews: []
    };
    
    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newProduct)
      });
      
      if (res.ok) {
        const created = await res.json();
        setProducts([...products, created]);
        e.target.reset();
      }
    } catch (err) {
      alert('Failed to add product: ' + err.message);
    }
  };

  const deleteProduct = async (id) => {
    try {
      await fetch(`/api/products/${id}`, { method: 'DELETE' });
      setProducts(products.filter(p => p.id !== id));
    } catch (err) {
      alert('Failed to delete: ' + err.message);
    }
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filter === 'all' || p.category === filter;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading E-Commerce Platform...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-red-500 text-xl">Error: {error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold">🛒 E-Shop</h1>
            <button onClick={() => setPage('dashboard')} className={`px-4 py-2 rounded ${page === 'dashboard' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Dashboard</button>
            <button onClick={() => setPage('products')} className={`px-4 py-2 rounded ${page === 'products' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Products</button>
            <button onClick={() => setPage('orders')} className={`px-4 py-2 rounded ${page === 'orders' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Orders</button>
            <button onClick={() => setPage('cart')} className={`px-4 py-2 rounded ${page === 'cart' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Cart ({cart.length})</button>
          </div>
          <div>
            {user ? (
              <span className="text-sm">Welcome, {user.email}</span>
            ) : (
              <button onClick={() => setShowAuthModal(true)} className="bg-green-600 px-4 py-2 rounded hover:bg-green-700">Login</button>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {page === 'dashboard' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm">Total Revenue</div>
                <div className="text-3xl font-bold text-green-500">${stats.totalRevenue.toFixed(2)}</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm">Total Orders</div>
                <div className="text-3xl font-bold text-blue-500">{stats.totalOrders}</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm">Total Products</div>
                <div className="text-3xl font-bold text-purple-500">{stats.totalProducts}</div>
              </div>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-lg mb-6">
              <h3 className="text-xl font-bold mb-4">Add New Product</h3>
              <form onSubmit={addProduct} className="grid grid-cols-4 gap-4">
                <input name="name" placeholder="Product Name" required className="bg-slate-700 p-2 rounded" />
                <input name="price" type="number" step="0.01" placeholder="Price" required className="bg-slate-700 p-2 rounded" />
                <select name="category" required className="bg-slate-700 p-2 rounded">
                  <option value="">Select Category</option>
                  <option value="electronics">Electronics</option>
                  <option value="clothing">Clothing</option>
                  <option value="books">Books</option>
                  <option value="home">Home</option>
                </select>
                <input name="stock" type="number" placeholder="Stock" required className="bg-slate-700 p-2 rounded" />
                <button type="submit" className="col-span-4 bg-blue-600 p-2 rounded hover:bg-blue-700">Add Product</button>
              </form>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-bold mb-4">Recent Orders</h3>
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left p-2">Order ID</th>
                    <th className="text-left p-2">Total</th>
                    <th className="text-left p-2">Status</th>
                    <th className="text-left p-2">Items</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.slice(0, 5).map(order => (
                    <tr key={order.id} className="border-b border-slate-700">
                      <td className="p-2">#{order.id}</td>
                      <td className="p-2">${order.total?.toFixed(2)}</td>
                      <td className="p-2"><span className="bg-yellow-600 px-2 py-1 rounded text-xs">{order.status}</span></td>
                      <td className="p-2">{order.items?.length || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {page === 'products' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Product Catalog</h2>
            <div className="flex gap-4 mb-6">
              <input value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} placeholder="Search products..." className="flex-1 bg-slate-800 p-3 rounded" />
              <select value={filter} onChange={(e) => setFilter(e.target.value)} className="bg-slate-800 p-3 rounded">
                <option value="all">All Categories</option>
                <option value="electronics">Electronics</option>
                <option value="clothing">Clothing</option>
                <option value="books">Books</option>
                <option value="home">Home</option>
              </select>
            </div>

            {filteredProducts.length === 0 ? (
              <div className="text-center text-slate-400 py-12">No products found</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {filteredProducts.map(product => (
                  <div key={product.id} className="bg-slate-800 rounded-lg p-4 hover:bg-slate-750">
                    <div className="aspect-square bg-slate-700 rounded mb-3 flex items-center justify-center text-4xl">📦</div>
                    <h3 className="font-bold mb-2">{product.name}</h3>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-2xl font-bold text-green-500">${product.price?.toFixed(2)}</span>
                      <span className="text-sm text-slate-400">{product.category}</span>
                    </div>
                    <div className="text-sm text-slate-400 mb-3">Stock: {product.stock || 0}</div>
                    <div className="flex gap-2">
                      <button onClick={() => addToCart(product)} className="flex-1 bg-blue-600 p-2 rounded hover:bg-blue-700">Add to Cart</button>
                      <button onClick={() => deleteProduct(product.id)} className="bg-red-600 p-2 rounded hover:bg-red-700">🗑️</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {page === 'cart' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
            {cart.length === 0 ? (
              <div className="text-center text-slate-400 py-12">Your cart is empty</div>
            ) : (
              <div>
                <div className="bg-slate-800 rounded-lg p-6 mb-6">
                  {cart.map(item => (
                    <div key={item.id} className="flex items-center justify-between border-b border-slate-700 py-4">
                      <div className="flex items-center gap-4">
                        <div className="w-16 h-16 bg-slate-700 rounded flex items-center justify-center">📦</div>
                        <div>
                          <div className="font-bold">{item.name}</div>
                          <div className="text-slate-400">Quantity: {item.quantity}</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <div className="text-xl font-bold">${((item.price || 0) * item.quantity).toFixed(2)}</div>
                        <button onClick={() => removeFromCart(item.id)} className="bg-red-600 px-3 py-1 rounded hover:bg-red-700">Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-slate-800 rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl">Total:</span>
                    <span className="text-3xl font-bold text-green-500">${cart.reduce((sum, item) => sum + (item.price || 0) * item.quantity, 0).toFixed(2)}</span>
                  </div>
                  <button onClick={checkout} className="w-full bg-green-600 p-3 rounded text-xl hover:bg-green-700">Proceed to Checkout</button>
                </div>
              </div>
            )}
          </div>
        )}

        {page === 'orders' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Order History</h2>
            {orders.length === 0 ? (
              <div className="text-center text-slate-400 py-12">No orders yet</div>
            ) : (
              <div className="space-y-4">
                {orders.map(order => (
                  <div key={order.id} className="bg-slate-800 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="text-xl font-bold">Order #{order.id}</div>
                        <div className="text-slate-400">Status: <span className="text-yellow-500">{order.status}</span></div>
                      </div>
                      <div className="text-2xl font-bold text-green-500">${order.total?.toFixed(2)}</div>
                    </div>
                    <div className="text-sm text-slate-400">Items: {order.items?.length || 0}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {showAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-slate-800 p-8 rounded-lg w-96">
            <h2 className="text-2xl font-bold mb-4">{authMode === 'login' ? 'Login' : 'Register'}</h2>
            <form onSubmit={handleAuth}>
              <input name="email" type="email" placeholder="Email" required className="w-full bg-slate-700 p-3 rounded mb-3" />
              <input name="password" type="password" placeholder="Password" required className="w-full bg-slate-700 p-3 rounded mb-4" />
              <button type="submit" className="w-full bg-blue-600 p-3 rounded hover:bg-blue-700 mb-3">
                {authMode === 'login' ? 'Login' : 'Register'}
              </button>
              <button type="button" onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')} className="w-full text-blue-400 hover:text-blue-300">
                {authMode === 'login' ? 'Need an account? Register' : 'Have an account? Login'}
              </button>
              <button type="button" onClick={() => setShowAuthModal(false)} className="w-full mt-3 text-slate-400 hover:text-white">Cancel</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;