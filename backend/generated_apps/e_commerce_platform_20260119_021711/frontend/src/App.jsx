import React from 'react';

const { useState, useEffect } = React;

const App = () => {
  const [currentPage, setCurrentPage] = useState('products');
  const [products, setProducts] = useState([]);
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [category, setCategory] = useState('all');
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  useEffect(() => {
    loadProducts();
    loadUser();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const res = await fetch('/api/products');
      if (!res.ok) throw new Error('Failed to load products');
      const data = await res.json();
      setProducts(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadUser = async () => {
    try {
      const res = await fetch('/api/auth/me');
      if (res.ok) {
        const userData = await res.json();
        setUser(userData);
      }
    } catch (err) {
      console.log('Not authenticated');
    }
  };

  const handleAuth = async (email, password, name = '') => {
    try {
      const endpoint = authMode === 'login' ? '/api/auth/login' : '/api/auth/register';
      const body = authMode === 'login' ? { email, password } : { email, password, name };
      
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      });
      
      if (!res.ok) throw new Error('Authentication failed');
      const userData = await res.json();
      setUser(userData);
      setShowAuthModal(false);
    } catch (err) {
      alert(err.message);
    }
  };

  const addToCart = async (product) => {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
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

  const updateQuantity = (productId, quantity) => {
    if (quantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => 
        item.id === productId ? { ...item, quantity } : item
      ));
    }
  };

  const checkout = async () => {
    if (!user) {
      alert('Please login to checkout');
      setShowAuthModal(true);
      return;
    }

    try {
      const orderData = {
        items: cart,
        total: cart.reduce((sum, item) => sum + item.price * item.quantity, 0),
        userId: user.id
      };

      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });

      if (!res.ok) throw new Error('Checkout failed');
      const order = await res.json();
      setOrders([...orders, order]);
      setCart([]);
      setCurrentPage('orders');
      alert('Order placed successfully!');
    } catch (err) {
      alert(err.message);
    }
  };

  const filteredProducts = products.filter(p => 
    (searchTerm === '' || p.name.toLowerCase().includes(searchTerm.toLowerCase())) &&
    (category === 'all' || p.category === category)
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading...</div>
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
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <h1 className="text-2xl font-bold text-blue-400">ShopHub</h1>
            <div className="flex space-x-4">
              <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Products</button>
              <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Cart ({cart.length})</button>
              {user && <button onClick={() => setCurrentPage('orders')} className={`px-4 py-2 rounded ${currentPage === 'orders' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Orders</button>}
              {user?.isAdmin && <button onClick={() => setCurrentPage('admin')} className={`px-4 py-2 rounded ${currentPage === 'admin' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}>Admin</button>}
            </div>
          </div>
          <div>
            {user ? (
              <span className="text-slate-300">Welcome, {user.name}</span>
            ) : (
              <button onClick={() => setShowAuthModal(true)} className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">Login</button>
            )}
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {currentPage === 'products' && (
          <div>
            <div className="mb-6 flex gap-4">
              <input type="text" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white" />
              <select value={category} onChange={(e) => setCategory(e.target.value)} className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white">
                <option value="all">All Categories</option>
                <option value="electronics">Electronics</option>
                <option value="clothing">Clothing</option>
                <option value="books">Books</option>
              </select>
            </div>
            {filteredProducts.length === 0 ? (
              <div className="text-center text-slate-400 py-12">No products found</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
                {filteredProducts.map(product => (
                  <div key={product.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4 hover:border-blue-500 transition">
                    <div className="h-48 bg-slate-700 rounded mb-4 flex items-center justify-center text-slate-500">Image</div>
                    <h3 className="font-semibold text-lg mb-2">{product.name}</h3>
                    <p className="text-slate-400 text-sm mb-2">{product.category}</p>
                    <div className="flex items-center justify-between mb-3">
                      <span className="text-2xl font-bold text-blue-400">${product.price}</span>
                      <span className="text-yellow-400">★ {product.rating || 4.5}</span>
                    </div>
                    <button onClick={() => addToCart(product)} className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-semibold">Add to Cart</button>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {currentPage === 'cart' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
            {cart.length === 0 ? (
              <div className="text-center text-slate-400 py-12">Your cart is empty</div>
            ) : (
              <div className="space-y-4">
                {cart.map(item => (
                  <div key={item.id} className="bg-slate-800 border border-slate-700 rounded-lg p-4 flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className="w-20 h-20 bg-slate-700 rounded"></div>
                      <div>
                        <h3 className="font-semibold">{item.name}</h3>
                        <p className="text-slate-400">${item.price}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="flex items-center space-x-2">
                        <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="px-3 py-1 bg-slate-700 rounded">-</button>
                        <span className="px-4">{item.quantity}</span>
                        <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="px-3 py-1 bg-slate-700 rounded">+</button>
                      </div>
                      <span className="font-bold text-xl">${(item.price * item.quantity).toFixed(2)}</span>
                      <button onClick={() => removeFromCart(item.id)} className="px-4 py-2 bg-red-600 hover:bg-red-700 rounded">Remove</button>
                    </div>
                  </div>
                ))}
                <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-2xl font-bold">Total:</span>
                    <span className="text-3xl font-bold text-blue-400">${cart.reduce((sum, item) => sum + item.price * item.quantity, 0).toFixed(2)}</span>
                  </div>
                  <button onClick={checkout} className="w-full bg-green-600 hover:bg-green-700 py-3 rounded font-bold text-lg">Checkout</button>
                </div>
              </div>
            )}
          </div>
        )}

        {currentPage === 'orders' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">My Orders</h2>
            {orders.length === 0 ? (
              <div className="text-center text-slate-400 py-12">No orders yet</div>
            ) : (
              <div className="space-y-4">
                {orders.map(order => (
                  <div key={order.id} className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="font-bold text-xl">Order #{order.id}</h3>
                        <p className="text-slate-400">{order.date || new Date().toLocaleDateString()}</p>
                      </div>
                      <span className="px-4 py-2 bg-green-600 rounded">{order.status || 'Processing'}</span>
                    </div>
                    <div className="text-2xl font-bold text-blue-400">Total: ${order.total.toFixed(2)}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {currentPage === 'admin' && user?.isAdmin && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Total Products</h3>
                <p className="text-4xl font-bold text-blue-400">{products.length}</p>
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Total Orders</h3>
                <p className="text-4xl font-bold text-green-400">{orders.length}</p>
              </div>
              <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
                <h3 className="text-slate-400 mb-2">Revenue</h3>
                <p className="text-4xl font-bold text-yellow-400">${orders.reduce((sum, o) => sum + o.total, 0).toFixed(2)}</p>
              </div>
            </div>
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Product Management</h3>
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3">Name</th>
                    <th className="text-left py-3">Category</th>
                    <th className="text-left py-3">Price</th>
                    <th className="text-left py-3">Stock</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(product => (
                    <tr key={product.id} className="border-b border-slate-700">
                      <td className="py-3">{product.name}</td>
                      <td className="py-3">{product.category}</td>
                      <td className="py-3">${product.price}</td>
                      <td className="py-3">{product.stock || 'In Stock'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {showAuthModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
          <div className="bg-slate-800 rounded-lg p-8 w-96">
            <h2 className="text-2xl font-bold mb-4">{authMode === 'login' ? 'Login' : 'Register'}</h2>
            <form onSubmit={(e) => { e.preventDefault(); const formData = new FormData(e.target); handleAuth(formData.get('email'), formData.get('password'), formData.get('name')); }}>
              {authMode === 'register' && <input type="text" name="name" placeholder="Name" className="w-full px-4 py-2 mb-4 bg-slate-700 border border-slate-600 rounded text-white" required />}
              <input type="email" name="email" placeholder="Email" className="w-full px-4 py-2 mb-4 bg-slate-700 border border-slate-600 rounded text-white" required />
              <input type="password" name="password" placeholder="Password" className="w-full px-4 py-2 mb-4 bg-slate-700 border border-slate-600 rounded text-white" required />
              <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-semibold mb-4">{authMode === 'login' ? 'Login' : 'Register'}</button>
            </form>
            <button onClick={() => setAuthMode(authMode === 'login' ? 'register' : 'login')} className="text-blue-400 hover:underline">{authMode === 'login' ? 'Need an account? Register' : 'Have an account? Login'}</button>
            <button onClick={() => setShowAuthModal(false)} className="ml-4 text-slate-400 hover:underline">Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;