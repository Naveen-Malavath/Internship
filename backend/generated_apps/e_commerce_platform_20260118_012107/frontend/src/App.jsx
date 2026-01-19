import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('catalog');
  const [cart, setCart] = React.useState([]);
  const [searchTerm, setSearchTerm] = React.useState('');
  const [selectedCategory, setSelectedCategory] = React.useState('all');
  const [isLoggedIn, setIsLoggedIn] = React.useState(true);

  const products = [
    { id: 1, name: 'Wireless Headphones', price: 99.99, category: 'electronics', rating: 4.5, reviews: 128, image: '🎧' },
    { id: 2, name: 'Smart Watch', price: 249.99, category: 'electronics', rating: 4.7, reviews: 89, image: '⌚' },
    { id: 3, name: 'Running Shoes', price: 79.99, category: 'sports', rating: 4.3, reviews: 234, image: '👟' },
    { id: 4, name: 'Yoga Mat', price: 29.99, category: 'sports', rating: 4.6, reviews: 156, image: '🧘' },
    { id: 5, name: 'Coffee Maker', price: 149.99, category: 'home', rating: 4.4, reviews: 92, image: '☕' },
    { id: 6, name: 'Desk Lamp', price: 39.99, category: 'home', rating: 4.2, reviews: 67, image: '💡' },
    { id: 7, name: 'Laptop Stand', price: 49.99, category: 'electronics', rating: 4.8, reviews: 203, image: '💻' },
    { id: 8, name: 'Water Bottle', price: 19.99, category: 'sports', rating: 4.5, reviews: 412, image: '💧' }
  ];

  const orders = [
    { id: 1001, date: '2024-01-15', total: 329.97, status: 'Delivered', items: 3 },
    { id: 1002, date: '2024-01-20', total: 149.99, status: 'Shipped', items: 1 },
    { id: 1003, date: '2024-01-25', total: 79.99, status: 'Processing', items: 1 }
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

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
    } else {
      setCart(cart.map(item => item.id === productId ? { ...item, quantity: newQuantity } : item));
    }
  };

  const filteredProducts = products.filter(p => 
    (selectedCategory === 'all' || p.category === selectedCategory) &&
    (searchTerm === '' || p.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const cartTotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold">🛍️ ShopHub</h1>
          <div className="flex gap-2">
            <button onClick={() => setCurrentPage('catalog')} className={`px-4 py-2 rounded ${currentPage === 'catalog' ? 'bg-blue-600' : 'bg-slate-700'}`}>Catalog</button>
            <button onClick={() => setCurrentPage('dashboard')} className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}>Dashboard</button>
            <button onClick={() => setCurrentPage('cart')} className={`px-4 py-2 rounded ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700'} relative`}>
              Cart {cart.length > 0 && <span className="absolute -top-1 -right-1 bg-red-500 text-xs rounded-full w-5 h-5 flex items-center justify-center">{cart.length}</span>}
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'catalog' && (
        <div className="container mx-auto p-6">
          <div className="mb-6 flex gap-4">
            <input type="text" placeholder="Search products..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="flex-1 px-4 py-2 bg-slate-800 rounded border border-slate-700 focus:border-blue-500 outline-none" />
            <select value={selectedCategory} onChange={(e) => setSelectedCategory(e.target.value)} className="px-4 py-2 bg-slate-800 rounded border border-slate-700 outline-none">
              <option value="all">All Categories</option>
              <option value="electronics">Electronics</option>
              <option value="sports">Sports</option>
              <option value="home">Home</option>
            </select>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {filteredProducts.map(product => (
              <div key={product.id} className="bg-slate-800 rounded-lg p-4 hover:bg-slate-750 transition">
                <div className="text-6xl text-center mb-4">{product.image}</div>
                <h3 className="text-lg font-semibold mb-2">{product.name}</h3>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-yellow-400">★ {product.rating}</span>
                  <span className="text-slate-400 text-sm">({product.reviews})</span>
                </div>
                <p className="text-2xl font-bold text-blue-400 mb-4">${product.price}</p>
                <button onClick={() => addToCart(product)} className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded transition">Add to Cart</button>
              </div>
            ))}
          </div>
        </div>
      )}

      {currentPage === 'dashboard' && (
        <div className="container mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Customer Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 mb-2">Total Orders</h3>
              <p className="text-3xl font-bold">{orders.length}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 mb-2">Total Spent</h3>
              <p className="text-3xl font-bold">${orders.reduce((sum, o) => sum + o.total, 0).toFixed(2)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 mb-2">Active Orders</h3>
              <p className="text-3xl font-bold">{orders.filter(o => o.status !== 'Delivered').length}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-slate-400 mb-2">Cart Items</h3>
              <p className="text-3xl font-bold">{cart.length}</p>
            </div>
          </div>

          <h3 className="text-2xl font-bold mb-4">Order History</h3>
          <div className="bg-slate-800 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="text-left p-4">Order ID</th>
                  <th className="text-left p-4">Date</th>
                  <th className="text-left p-4">Items</th>
                  <th className="text-left p-4">Total</th>
                  <th className="text-left p-4">Status</th>
                </tr>
              </thead>
              <tbody>
                {orders.map(order => (
                  <tr key={order.id} className="border-t border-slate-700">
                    <td className="p-4">#{order.id}</td>
                    <td className="p-4">{order.date}</td>
                    <td className="p-4">{order.items}</td>
                    <td className="p-4">${order.total.toFixed(2)}</td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${order.status === 'Delivered' ? 'bg-green-600' : order.status === 'Shipped' ? 'bg-blue-600' : 'bg-yellow-600'}`}>
                        {order.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {currentPage === 'cart' && (
        <div className="container mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Shopping Cart</h2>
          
          {cart.length === 0 ? (
            <div className="bg-slate-800 p-12 rounded-lg text-center">
              <p className="text-xl text-slate-400 mb-4">Your cart is empty</p>
              <button onClick={() => setCurrentPage('catalog')} className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded transition">Continue Shopping</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 space-y-4">
                {cart.map(item => (
                  <div key={item.id} className="bg-slate-800 p-4 rounded-lg flex items-center gap-4">
                    <div className="text-4xl">{item.image}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-lg">{item.name}</h3>
                      <p className="text-blue-400">${item.price}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <button onClick={() => updateQuantity(item.id, item.quantity - 1)} className="bg-slate-700 w-8 h-8 rounded hover:bg-slate-600">-</button>
                      <span className="w-12 text-center">{item.quantity}</span>
                      <button onClick={() => updateQuantity(item.id, item.quantity + 1)} className="bg-slate-700 w-8 h-8 rounded hover:bg-slate-600">+</button>
                    </div>
                    <p className="font-bold w-24 text-right">${(item.price * item.quantity).toFixed(2)}</p>
                    <button onClick={() => removeFromCart(item.id)} className="text-red-400 hover:text-red-300">✕</button>
                  </div>
                ))}
              </div>
              
              <div className="bg-slate-800 p-6 rounded-lg h-fit">
                <h3 className="text-xl font-bold mb-4">Order Summary</h3>
                <div className="space-y-2 mb-4">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Subtotal</span>
                    <span>${cartTotal.toFixed(2)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Shipping</span>
                    <span>$10.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Tax</span>
                    <span>${(cartTotal * 0.1).toFixed(2)}</span>
                  </div>
                  <div className="border-t border-slate-700 pt-2 mt-2">
                    <div className="flex justify-between text-xl font-bold">
                      <span>Total</span>
                      <span>${(cartTotal + 10 + cartTotal * 0.1).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
                <button className="w-full bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded font-semibold transition">Proceed to Checkout</button>
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