import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12543.82, type: 'checking' },
    { id: 'savings', name: 'Savings Account', balance: 45230.15, type: 'savings' },
    { id: 'credit', name: 'Credit Card', balance: -2341.50, type: 'credit' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Grocery Store', amount: -125.43, category: 'Shopping', status: 'completed' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 4500.00, category: 'Income', status: 'completed' },
    { id: 3, date: '2024-01-13', description: 'Electric Bill', amount: -89.32, category: 'Utilities', status: 'completed' },
    { id: 4, date: '2024-01-12', description: 'Restaurant', amount: -67.80, category: 'Dining', status: 'completed' },
    { id: 5, date: '2024-01-11', description: 'Gas Station', amount: -52.15, category: 'Transport', status: 'completed' },
    { id: 6, date: '2024-01-10', description: 'Online Transfer', amount: -500.00, category: 'Transfer', status: 'pending' }
  ];

  const quickActions = [
    { id: 1, name: 'Send Money', icon: '💸' },
    { id: 2, name: 'Pay Bills', icon: '📄' },
    { id: 3, name: 'Mobile Recharge', icon: '📱' },
    { id: 4, name: 'Investments', icon: '📈' }
  ];

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-6">
            <h1 className="text-xl font-bold text-blue-400">💳 BankPro</h1>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transactions')}
              className={`px-4 py-2 rounded ${currentPage === 'transactions' ? 'bg-blue-600' : 'hover:bg-slate-700'}`}
            >
              Transactions
            </button>
          </div>
          <div className="flex items-center space-x-4">
            <span className="text-sm text-slate-400">Welcome, John Doe</span>
            <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600">Logout</button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="max-w-7xl mx-auto p-6">
          <h2 className="text-2xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-lg shadow-lg col-span-2">
              <div className="text-sm text-blue-200 mb-2">Total Balance</div>
              <div className="text-3xl font-bold">${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
              <div className="text-sm text-blue-200 mt-2">Across all accounts</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <div className="text-sm text-slate-400 mb-2">Monthly Income</div>
              <div className="text-2xl font-bold text-green-400">$4,500</div>
              <div className="text-xs text-slate-500 mt-2">+12% vs last month</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <div className="text-sm text-slate-400 mb-2">Monthly Expenses</div>
              <div className="text-2xl font-bold text-red-400">$2,834</div>
              <div className="text-xs text-slate-500 mt-2">-5% vs last month</div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6 mb-8">
            <div className="col-span-2">
              <h3 className="text-xl font-semibold mb-4">My Accounts</h3>
              <div className="space-y-4">
                {accounts.map(account => (
                  <div key={account.id} className="bg-slate-800 p-5 rounded-lg flex items-center justify-between hover:bg-slate-750 cursor-pointer">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-xl">
                        {account.type === 'checking' ? '🏦' : account.type === 'savings' ? '💰' : '💳'}
                      </div>
                      <div>
                        <div className="font-semibold">{account.name}</div>
                        <div className="text-sm text-slate-400">****{account.id.slice(-4)}</div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                        ${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-xs text-slate-400">{account.balance < 0 ? 'Outstanding' : 'Available'}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map(action => (
                  <button key={action.id} className="bg-slate-800 p-4 rounded-lg hover:bg-slate-700 transition text-center">
                    <div className="text-3xl mb-2">{action.icon}</div>
                    <div className="text-sm">{action.name}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-xl font-semibold mb-4">Recent Transactions</h3>
            <div className="bg-slate-800 rounded-lg overflow-hidden">
              {transactions.slice(0, 5).map(tx => (
                <div key={tx.id} className="p-4 border-b border-slate-700 last:border-b-0 flex items-center justify-between hover:bg-slate-750">
                  <div className="flex items-center space-x-4">
                    <div className={`w-10 h-10 rounded-full flex items-center justify-center ${tx.amount > 0 ? 'bg-green-600' : 'bg-red-600'}`}>
                      {tx.amount > 0 ? '↓' : '↑'}
                    </div>
                    <div>
                      <div className="font-medium">{tx.description}</div>
                      <div className="text-sm text-slate-400">{tx.date} • {tx.category}</div>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className={`font-bold ${tx.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {tx.amount > 0 ? '+' : ''}{tx.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                    <div className={`text-xs ${tx.status === 'pending' ? 'text-yellow-400' : 'text-slate-400'}`}>
                      {tx.status}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="max-w-7xl mx-auto p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold">All Transactions</h2>
            <div className="flex items-center space-x-3">
              <select className="bg-slate-800 border border-slate-700 rounded px-4 py-2">
                <option>All Accounts</option>
                <option>Checking</option>
                <option>Savings</option>
                <option>Credit Card</option>
              </select>
              <input type="text" placeholder="Search transactions..." className="bg-slate-800 border border-slate-700 rounded px-4 py-2 w-64" />
            </div>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 p-4 rounded-lg">
              <div className="text-sm text-slate-400 mb-1">Total Income</div>
              <div className="text-xl font-bold text-green-400">$4,500.00</div>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <div className="text-sm text-slate-400 mb-1">Total Expenses</div>
              <div className="text-xl font-bold text-red-400">$834.70</div>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <div className="text-sm text-slate-400 mb-1">Net Balance</div>
              <div className="text-xl font-bold text-blue-400">$3,665.30</div>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg">
              <div className="text-sm text-slate-400 mb-1">Pending</div>
              <div className="text-xl font-bold text-yellow-400">1</div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="text-left p-4 font-semibold">Date</th>
                  <th className="text-left p-4 font-semibold">Description</th>
                  <th className="text-left p-4 font-semibold">Category</th>
                  <th className="text-left p-4 font-semibold">Status</th>
                  <th className="text-right p-4 font-semibold">Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(tx => (
                  <tr key={tx.id} className="border-b border-slate-700 hover:bg-slate-750">
                    <td className="p-4 text-slate-300">{tx.date}</td>
                    <td className="p-4">{tx.description}</td>
                    <td className="p-4">
                      <span className="bg-slate-700 px-3 py-1 rounded-full text-sm">{tx.category}</span>
                    </td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-sm ${tx.status === 'pending' ? 'bg-yellow-600' : 'bg-green-600'}`}>
                        {tx.status}
                      </span>
                    </td>
                    <td className={`p-4 text-right font-bold ${tx.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {tx.amount > 0 ? '+' : ''}{tx.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}
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