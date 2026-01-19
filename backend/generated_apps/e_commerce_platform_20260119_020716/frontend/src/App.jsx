import React from 'react';

const { useState, useEffect } = React;

const App = () => {
  const [currentPage, setCurrentPage] = useState('products');
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [stats, setStats] = useState({ totalProducts: 0, totalOrders: 0, totalRevenue: 0 });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [productsRes, ordersRes, userRes] = await Promise.all([
        fetch('/api/products'),
        fetch('/api/orders'),
        fetch('/api/user')
      ]);

      if (productsRes.ok) {
        const productsData = await productsRes.json();
        setProducts(Array.isArray(productsData) ? productsData : []);
      }

      if (ordersRes.ok) {
        const ordersData = await ordersRes.json();
        setOrders(Array.isArray(ordersData) ? ordersData : []);
      }

      if (userRes.ok) {
        const userData = await userRes.json();
        setUser(userData);
      }

      calculateStats();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const calculateStats = () => {
    const totalRevenue = orders.reduce((sum, order) => sum + (order.total || 0), 0);
    setStats({
      totalProducts: products.length,
      totalOrders: orders.length,
      totalRevenue: totalRevenue
    });
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
        setShowProductForm(false);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const updateProduct = async (id, productData) => {
    try {
      const res = await fetch(`/api/products/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      if (res.ok) {
        const updated = await res.json();
        setProducts(products.map(p => p.id === id ? updated : p));
        setEditingProduct(null);
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteProduct = async (id) => {
    if (!confirm('Delete this product?')) return;
    try {
      const res = await fetch(`/api/products/${id}`, { method: 'DELETE' });
      if (res.ok) {
        setProducts(products.filter(p => p.id !== id));
      }
    } catch (err) {
      setError(err.message);
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
    const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          items: cart,
          total: total,
          status: 'pending'
        })
      });
      if (res.ok) {
        const order = await res.json();
        setOrders([...orders, order]);
        setCart([]);
        alert('Order placed successfully!');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         p.description?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = categoryFilter === 'all' || p.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  const categories = [...new Set(products.map(p => p.category).filter(Boolean))];

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">Loading...</div>
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
          <h1 className="text-2xl font-bold">E-Commerce Platform</h1>
          <div className="flex gap-4">
            <button onClick={() => setCurrentPage('dashboard')} className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}>Dashboard</button>
            <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700'}`}>Products</button>
            <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700'}`}>Cart ({cart.length})</button>
            <button onClick={() => setCurrentPage('orders')} className={`px-4 py-2 rounded ${currentPage === 'orders' ? 'bg-blue-600' : 'bg-slate-700'}`}>Orders</button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto p-6">
        {currentPage === 'dashboard' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Admin Dashboard</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="text-slate-400 text-sm">Total Products</div>
                <div className="text-3xl font-bold mt-2">{stats.totalProducts}</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="text-slate-400 text-sm">Total Orders</div>
                <div className="text-3xl font-bold mt-2">{stats.totalOrders}</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="text-slate-400 text-sm">Total Revenue</div>
                <div className="text-3xl font-bold mt-2">${stats.totalRevenue.toFixed(2)}</div>
              </div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Recent Orders</h3>
              {orders.length === 0 ? (
                <div className="text-slate-400 text-center py-8">No orders yet</div>
              ) : (
                <table className="w-full">
                  <thead className="border-b border-slate-700">
                    <tr className="text-left">
                      <th className="pb-2">Order ID</th>
                      <th className="pb-2">Items</th>
                      <th className="pb-2">Total</th>
                      <th className="pb-2">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.slice(0, 5).map(order => (
                      <tr key={order.id} className="border-b border-slate-700">
                        <td className="py-3">#{order.id}</td>
                        <td>{order.items?.length || 0}</td>
                        <td>${order.total?.toFixed(2)}</td>
                        <td><span className="px-2 py-1 bg-yellow-600 rounded text-xs">{order.status}</span></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </div>
        )}

        {currentPage === 'products' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold">Product Catalog</h2>
              <button onClick={() => setShowProductForm(true)} className="px-4 py-2 bg-green-600 rounded hover:bg-green-700">Add Product</button>
            </div>
            <div className="mb-6 flex gap-4">
              <input type="text" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded" />
              <select value={categoryFilter} onChange={(e) => setCategoryFilter(e.target.value)} className="px-4 py-2 bg-slate-800 border border-slate-700 rounded">
                <option value="all">All Categories</option>
                {categories.map(cat => <option key={cat} value={cat}>{cat}</option>)}
              </select>
            </div>
            {filteredProducts.length === 0 ? (
              <div className="text-slate-400 text-center py-12">No products found</div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {filteredProducts.map(product => (
                  <div key={product.id} className="bg-slate-800 rounded-lg border border-slate-700 p-4">
                    <div className="aspect-video bg-slate-700 rounded mb-3 flex items-center justify-center">
                      <span className="text-slate-500">Image</span>
                    </div>
                    <h3 className="font-bold text-lg mb-2">{product.name}</h3>
                    <p className="text-slate-400 text-sm mb-3">{product.description}</p>
                    <div className="flex justify-between items-center mb-3">
                      <span className="text-2xl font-bold">${product.price}</span>
                      <span className="text-slate-400 text-sm">Stock: {product.stock || 0}</span>
                    </div>
                    <div className="flex gap-2">
                      <button onClick={() => addToCart(product)} className="flex-1 px-3 py-2 bg-blue-600 rounded hover:bg-blue-700">Add to Cart</button>
                      <button onClick={() => setEditingProduct(product)} className="px-3 py-2 bg-slate-700 rounded hover:bg-slate-600">Edit</button>
                      <button onClick={() => deleteProduct(product.id)} className="px-3 py-2 bg-red-600 rounded hover:bg-red-700">Del</button>
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
              <div className="text-slate-400 text-center py-12">Your cart is empty</div>
            ) : (
              <div>
                {cart.map(item => (
                  <div key={item.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-3 flex justify-between items-center">
                    <div>
                      <h3 className="font-bold">{item.name}</h3>
                      <p className="text-slate-400">Quantity: {item.quantity}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <span className="text-xl font-bold">${(item.price * item.quantity).toFixed(2)}</span>
                      <button onClick={() => removeFromCart(item.id)} className="px-3 py-1 bg-red-600 rounded hover:bg-red-700">Remove</button>
                    </div>
                  </div>
                ))}
                <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mt-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-xl font-bold">Total:</span>
                    <span className="text-2xl font-bold">${cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}</span>
                  </div>
                  <button onClick={checkout} className="w-full px-4 py-3 bg-green-600 rounded hover:bg-green-700 text-lg font-bold">Checkout</button>
                </div>
              </div>
            )}
          </div>
        )}

        {currentPage === 'orders' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Order History</h2>
            {orders.length === 0 ? (
              <div className="text-slate-400 text-center py-12">No orders yet</div>
            ) : (
              orders.map(order => (
                <div key={order.id} className="bg-slate-800 p-4 rounded-lg border border-slate-700 mb-3">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="font-bold">Order #{order.id}</h3>
                      <p className="text-slate-400 text-sm">{order.items?.length || 0} items</p>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">${order.total?.toFixed(2)}</div>
                      <span className="px-2 py-1 bg-yellow-600 rounded text-xs">{order.status}</span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>

      {(showProductForm || editingProduct) && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">{editingProduct ? 'Edit Product' : 'Add Product'}</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.target);
              const data = {
                name: formData.get('name'),
                description: formData.get('description'),
                price: parseFloat(formData.get('price')),
                category: formData.get('category'),
                stock: parseInt(formData.get('stock'))
              };
              editingProduct ? updateProduct(editingProduct.id, data) : addProduct(data);
            }}>
              <input name="name" defaultValue={editingProduct?.name} placeholder="Product Name" required className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded mb-3" />
              <textarea name="description" defaultValue={editingProduct?.description} placeholder="Description" required className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded mb-3" />
              <input name="price" type="number" step="0.01" defaultValue={editingProduct?.price} placeholder="Price" required className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded mb-3" />
              <input name="category" defaultValue={editingProduct?.category} placeholder="Category" required className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded mb-3" />
              <input name="stock" type="number" defaultValue={editingProduct?.stock} placeholder="Stock" required className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded mb-4" />
              <div className="flex gap-2">
                <button type="submit" className="flex-1 px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">Save</button>
                <button type="button" onClick={() => { setShowProductForm(false); setEditingProduct(null); }} className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;