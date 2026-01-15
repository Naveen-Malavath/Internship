import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12450.75, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 34200.50, number: '****7832' },
    { id: 'credit', name: 'Credit Card', balance: -2340.25, number: '****9104' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', merchant: 'Amazon Purchase', amount: -127.99, status: 'completed', category: 'Shopping' },
    { id: 2, date: '2024-01-14', merchant: 'Salary Deposit', amount: 4500.00, status: 'completed', category: 'Income' },
    { id: 3, date: '2024-01-13', merchant: 'Grocery Store', amount: -85.42, status: 'completed', category: 'Food' },
    { id: 4, date: '2024-01-12', merchant: 'Gas Station', amount: -65.00, status: 'completed', category: 'Transport' },
    { id: 5, date: '2024-01-11', merchant: 'Netflix Subscription', amount: -15.99, status: 'completed', category: 'Entertainment' },
    { id: 6, date: '2024-01-10', merchant: 'Restaurant', amount: -45.50, status: 'pending', category: 'Food' }
  ];

  const recentOrders = [
    { id: 'ORD001', date: '2024-01-15', type: 'Transfer', amount: 500.00, status: 'completed' },
    { id: 'ORD002', date: '2024-01-14', type: 'Payment', amount: 127.99, status: 'completed' },
    { id: 'ORD003', date: '2024-01-10', type: 'Transfer', amount: 1000.00, status: 'pending' }
  ];

  const Dashboard = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Total Balance</p>
          <p className="text-3xl font-bold text-green-400 mt-2">$44,311.00</p>
          <p className="text-xs text-slate-500 mt-2">+2.5% from last month</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Monthly Income</p>
          <p className="text-3xl font-bold text-blue-400 mt-2">$4,500.00</p>
          <p className="text-xs text-slate-500 mt-2">Salary deposited</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Monthly Spending</p>
          <p className="text-3xl font-bold text-red-400 mt-2">$1,267.89</p>
          <p className="text-xs text-slate-500 mt-2">15 transactions</p>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg">
          <p className="text-slate-400 text-sm">Pending Orders</p>
          <p className="text-3xl font-bold text-yellow-400 mt-2">2</p>
          <p className="text-xs text-slate-500 mt-2">Awaiting processing</p>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg">
          <h2 className="text-xl font-bold mb-4">My Accounts</h2>
          {accounts.map(account => (
            <div key={account.id} className="bg-slate-700 p-4 rounded mb-3 flex justify-between items-center">
              <div>
                <p className="font-semibold">{account.name}</p>
                <p className="text-sm text-slate-400">{account.number}</p>
              </div>
              <p className={`text-xl font-bold ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${Math.abs(account.balance).toFixed(2)}
              </p>
            </div>
          ))}
        </div>

        <div className="bg-slate-800 p-6 rounded-lg">
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded text-left">
              <p className="font-semibold">Transfer Money</p>
              <p className="text-sm text-slate-300">Send to another account</p>
            </button>
            <button className="w-full bg-purple-600 hover:bg-purple-700 p-4 rounded text-left">
              <p className="font-semibold">Pay Bills</p>
              <p className="text-sm text-slate-300">Manage your payments</p>
            </button>
            <button className="w-full bg-green-600 hover:bg-green-700 p-4 rounded text-left">
              <p className="font-semibold">Deposit Check</p>
              <p className="text-sm text-slate-300">Mobile deposit</p>
            </button>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Recent Orders</h2>
        <table className="w-full">
          <thead>
            <tr className="text-left border-b border-slate-700">
              <th className="pb-3 text-slate-400">Order ID</th>
              <th className="pb-3 text-slate-400">Date</th>
              <th className="pb-3 text-slate-400">Type</th>
              <th className="pb-3 text-slate-400">Amount</th>
              <th className="pb-3 text-slate-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {recentOrders.map(order => (
              <tr key={order.id} className="border-b border-slate-700">
                <td className="py-3">{order.id}</td>
                <td className="py-3">{order.date}</td>
                <td className="py-3">{order.type}</td>
                <td className="py-3 font-semibold">${order.amount.toFixed(2)}</td>
                <td className="py-3">
                  <span className={`px-3 py-1 rounded text-xs ${order.status === 'completed' ? 'bg-green-600' : 'bg-yellow-600'}`}>
                    {order.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  const Transactions = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Orders & Transactions</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-slate-800 p-4 rounded-lg">
          <p className="text-slate-400 text-sm">Total Transactions</p>
          <p className="text-2xl font-bold mt-2">{transactions.length}</p>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg">
          <p className="text-slate-400 text-sm">Total Spent</p>
          <p className="text-2xl font-bold text-red-400 mt-2">$339.90</p>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg">
          <p className="text-slate-400 text-sm">Total Income</p>
          <p className="text-2xl font-bold text-green-400 mt-2">$4,500.00</p>
        </div>
        <div className="bg-slate-800 p-4 rounded-lg">
          <p className="text-slate-400 text-sm">Pending</p>
          <p className="text-2xl font-bold text-yellow-400 mt-2">1</p>
        </div>
      </div>

      <div className="bg-slate-800 p-6 rounded-lg mb-6">
        <div className="flex gap-4 mb-4">
          <input type="text" placeholder="Search transactions..." className="flex-1 bg-slate-700 px-4 py-2 rounded text-white" />
          <select className="bg-slate-700 px-4 py-2 rounded text-white">
            <option>All Categories</option>
            <option>Shopping</option>
            <option>Food</option>
            <option>Transport</option>
            <option>Entertainment</option>
          </select>
          <select className="bg-slate-700 px-4 py-2 rounded text-white">
            <option>All Status</option>
            <option>Completed</option>
            <option>Pending</option>
          </select>
        </div>
      </div>

      <div className="bg-slate-800 p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">All Transactions</h2>
        <table className="w-full">
          <thead>
            <tr className="text-left border-b border-slate-700">
              <th className="pb-3 text-slate-400">Date</th>
              <th className="pb-3 text-slate-400">Merchant</th>
              <th className="pb-3 text-slate-400">Category</th>
              <th className="pb-3 text-slate-400">Amount</th>
              <th className="pb-3 text-slate-400">Status</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map(txn => (
              <tr key={txn.id} className="border-b border-slate-700 hover:bg-slate-700">
                <td className="py-4">{txn.date}</td>
                <td className="py-4">{txn.merchant}</td>
                <td className="py-4">
                  <span className="px-2 py-1 bg-slate-600 rounded text-xs">{txn.category}</span>
                </td>
                <td className={`py-4 font-bold ${txn.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {txn.amount >= 0 ? '+' : ''}{txn.amount.toFixed(2)}
                </td>
                <td className="py-4">
                  <span className={`px-3 py-1 rounded text-xs ${txn.status === 'completed' ? 'bg-green-600' : 'bg-yellow-600'}`}>
                    {txn.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 border-b border-slate-700">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <div className="flex items-center space-x-6">
            <h1 className="text-2xl font-bold text-blue-400">BankApp</h1>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transactions')}
              className={`px-4 py-2 rounded ${currentPage === 'transactions' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Transactions
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-slate-400">Welcome, John Doe</span>
            <button className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded text-sm">Logout</button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && <Dashboard />}
      {currentPage === 'transactions' && <Transactions />}
    </div>
  );
};

App;

export default App;