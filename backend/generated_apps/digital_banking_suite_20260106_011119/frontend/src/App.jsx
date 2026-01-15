import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12458.32, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 45230.18, number: '****7890' },
    { id: 'credit', name: 'Credit Card', balance: -2341.50, number: '****1234' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', merchant: 'Amazon Purchase', amount: -156.78, status: 'completed', category: 'Shopping' },
    { id: 2, date: '2024-01-14', merchant: 'Salary Deposit', amount: 5200.00, status: 'completed', category: 'Income' },
    { id: 3, date: '2024-01-13', merchant: 'Netflix Subscription', amount: -15.99, status: 'completed', category: 'Entertainment' },
    { id: 4, date: '2024-01-12', merchant: 'Grocery Store', amount: -87.45, status: 'completed', category: 'Food' },
    { id: 5, date: '2024-01-11', merchant: 'Gas Station', amount: -52.30, status: 'completed', category: 'Transportation' },
    { id: 6, date: '2024-01-10', merchant: 'Transfer to Savings', amount: -1000.00, status: 'completed', category: 'Transfer' },
    { id: 7, date: '2024-01-09', merchant: 'Restaurant', amount: -68.20, status: 'pending', category: 'Food' },
    { id: 8, date: '2024-01-08', merchant: 'Online Payment', amount: -234.50, status: 'completed', category: 'Bills' }
  ];

  const quickActions = [
    { name: 'Transfer Money', icon: '💸' },
    { name: 'Pay Bills', icon: '📄' },
    { name: 'Mobile Deposit', icon: '📱' },
    { name: 'Send Money', icon: '✉️' }
  ];

  const spendingByCategory = [
    { category: 'Food', amount: 155.65, percentage: 28 },
    { category: 'Shopping', amount: 156.78, percentage: 28 },
    { category: 'Bills', amount: 234.50, percentage: 42 },
    { category: 'Entertainment', amount: 15.99, percentage: 3 }
  ];

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
  const recentSpending = transactions.filter(t => t.amount < 0).slice(0, 5).reduce((sum, t) => sum + Math.abs(t.amount), 0);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">💳 SecureBank</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setCurrentPage('dashboard')}
              className={`px-6 py-2 rounded-lg transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button
              onClick={() => setCurrentPage('transactions')}
              className={`px-6 py-2 rounded-lg transition ${currentPage === 'transactions' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Transactions
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-6 rounded-lg shadow-lg">
              <p className="text-blue-200 text-sm mb-1">Total Balance</p>
              <p className="text-3xl font-bold">${totalBalance.toFixed(2)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Recent Spending</p>
              <p className="text-3xl font-bold text-red-400">-${recentSpending.toFixed(2)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Active Accounts</p>
              <p className="text-3xl font-bold">{accounts.length}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Pending Transactions</p>
              <p className="text-3xl font-bold text-yellow-400">{transactions.filter(t => t.status === 'pending').length}</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6 mb-6">
            <div className="col-span-2 bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">My Accounts</h3>
              {accounts.map(account => (
                <div key={account.id} className="bg-slate-700 p-4 rounded-lg mb-3 flex justify-between items-center">
                  <div>
                    <p className="font-semibold">{account.name}</p>
                    <p className="text-sm text-slate-400">{account.number}</p>
                  </div>
                  <p className={`text-xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    ${account.balance.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, idx) => (
                  <button key={idx} className="bg-slate-700 hover:bg-slate-600 p-4 rounded-lg transition text-center">
                    <div className="text-2xl mb-2">{action.icon}</div>
                    <div className="text-xs">{action.name}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
              {transactions.slice(0, 5).map(trans => (
                <div key={trans.id} className="flex justify-between items-center py-3 border-b border-slate-700">
                  <div>
                    <p className="font-semibold">{trans.merchant}</p>
                    <p className="text-xs text-slate-400">{trans.date}</p>
                  </div>
                  <p className={`font-bold ${trans.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    ${trans.amount.toFixed(2)}
                  </p>
                </div>
              ))}
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Spending Analytics</h3>
              {spendingByCategory.map((item, idx) => (
                <div key={idx} className="mb-4">
                  <div className="flex justify-between mb-1">
                    <span className="text-sm">{item.category}</span>
                    <span className="text-sm font-bold">${item.amount.toFixed(2)}</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${item.percentage}%` }}></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Transactions</h2>

          <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700 mb-6">
            <div className="flex gap-4 mb-4">
              <input type="text" placeholder="Search transactions..." className="flex-1 bg-slate-700 px-4 py-2 rounded-lg border border-slate-600 focus:outline-none focus:border-blue-500" />
              <select className="bg-slate-700 px-4 py-2 rounded-lg border border-slate-600">
                <option>All Categories</option>
                <option>Food</option>
                <option>Shopping</option>
                <option>Bills</option>
              </select>
              <select className="bg-slate-700 px-4 py-2 rounded-lg border border-slate-600">
                <option>All Status</option>
                <option>Completed</option>
                <option>Pending</option>
              </select>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider">Date</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider">Merchant</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider">Category</th>
                  <th className="px-6 py-3 text-left text-xs font-semibold uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-semibold uppercase tracking-wider">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-700">
                {transactions.map(trans => (
                  <tr key={trans.id} className="hover:bg-slate-700 transition">
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{trans.date}</td>
                    <td className="px-6 py-4 whitespace-nowrap font-medium">{trans.merchant}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{trans.category}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 rounded-full text-xs ${trans.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                        {trans.status}
                      </span>
                    </td>
                    <td className={`px-6 py-4 whitespace-nowrap text-right font-bold ${trans.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      ${trans.amount.toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;