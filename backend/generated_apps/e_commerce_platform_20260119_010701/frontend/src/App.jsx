import React from 'react';

const { useState, useEffect } = React;

const API_BASE_URL = 'http://localhost:8000';

const App = () => {
  const [currentPage, setCurrentPage] = useState('products');
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [cart, setCart] = useState([]);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [showAddProductModal, setShowAddProductModal] = useState(false);

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    setLoading(true);
    try {
      const [productsRes, ordersRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/products`),
        fetch(`${API_BASE_URL}/api/orders`)
      ]);
      
      if (productsRes.ok) {
        const productsData = await productsRes.json();
        setProducts(Array.isArray(productsData) ? productsData : []);
      }
      
      if (ordersRes.ok) {
        const ordersData = await ordersRes.json();
        setOrders(Array.isArray(ordersData) ? ordersData : []);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const addProduct = async (productData) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/products`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(productData)
      });
      
      if (res.ok) {
        const newProduct = await res.json();
        setProducts([...products, newProduct]);
        setShowAddProductModal(false);
      } else {
        setError('Failed to add product');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const deleteProduct = async (id) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/products/${id}`, {
        method: 'DELETE'
      });
      
      if (res.ok) {
        setProducts(products.filter(p => p.id !== id));
      } else {
        setError('Failed to delete product');
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const updateProduct = async (id, updates) => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/products/${id}`, {
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
      setCart(cart.map(item => 
        item.id === product.id 
          ? { ...item, quantity: item.quantity + 1 }
          : item
      ));
    } else {
      setCart([...cart, { ...product, quantity: 1 }]);
    }
  };

  const removeFromCart = (productId) => {
    setCart(cart.filter(item => item.id !== productId));
  };

  const createOrder = async () => {
    const orderData = {
      items: cart,
      total: cart.reduce((sum, item) => sum + (item.price * item.quantity), 0),
      status: 'pending',
      created_at: new Date().toISOString()
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/orders`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
      });
      
      if (res.ok) {
        const newOrder = await res.json();
        setOrders([...orders, newOrder]);
        setCart([]);
        setCurrentPage('orders');
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

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">E-Commerce Platform</h1>
          <div className="flex gap-4">
            <button onClick={() => setCurrentPage('products')} className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700'}`}>Products</button>
            <button onClick={() => setCurrentPage('admin')} className={`px-4 py-2 rounded ${currentPage === 'admin' ? 'bg-blue-600' : 'bg-slate-700'}`}>Admin Dashboard</button>
            <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700'}`}>Cart ({cart.length})</button>
            <button onClick={() => setCurrentPage('orders')} className={`px-4 py-2 rounded ${currentPage === 'orders' ? 'bg-blue-600' : 'bg-slate-700'}`}>Orders</button>
          </div>
        </div>
      </nav>

      {error && (
        <div className="bg-red-500 text-white px-6 py-3 text-center">
          Error: {error} <button onClick={() => setError(null)} className="ml-4 underline">Dismiss</button>
        </div>
      )}

      <main className="p-6">
        {currentPage === 'products' && (
          <div>
            <div className="mb-6 flex gap-4">
              <input
                type="text"
                placeholder="Search products..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white"
              />
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="px-4 py-2 bg-slate-800 border border-slate-700 rounded text-white"
              >
                <option value="all">All Categories</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-6">
              {filteredProducts.map(product => (
                <div key={product.id} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
                  <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                  <p className="text-slate-400 mb-2">{product.category}</p>
                  <p className="text-sm text-slate-300 mb-4">{product.description}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-green-400">${product.price}</span>
                    <button
                      onClick={() => addToCart(product)}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                    >
                      Add to Cart
                    </button>
                  </div>
                  <div className="mt-2 text-sm text-slate-400">Stock: {product.stock || 0}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {currentPage === 'admin' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold">Admin Dashboard</h2>
              <button
                onClick={() => setShowAddProductModal(true)}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded"
              >
                Add Product
              </button>
            </div>

            <div className="grid grid-cols-3 gap-6 mb-8">
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="text-slate-400 mb-2">Total Products</div>
                <div className="text-4xl font-bold">{products.length}</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="text-slate-400 mb-2">Total Orders</div>
                <div className="text-4xl font-bold">{orders.length}</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="text-slate-400 mb-2">Revenue</div>
                <div className="text-4xl font-bold">${orders.reduce((sum, o) => sum + (o.total || 0), 0).toFixed(2)}</div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-4 py-3 text-left">ID</th>
                    <th className="px-4 py-3 text-left">Name</th>
                    <th className="px-4 py-3 text-left">Category</th>
                    <th className="px-4 py-3 text-left">Price</th>
                    <th className="px-4 py-3 text-left">Stock</th>
                    <th className="px-4 py-3 text-left">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(product => (
                    <tr key={product.id} className="border-t border-slate-700">
                      <td className="px-4 py-3">{product.id}</td>
                      <td className="px-4 py-3">{product.name}</td>
                      <td className="px-4 py-3">{product.category}</td>
                      <td className="px-4 py-3">${product.price}</td>
                      <td className="px-4 py-3">{product.stock}</td>
                      <td className="px-4 py-3">
                        <button
                          onClick={() => deleteProduct(product.id)}
                          className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {showAddProductModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                <div className="bg-slate-800 p-6 rounded-lg w-full max-w-md">
                  <h3 className="text-2xl font-bold mb-4">Add New Product</h3>
                  <form onSubmit={(e) => {
                    e.preventDefault();
                    const formData = new FormData(e.target);
                    addProduct({
                      name: formData.get('name'),
                      category: formData.get('category'),
                      description: formData.get('description'),
                      price: parseFloat(formData.get('price')),
                      stock: parseInt(formData.get('stock'))
                    });
                  }}>
                    <input name="name" placeholder="Product Name" required className="w-full px-4 py-2 mb-3 bg-slate-700 border border-slate-600 rounded text-white" />
                    <input name="category" placeholder="Category" required className="w-full px-4 py-2 mb-3 bg-slate-700 border border-slate-600 rounded text-white" />
                    <textarea name="description" placeholder="Description" required className="w-full px-4 py-2 mb-3 bg-slate-700 border border-slate-600 rounded text-white" />
                    <input name="price" type="number" step="0.01" placeholder="Price" required className="w-full px-4 py-2 mb-3 bg-slate-700 border border-slate-600 rounded text-white" />
                    <input name="stock" type="number" placeholder="Stock" required className="w-full px-4 py-2 mb-3 bg-slate-700 border border-slate-600 rounded text-white" />
                    <div className="flex gap-3">
                      <button type="submit" className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 rounded">Add</button>
                      <button type="button" onClick={() => setShowAddProductModal(false)} className="flex-1 px-4 py-2 bg-slate-600 hover:bg-slate-700 rounded">Cancel</button>
                    </div>
                  </form>
                </div>
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
                {cart.map(item => (
                  <div key={item.id} className="bg-slate-800 p-4 rounded-lg mb-4 flex justify-between items-center">
                    <div>
                      <h3 className="text-xl font-bold">{item.name}</h3>
                      <p className="text-slate-400">Quantity: {item.quantity}</p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-green-400">${(item.price * item.quantity).toFixed(2)}</div>
                      <button onClick={() => removeFromCart(item.id)} className="mt-2 px-4 py-1 bg-red-600 hover:bg-red-700 rounded text-sm">Remove</button>
                    </div>
                  </div>
                ))}
                <div className="bg-slate-800 p-6 rounded-lg mt-6">
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-2xl font-bold">Total:</span>
                    <span className="text-3xl font-bold text-green-400">${cart.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}</span>
                  </div>
                  <button onClick={createOrder} className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded text-xl font-bold">Checkout</button>
                </div>
              </div>
            )}
          </div>
        )}

        {currentPage === 'orders' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Order History</h2>
            {orders.length === 0 ? (
              <div className="text-center text-slate-400 py-12">No orders yet</div>
            ) : (
              <div className="space-y-4">
                {orders.map((order, idx) => (
                  <div key={order.id || idx} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <div className="text-lg font-bold">Order #{order.id || idx + 1}</div>
                        <div className="text-sm text-slate-400">{order.created_at ? new Date(order.created_at).toLocaleDateString() : 'Recent'}</div>
                      </div>
                      <div className="text-right">
                        <div className="text-2xl font-bold text-green-400">${order.total?.toFixed(2)}</div>
                        <div className="text-sm text-blue-400 capitalize">{order.status || 'pending'}</div>
                      </div>
                    </div>
                    {order.items && (
                      <div className="text-sm text-slate-400">
                        {order.items.length} item(s)
                      </div>
                    )}
                  </div>
                ))}
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