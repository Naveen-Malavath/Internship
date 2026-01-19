import React from 'react';

const { useState, useEffect } = React;

const App = () => {
  const [currentPage, setCurrentPage] = useState('products');
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showCartModal, setShowCartModal] = useState(false);
  const [orders, setOrders] = useState([]);
  const [reviews, setReviews] = useState([]);
  const [stats, setStats] = useState(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [productsRes, cartRes, ordersRes] = await Promise.all([
        fetch('/api/products'),
        fetch('/api/cart'),
        fetch('/api/orders')
      ]);

      if (productsRes.ok) {
        const productsData = await productsRes.json();
        setProducts(productsData);
      }
      if (cartRes.ok) {
        const cartData = await cartRes.json();
        setCart(cartData);
      }
      if (ordersRes.ok) {
        const ordersData = await ordersRes.json();
        setOrders(ordersData);
      }

      const statsRes = await fetch('/api/stats');
      if (statsRes.ok) {
        const statsData = await statsRes.json();
        setStats(statsData);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleLogin = async (email, password) => {
    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setShowLoginModal(false);
      } else {
        setError('Login failed');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const handleRegister = async (email, password, name) => {
    try {
      const res = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, name })
      });
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
        setShowLoginModal(false);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const addToCart = async (product) => {
    try {
      const res = await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: product.id, quantity: 1 })
      });
      if (res.ok) {
        const newCart = await res.json();
        setCart(newCart);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const updateCartQuantity = async (itemId, quantity) => {
    try {
      const res = await fetch(`/api/cart/${itemId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity })
      });
      if (res.ok) {
        const updatedCart = await res.json();
        setCart(updatedCart);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const removeFromCart = async (itemId) => {
    try {
      await fetch(`/api/cart/${itemId}`, { method: 'DELETE' });
      setCart(cart.filter(item => item.id !== itemId));
    } catch (err) {
      setError(err.message);
    }
  };

  const checkout = async () => {
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ cart_items: cart })
      });
      if (res.ok) {
        const order = await res.json();
        setOrders([...orders, order]);
        setCart([]);
        setShowCartModal(false);
        setCurrentPage('orders');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const addReview = async (productId, rating, comment) => {
    try {
      const res = await fetch('/api/reviews', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ product_id: productId, rating, comment })
      });
      if (res.ok) {
        const review = await res.json();
        setReviews([...reviews, review]);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || p.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const categories = [...new Set(products.map(p => p.category))];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">E-Commerce Store</h1>
          <div className="flex gap-4">
            <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700'}`}>Products</button>
            <button onClick={() => setCurrentPage('orders')} className={`px-4 py-2 rounded ${currentPage === 'orders' ? 'bg-blue-600' : 'bg-slate-700'}`}>Orders</button>
            {user?.role === 'admin' && <button onClick={() => setCurrentPage('admin')} className={`px-4 py-2 rounded ${currentPage === 'admin' ? 'bg-blue-600' : 'bg-slate-700'}`}>Dashboard</button>}
            <button onClick={() => setShowCartModal(true)} className="px-4 py-2 bg-green-600 rounded relative">Cart ({cart.length})</button>
            {!user ? <button onClick={() => setShowLoginModal(true)} className="px-4 py-2 bg-purple-600 rounded">Login</button> : <span className="px-4 py-2">{user.name}</span>}
          </div>
        </div>
      </nav>

      {error && <div className="bg-red-600 text-white p-4 text-center">{error}</div>}

      <div className="container mx-auto p-6">
        {currentPage === 'products' && (
          <div>
            <div className="mb-6 flex gap-4">
              <input type="text" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="flex-1 p-3 bg-slate-800 border border-slate-700 rounded text-white" />
              <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="p-3 bg-slate-800 border border-slate-700 rounded text-white">
                <option value="all">All Categories</option>
                {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {filteredProducts.map(product => (
                <div key={product.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4">
                  <div className="bg-slate-700 h-48 rounded mb-4 flex items-center justify-center">
                    <span className="text-slate-500">Image</span>
                  </div>
                  <h3 className="font-bold text-lg mb-2">{product.name}</h3>
                  <p className="text-slate-400 text-sm mb-2">{product.description}</p>
                  <p className="text-green-400 font-bold text-xl mb-4">${product.price}</p>
                  <button onClick={() => addToCart(product)} className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">Add to Cart</button>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentPage === 'orders' && (
          <div>
            <h2 className="text-2xl font-bold mb-6">My Orders</h2>
            <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="p-4 text-left">Order ID</th>
                    <th className="p-4 text-left">Date</th>
                    <th className="p-4 text-left">Total</th>
                    <th className="p-4 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <tr key={order.id} className="border-t border-slate-700">
                      <td className="p-4">#{order.id}</td>
                      <td className="p-4">{new Date(order.created_at).toLocaleDateString()}</td>
                      <td className="p-4">${order.total}</td>
                      <td className="p-4"><span className="bg-green-600 px-2 py-1 rounded text-sm">{order.status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {currentPage === 'admin' && stats && (
          <div>
            <h2 className="text-2xl font-bold mb-6">Admin Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Total Revenue</h3>
                <p className="text-3xl font-bold text-green-400">${stats.total_revenue || 0}</p>
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Total Orders</h3>
                <p className="text-3xl font-bold text-blue-400">{stats.total_orders || 0}</p>
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Total Products</h3>
                <p className="text-3xl font-bold text-purple-400">{stats.total_products || 0}</p>
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Total Users</h3>
                <p className="text-3xl font-bold text-yellow-400">{stats.total_users || 0}</p>
              </div>
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Products Inventory</h3>
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="p-3 text-left">Product</th>
                    <th className="p-3 text-left">Category</th>
                    <th className="p-3 text-left">Price</th>
                    <th className="p-3 text-left">Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(product => (
                    <tr key={product.id} className="border-t border-slate-700">
                      <td className="p-3">{product.name}</td>
                      <td className="p-3">{product.category}</td>
                      <td className="p-3">${product.price}</td>
                      <td className="p-3">{product.stock || 0}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>

      {showCartModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-lg p-6 max-w-2xl w-full max-h-96 overflow-y-auto">
            <h2 className="text-2xl font-bold mb-4">Shopping Cart</h2>
            {cart.length === 0 ? (
              <p className="text-slate-400">Your cart is empty</p>
            ) : (
              <div>
                {cart.map(item => (
                  <div key={item.id} className="flex justify-between items-center border-b border-slate-700 py-4">
                    <div>
                      <h3 className="font-bold">{item.product_name}</h3>
                      <p className="text-slate-400">${item.price}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <input type="number" value={item.quantity} onChange={(e) => updateCartQuantity(item.id, parseInt(e.target.value))} className="w-20 p-2 bg-slate-700 rounded text-center" />
                      <button onClick={() => removeFromCart(item.id)} className="bg-red-600 px-3 py-1 rounded">Remove</button>
                    </div>
                  </div>
                ))}
                <div className="mt-4 flex justify-between items-center">
                  <p className="text-xl font-bold">Total: ${cart.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2)}</p>
                  <button onClick={checkout} className="bg-green-600 px-6 py-2 rounded">Checkout</button>
                </div>
              </div>
            )}
            <button onClick={() => setShowCartModal(false)} className="mt-4 bg-slate-700 px-4 py-2 rounded">Close</button>
          </div>
        </div>
      )}

      {showLoginModal && <LoginModal onLogin={handleLogin} onRegister={handleRegister} onClose={() => setShowLoginModal(false)} />}
    </div>
  );
};

const LoginModal = ({ onLogin, onRegister, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (isLogin) {
      onLogin(email, password);
    } else {
      onRegister(email, password, name);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <div className="bg-slate-800 rounded-lg p-6 max-w-md w-full">
        <h2 className="text-2xl font-bold mb-4">{isLogin ? 'Login' : 'Register'}</h2>
        <form onSubmit={handleSubmit}>
          {!isLogin && <input type="text" placeholder="Name" value={name} onChange={(e) => setName(e.target.value)} className="w-full p-3 mb-4 bg-slate-700 border border-slate-600 rounded" required />}
          <input type="email" placeholder="Email" value={email} onChange={(e) => setEmail(e.target.value)} className="w-full p-3 mb-4 bg-slate-700 border border-slate-600 rounded" required />
          <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} className="w-full p-3 mb-4 bg-slate-700 border border-slate-600 rounded" required />
          <button type="submit" className="w-full bg-blue-600 p-3 rounded mb-4">{isLogin ? 'Login' : 'Register'}</button>
        </form>
        <button onClick={() => setIsLogin(!isLogin)} className="text-blue-400 mb-4">{isLogin ? 'Need an account? Register' : 'Have an account? Login'}</button>
        <button onClick={onClose} className="w-full bg-slate-700 p-3 rounded">Close</button>
      </div>
    </div>
  );
};

App;

export default App;