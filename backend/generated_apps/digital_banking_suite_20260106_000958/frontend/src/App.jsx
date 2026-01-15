import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12450.32, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 45230.18, number: '****7832' },
    { id: 'credit', name: 'Credit Card', balance: -2340.50, number: '****9901' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Grocery Store', amount: -125.43, status: 'completed', category: 'Food' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 5200.00, status: 'completed', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Electric Bill', amount: -89.32, status: 'completed', category: 'Utilities' },
    { id: 4, date: '2024-01-12', description: 'Online Transfer', amount: -500.00, status: 'pending', category: 'Transfer' },
    { id: 5, date: '2024-01-11', description: 'Restaurant', amount: -67.89, status: 'completed', category: 'Food' },
    { id: 6, date: '2024-01-10', description: 'Gas Station', amount: -45.00, status: 'completed', category: 'Transport' }
  ];

  const metrics = [
    { label: 'Total Balance', value: '$55,339.00', change: '+2.4%', positive: true },
    { label: 'Monthly Income', value: '$5,200.00', change: '+0.5%', positive: true },
    { label: 'Monthly Expenses', value: '$2,847.64', change: '-5.2%', positive: true },
    { label: 'Pending Transactions', value: '3', change: '+1', positive: false }
  ];

  const quickActions = [
    { icon: '💸', label: 'Transfer Money', action: 'transfer' },
    { icon: '💳', label: 'Pay Bills', action: 'bills' },
    { icon: '📊', label: 'View Reports', action: 'reports' },
    { icon: '⚙️', label: 'Settings', action: 'settings' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-8">
            <h1 className="text-2xl font-bold text-blue-400">🏦 Digital Bank</h1>
            <div className="flex space-x-2">
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`px-4 py-2 rounded transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentPage('transactions')}
                className={`px-4 py-2 rounded transition ${currentPage === 'transactions' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
              >
                Transactions
              </button>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-slate-400">Welcome, John Doe</span>
            <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">Logout</button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="p-6">
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-2">Account Overview</h2>
            <p className="text-slate-400">Manage your accounts and view your financial summary</p>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            {metrics.map((metric, index) => (
              <div key={index} className="bg-slate-800 border border-slate-700 rounded-lg p-5">
                <p className="text-slate-400 text-sm mb-1">{metric.label}</p>
                <p className="text-2xl font-bold mb-2">{metric.value}</p>
                <span className={`text-sm ${metric.positive ? 'text-green-400' : 'text-red-400'}`}>
                  {metric.change}
                </span>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-3 gap-6 mb-6">
            {accounts.map((account) => (
              <div
                key={account.id}
                onClick={() => setSelectedAccount(account.id)}
                className={`bg-gradient-to-br from-blue-600 to-blue-800 rounded-lg p-6 cursor-pointer transition transform hover:scale-105 ${selectedAccount === account.id ? 'ring-4 ring-blue-400' : ''}`}
              >
                <p className="text-sm opacity-90 mb-2">{account.name}</p>
                <p className="text-3xl font-bold mb-3">${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}</p>
                <p className="text-sm opacity-75">{account.number}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, index) => (
                  <button
                    key={index}
                    className="bg-slate-700 hover:bg-slate-600 rounded-lg p-4 text-left transition"
                  >
                    <div className="text-3xl mb-2">{action.icon}</div>
                    <div className="text-sm font-medium">{action.label}</div>
                  </button>
                ))}
              </div>
            </div>

            <div className="bg-slate-800 border border-slate-700 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {transactions.slice(0, 4).map((transaction) => (
                  <div key={transaction.id} className="flex justify-between items-center py-2 border-b border-slate-700">
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-slate-400">{transaction.date}</p>
                    </div>
                    <span className={`font-bold ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="p-6">
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-2">Transactions & Orders</h2>
            <p className="text-slate-400">View and manage all your transactions</p>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg p-6 mb-6">
            <div className="flex space-x-4 mb-4">
              <input
                type="text"
                placeholder="Search transactions..."
                className="flex-1 bg-slate-700 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <select className="bg-slate-700 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>All Categories</option>
                <option>Food</option>
                <option>Utilities</option>
                <option>Transport</option>
                <option>Income</option>
              </select>
              <select className="bg-slate-700 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500">
                <option>All Status</option>
                <option>Completed</option>
                <option>Pending</option>
              </select>
            </div>
          </div>

          <div className="bg-slate-800 border border-slate-700 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="text-left px-6 py-4 font-semibold">Date</th>
                  <th className="text-left px-6 py-4 font-semibold">Description</th>
                  <th className="text-left px-6 py-4 font-semibold">Category</th>
                  <th className="text-left px-6 py-4 font-semibold">Status</th>
                  <th className="text-right px-6 py-4 font-semibold">Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction) => (
                  <tr key={transaction.id} className="border-t border-slate-700 hover:bg-slate-750">
                    <td className="px-6 py-4 text-slate-300">{transaction.date}</td>
                    <td className="px-6 py-4 font-medium">{transaction.description}</td>
                    <td className="px-6 py-4">
                      <span className="px-3 py-1 bg-slate-700 rounded-full text-sm">{transaction.category}</span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${transaction.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                        {transaction.status}
                      </span>
                    </td>
                    <td className={`px-6 py-4 text-right font-bold ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="flex justify-between items-center mt-6">
            <p className="text-slate-400">Showing {transactions.length} transactions</p>
            <div className="flex space-x-2">
              <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">Previous</button>
              <button className="px-4 py-2 bg-blue-600 rounded">1</button>
              <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">2</button>
              <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">Next</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;