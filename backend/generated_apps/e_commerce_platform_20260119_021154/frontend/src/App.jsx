import React from 'react';

const { useState, useEffect } = React;

const App = () => {
  const [currentPage, setCurrentPage] = useState('products');
  const [products, setProducts] = useState([]);
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showAddProduct, setShowAddProduct] = useState(false);
  const [stats, setStats] = useState({ totalRevenue: 0, totalOrders: 0, totalProducts: 0 });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [productsRes, usersRes, ordersRes] = await Promise.all([
        fetch('/api/products'),
        fetch('/api/users'),
        fetch('/api/orders')
      ]);

      if (!productsRes.ok || !usersRes.ok || !ordersRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const productsData = await productsRes.json();
      const usersData = await usersRes.json();
      const ordersData = await ordersRes.json();

      setProducts(productsData);
      setUsers(usersData);
      setOrders(ordersData);

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

  const addProduct = async (productData) => {
    try {
      const res = await fetch('/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      if (res.ok) {
        const newProduct = await res.json();
        setProducts([...products, newProduct]);
        setShowAddProduct(false);
        setStats(prev => ({ ...prev, totalProducts: prev.totalProducts + 1 }));
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteProduct = async (id) => {
    try {
      const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setProducts(products.filter(p => p.id !== id));
        setStats(prev => ({ ...prev, totalProducts: prev.totalProducts - 1 }));
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const updateProduct = async (id, updates) => {
    try {
      const res = await fetch(`/api/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates)
      });
      if (res.ok) {
        const updated = await res.json();
        setProducts(products.map(p => p.id === id ? updated : p));
      }
    } catch (err) {
      setError(err.message);
    }
  };

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

  const checkout = async () => {
    const orderData = {
      items: cart,
      total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0),
      status: 'pending'
    };
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });
      if (res.ok) {
        const newOrder = await res.json();
        setOrders([...orders, newOrder]);
        setCart([]);
        setStats(prev => ({ 
          ...prev, 
          totalOrders: prev.totalOrders + 1,
          totalRevenue: prev.totalRevenue + orderData.total
        }));
        alert('Order placed successfully!');
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

  const categories = [...new Set(products.map(p => p.category).filter(Boolean))];

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
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold">E-Commerce Platform</h1>
            <div className="flex gap-4">
              <button onClick={() => setCurrentPage('dashboard')} className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}>Dashboard</button>
              <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}>Products</button>
              <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'} relative`}>
                Cart {cart.length > 0 && <span className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs">{cart.length}</span>}
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {currentPage === 'dashboard' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <h3 className="text-slate-400 text-sm mb-2">Total Revenue</h3>
                <p className="text-3xl font-bold text-green-400">${stats.totalRevenue.toFixed(2)}</p>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <h3 className="text-slate-400 text-sm mb-2">Total Orders</h3>
                <p className="text-3xl font-bold text-blue-400">{stats.totalOrders}</p>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <h3 className="text-slate-400 text-sm mb-2">Products</h3>
                <p className="text-3xl font-bold text-purple-400">{stats.totalProducts}</p>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
              <h3 className="text-xl font-bold mb-4">Recent Orders</h3>
              {orders.length === 0 ? (
                <p className="text-slate-400">No orders yet</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4">Order ID</th>
                        <th className="text-left py-3 px-4">Total</th>
                        <th className="text-left py-3 px-4">Status</th>
                        <th className="text-left py-3 px-4">Items</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.slice(-5).reverse().map(order => (
                        <tr key={order.id} className="border-b border-slate-700">
                          <td className="py-3 px-4">#{order.id}</td>
                          <td className="py-3 px-4">${order.total?.toFixed(2)}</td>
                          <td className="py-3 px-4">
                            <span className="px-2 py-1 rounded bg-yellow-600 text-xs">{order.status}</span>
                          </td>
                          <td className="py-3 px-4">{order.items?.length || 0}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Product Inventory</h3>
              <button onClick={() => { setCurrentPage('products'); setShowAddProduct(true); }} className="mb-4 px-4 py-2 bg-green-600 hover:bg-green-700 rounded">Add New Product</button>
              {products.length === 0 ? (
                <p className="text-slate-400">No products available</p>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4">Name</th>
                        <th className="text-left py-3 px-4">Category</th>
                        <th className="text-left py-3 px-4">Price</th>
                        <th className="text-left py-3 px-4">Stock</th>
                        <th className="text-left py-3 px-4">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {products.map(product => (
                        <tr key={product.id} className="border-b border-slate-700">
                          <td className="py-3 px-4">{product.name}</td>
                          <td className="py-3 px-4">{product.category}</td>
                          <td className="py-3 px-4">${product.price}</td>
                          <td className="py-3 px-4">{product.stock || 'N/A'}</td>
                          <td className="py-3 px-4">
                            <button onClick={() => deleteProduct(product.id)} className="text-red-400 hover:text-red-300">Delete</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        )}

        {currentPage === 'products' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold">Product Catalog</h2>
              <button onClick={() => setShowAddProduct(true)} className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded">Add Product</button>
            </div>

            <div className="flex gap-4 mb-6">
              <input type="text" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded focus:outline-none focus:border-blue-500" />
              <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="px-4 py-2 bg-slate-800 border border-slate-700 rounded focus:outline-none focus:border-blue-500">
                <option value="all">All Categories</option>
                {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
            </div>

            {showAddProduct && (
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
                <h3 className="text-xl font-bold mb-4">Add New Product</h3>
                <form onSubmit={(e) => {
                  e.preventDefault();
                  const formData = new FormData(e.target);
                  addProduct({
                    name: formData.get('name'),
                    price: parseFloat(formData.get('price')),
                    category: formData.get('category'),
                    description: formData.get('description'),
                    stock: parseInt(formData.get('stock'))
                  });
                  e.target.reset();
                }}>
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <input type="text" name="name" placeholder="Product Name" required className="px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-blue-500" />
                    <input type="number" name="price" placeholder="Price" step="0.01" required className="px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-blue-500" />
                    <input type="text" name="category" placeholder="Category" required className="px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-blue-500" />
                    <input type="number" name="stock" placeholder="Stock" required className="px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-blue-500" />
                  </div>
                  <textarea name="description" placeholder="Description" className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded focus:outline-none focus:border-blue-500 mb-4" rows="3"></textarea>
                  <div className="flex gap-2">
                    <button type="submit" className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded">Add Product</button>
                    <button type="button" onClick={() => setShowAddProduct(false)} className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded">Cancel</button>
                  </div>
                </form>
              </div>
            )}

            {filteredProducts.length === 0 ? (
              <div className="text-center text-slate-400 py-12">No products found</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {filteredProducts.map(product => (
                  <div key={product.id} className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
                    <div className="h-48 bg-slate-700 flex items-center justify-center">
                      <span className="text-slate-500">No Image</span>
                    </div>
                    <div className="p-4">
                      <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                      <p className="text-slate-400 text-sm mb-2">{product.category}</p>
                      <p className="text-slate-300 mb-4">{product.description}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-2xl font-bold text-green-400">${product.price}</span>
                        <button onClick={() => addToCart(product)} className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded">Add to Cart</button>
                      </div>
                    </div>
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
              <div>
                <div className="space-y-4 mb-6">
                  {cart.map(item => (
                    <div key={item.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700 flex justify-between items-center">
                      <div>
                        <h3 className="text-xl font-bold">{item.name}</h3>
                        <p className="text-slate-400">Quantity: {item.quantity}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-green-400">${(item.price * item.quantity).toFixed(2)}</p>
                        <button onClick={() => removeFromCart(item.id)} className="text-red-400 hover:text-red-300 text-sm">Remove</button>
                      </div>
                    </div>
                  ))}
                </div>
                <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl font-bold">Total:</span>
                    <span className="text-3xl font-bold text-green-400">${cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}</span>
                  </div>
                  <button onClick={checkout} className="w-full px-4 py-3 bg-green-600 hover:bg-green-700 rounded text-lg font-bold">Checkout</button>
                </div>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

App;

export default App;