import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [cartItems, setCartItems] = React.useState([]);

  const accounts = [
    { id: 1, name: 'Checking Account', balance: 15420.50, type: 'checking' },
    { id: 2, name: 'Savings Account', balance: 48750.25, type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -2340.00, type: 'credit' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', merchant: 'Amazon', amount: -89.99, category: 'Shopping' },
    { id: 2, date: '2024-01-14', merchant: 'Salary Deposit', amount: 5000.00, category: 'Income' },
    { id: 3, date: '2024-01-13', merchant: 'Starbucks', amount: -12.50, category: 'Food' },
    { id: 4, date: '2024-01-12', merchant: 'Shell Gas', amount: -45.00, category: 'Transport' }
  ];

  const products = [
    { id: 1, name: 'Premium Savings Plan', price: 0, description: 'High-yield savings account', category: 'Savings' },
    { id: 2, name: 'Investment Portfolio', price: 500, description: 'Managed investment service', category: 'Investment' },
    { id: 3, name: 'Travel Insurance', price: 299, description: 'Comprehensive travel coverage', category: 'Insurance' },
    { id: 4, name: 'Credit Card Plus', price: 0, description: '2% cashback on all purchases', category: 'Credit' }
  ];

  const addToCart = (product) => {
    setCartItems([...cartItems, product]);
  };

  const removeFromCart = (productId) => {
    setCartItems(cartItems.filter(item => item.id !== productId));
  };

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg">
        <div className="container mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">Digital Banking Suite</h1>
          <div className="flex gap-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('products')}
              className={`px-4 py-2 rounded ${currentPage === 'products' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Products
            </button>
            <button 
              onClick={() => setCurrentPage('cart')}
              className={`px-4 py-2 rounded relative ${currentPage === 'cart' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Cart ({cartItems.length})
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-gray-400 text-sm mb-2">Total Balance</h3>
              <p className="text-3xl font-bold text-green-400">${totalBalance.toFixed(2)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-gray-400 text-sm mb-2">Accounts</h3>
              <p className="text-3xl font-bold">{accounts.length}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-gray-400 text-sm mb-2">Transactions</h3>
              <p className="text-3xl font-bold">{transactions.length}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-gray-400 text-sm mb-2">Monthly Spending</h3>
              <p className="text-3xl font-bold text-red-400">$147.49</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4">Your Accounts</h3>
              {accounts.map(account => (
                <div key={account.id} className="flex justify-between items-center mb-4 p-4 bg-slate-700 rounded">
                  <div>
                    <p className="font-semibold">{account.name}</p>
                    <p className="text-sm text-gray-400">{account.type}</p>
                  </div>
                  <p className={`text-xl font-bold ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${Math.abs(account.balance).toFixed(2)}
                  </p>
                </div>
              ))}
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
              <div className="space-y-3">
                {transactions.map(txn => (
                  <div key={txn.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                    <div>
                      <p className="font-semibold">{txn.merchant}</p>
                      <p className="text-sm text-gray-400">{txn.date} • {txn.category}</p>
                    </div>
                    <p className={`font-bold ${txn.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {txn.amount >= 0 ? '+' : ''}{txn.amount.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'products' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Banking Products & Services</h2>
          
          <div className="grid grid-cols-4 gap-6">
            {products.map(product => (
              <div key={product.id} className="bg-slate-800 p-6 rounded-lg shadow-lg flex flex-col">
                <div className="mb-2">
                  <span className="text-xs bg-blue-600 px-2 py-1 rounded">{product.category}</span>
                </div>
                <h3 className="text-xl font-bold mb-2">{product.name}</h3>
                <p className="text-gray-400 text-sm mb-4 flex-grow">{product.description}</p>
                <div className="flex justify-between items-center">
                  <p className="text-2xl font-bold text-green-400">
                    {product.price === 0 ? 'Free' : `$${product.price}`}
                  </p>
                  <button 
                    onClick={() => addToCart(product)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded"
                  >
                    Add
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {currentPage === 'cart' && (
        <div className="container mx-auto p-8">
          <h2 className="text-3xl font-bold mb-6">Your Cart</h2>
          
          {cartItems.length === 0 ? (
            <div className="bg-slate-800 p-12 rounded-lg text-center">
              <p className="text-xl text-gray-400">Your cart is empty</p>
              <button 
                onClick={() => setCurrentPage('products')}
                className="mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-700 rounded"
              >
                Browse Products
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-3 gap-6">
              <div className="col-span-2 bg-slate-800 p-6 rounded-lg">
                <h3 className="text-xl font-bold mb-4">Items</h3>
                {cartItems.map((item, index) => (
                  <div key={index} className="flex justify-between items-center mb-4 p-4 bg-slate-700 rounded">
                    <div>
                      <p className="font-semibold">{item.name}</p>
                      <p className="text-sm text-gray-400">{item.description}</p>
                    </div>
                    <div className="flex items-center gap-4">
                      <p className="text-xl font-bold">{item.price === 0 ? 'Free' : `$${item.price}`}</p>
                      <button 
                        onClick={() => removeFromCart(item.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 rounded text-sm"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-slate-800 p-6 rounded-lg h-fit">
                <h3 className="text-xl font-bold mb-4">Order Summary</h3>
                <div className="space-y-3 mb-4">
                  <div className="flex justify-between">
                    <span>Items:</span>
                    <span>{cartItems.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Subtotal:</span>
                    <span>${cartItems.reduce((sum, item) => sum + item.price, 0).toFixed(2)}</span>
                  </div>
                  <div className="border-t border-slate-700 pt-3 flex justify-between font-bold text-xl">
                    <span>Total:</span>
                    <span className="text-green-400">${cartItems.reduce((sum, item) => sum + item.price, 0).toFixed(2)}</span>
                  </div>
                </div>
                <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 rounded font-bold">
                  Proceed to Checkout
                </button>
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