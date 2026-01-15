import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12543.67, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 45230.12, number: '****7890' },
    { id: 'credit', name: 'Credit Card', balance: -2341.50, number: '****3456' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Amazon Purchase', amount: -156.32, status: 'completed', category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 5400.00, status: 'completed', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Electric Bill', amount: -125.67, status: 'completed', category: 'Utilities' },
    { id: 4, date: '2024-01-12', description: 'Restaurant', amount: -87.45, status: 'completed', category: 'Dining' },
    { id: 5, date: '2024-01-11', description: 'Gas Station', amount: -52.30, status: 'completed', category: 'Transport' },
    { id: 6, date: '2024-01-10', description: 'Transfer to Savings', amount: -1000.00, status: 'pending', category: 'Transfer' }
  ];

  const quickActions = [
    { name: 'Send Money', icon: '💸' },
    { name: 'Pay Bills', icon: '📄' },
    { name: 'Deposit Check', icon: '📷' },
    { name: 'Transfer', icon: '🔄' }
  ];

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
  const monthlyIncome = 5400.00;
  const monthlyExpenses = 421.74;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="text-2xl">🏦</span>
            <h1 className="text-xl font-bold">SecureBank</h1>
          </div>
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
          <div className="flex items-center space-x-3">
            <span className="text-sm text-slate-400">John Doe</span>
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">JD</div>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-600 to-blue-800 p-6 rounded-lg shadow-lg">
              <div className="text-sm text-blue-200 mb-1">Total Balance</div>
              <div className="text-3xl font-bold">${totalBalance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">Monthly Income</div>
              <div className="text-2xl font-bold text-green-400">+${monthlyIncome.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">Monthly Expenses</div>
              <div className="text-2xl font-bold text-red-400">-${monthlyExpenses.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">Accounts</div>
              <div className="text-2xl font-bold">{accounts.length}</div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6 mb-6">
            <div className="col-span-2">
              <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                <h3 className="text-xl font-bold mb-4">My Accounts</h3>
                <div className="space-y-3">
                  {accounts.map(account => (
                    <div key={account.id} className="bg-slate-700 p-4 rounded-lg flex justify-between items-center hover:bg-slate-600 transition cursor-pointer" onClick={() => setSelectedAccount(account.id)}>
                      <div>
                        <div className="font-semibold">{account.name}</div>
                        <div className="text-sm text-slate-400">{account.number}</div>
                      </div>
                      <div className={`text-xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                        ${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                {quickActions.map((action, idx) => (
                  <button key={idx} className="bg-slate-700 hover:bg-blue-600 p-4 rounded-lg transition text-center">
                    <div className="text-2xl mb-2">{action.icon}</div>
                    <div className="text-sm">{action.name}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
            <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
            <div className="space-y-2">
              {transactions.slice(0, 5).map(transaction => (
                <div key={transaction.id} className="bg-slate-700 p-4 rounded flex justify-between items-center">
                  <div className="flex-1">
                    <div className="font-semibold">{transaction.description}</div>
                    <div className="text-sm text-slate-400">{transaction.date} • {transaction.category}</div>
                  </div>
                  <div className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Transactions & Orders</h2>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">Total Transactions</div>
              <div className="text-2xl font-bold">{transactions.length}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">Completed</div>
              <div className="text-2xl font-bold text-green-400">{transactions.filter(t => t.status === 'completed').length}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">Pending</div>
              <div className="text-2xl font-bold text-yellow-400">{transactions.filter(t => t.status === 'pending').length}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <div className="text-sm text-slate-400 mb-1">This Month</div>
              <div className="text-2xl font-bold">${monthlyExpenses.toFixed(2)}</div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">Filter Transactions</h3>
            </div>
            <div className="grid grid-cols-4 gap-4">
              <input type="text" placeholder="Search transactions..." className="bg-slate-700 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500" />
              <select className="bg-slate-700 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500">
                <option>All Categories</option>
                <option>Shopping</option>
                <option>Dining</option>
                <option>Utilities</option>
                <option>Transport</option>
              </select>
              <select className="bg-slate-700 border border-slate-600 rounded px-4 py-2 focus:outline-none focus:border-blue-500">
                <option>All Status</option>
                <option>Completed</option>
                <option>Pending</option>
              </select>
              <button className="bg-blue-600 hover:bg-blue-700 rounded px-4 py-2 transition">Apply Filters</button>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="text-left p-4">Date</th>
                  <th className="text-left p-4">Description</th>
                  <th className="text-left p-4">Category</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-right p-4">Amount</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((transaction, idx) => (
                  <tr key={transaction.id} className={idx % 2 === 0 ? 'bg-slate-800' : 'bg-slate-750'}>
                    <td className="p-4 text-slate-300">{transaction.date}</td>
                    <td className="p-4 font-semibold">{transaction.description}</td>
                    <td className="p-4 text-slate-400">{transaction.category}</td>
                    <td className="p-4">
                      <span className={`px-3 py-1 rounded-full text-xs ${transaction.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                        {transaction.status}
                      </span>
                    </td>
                    <td className={`p-4 text-right font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
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