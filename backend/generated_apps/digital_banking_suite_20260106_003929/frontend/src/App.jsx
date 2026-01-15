import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12453.67, type: 'Checking' },
    { id: 'savings', name: 'Savings Account', balance: 45230.12, type: 'Savings' },
    { id: 'credit', name: 'Credit Card', balance: -2341.50, type: 'Credit' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Amazon Purchase', amount: -127.43, status: 'Completed', category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 5000.00, status: 'Completed', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Electric Bill', amount: -89.50, status: 'Completed', category: 'Utilities' },
    { id: 4, date: '2024-01-12', description: 'Grocery Store', amount: -156.78, status: 'Completed', category: 'Food' },
    { id: 5, date: '2024-01-11', description: 'Transfer to Savings', amount: -500.00, status: 'Completed', category: 'Transfer' },
    { id: 6, date: '2024-01-10', description: 'Netflix Subscription', amount: -15.99, status: 'Pending', category: 'Entertainment' }
  ];

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
  const monthlyIncome = 5000.00;
  const monthlyExpenses = 889.70;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-blue-400">Digital Banking Suite</h1>
            <div className="flex gap-2">
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
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm mb-2">Total Balance</div>
              <div className="text-3xl font-bold text-green-400">${totalBalance.toFixed(2)}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm mb-2">Monthly Income</div>
              <div className="text-3xl font-bold text-blue-400">${monthlyIncome.toFixed(2)}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm mb-2">Monthly Expenses</div>
              <div className="text-3xl font-bold text-red-400">${monthlyExpenses.toFixed(2)}</div>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm mb-2">Net Savings</div>
              <div className="text-3xl font-bold text-green-400">${(monthlyIncome - monthlyExpenses).toFixed(2)}</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Your Accounts</h3>
              <div className="space-y-3">
                {accounts.map(account => (
                  <div key={account.id} className="flex justify-between items-center p-4 bg-slate-700 rounded">
                    <div>
                      <div className="font-semibold">{account.name}</div>
                      <div className="text-sm text-slate-400">{account.type}</div>
                    </div>
                    <div className={`text-xl font-bold ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${Math.abs(account.balance).toFixed(2)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 p-4 rounded transition text-left font-semibold">
                  Transfer Money
                </button>
                <button className="w-full bg-green-600 hover:bg-green-700 p-4 rounded transition text-left font-semibold">
                  Pay Bills
                </button>
                <button className="w-full bg-purple-600 hover:bg-purple-700 p-4 rounded transition text-left font-semibold">
                  Deposit Check
                </button>
                <button className="w-full bg-orange-600 hover:bg-orange-700 p-4 rounded transition text-left font-semibold">
                  Download Statements
                </button>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
            <div className="space-y-2">
              {transactions.slice(0, 5).map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-slate-700 rounded hover:bg-slate-600 transition">
                  <div className="flex-1">
                    <div className="font-semibold">{transaction.description}</div>
                    <div className="text-sm text-slate-400">{transaction.date} • {transaction.category}</div>
                  </div>
                  <div className={`text-lg font-bold ${transaction.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {transaction.amount >= 0 ? '+' : ''}{transaction.amount.toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-3xl font-bold">All Transactions</h2>
            <select 
              value={selectedAccount}
              onChange={(e) => setSelectedAccount(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded px-4 py-2"
            >
              <option value="all">All Accounts</option>
              {accounts.map(account => (
                <option key={account.id} value={account.id}>{account.name}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm">Total Transactions</div>
              <div className="text-2xl font-bold">{transactions.length}</div>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm">Completed</div>
              <div className="text-2xl font-bold text-green-400">{transactions.filter(t => t.status === 'Completed').length}</div>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm">Pending</div>
              <div className="text-2xl font-bold text-yellow-400">{transactions.filter(t => t.status === 'Pending').length}</div>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <div className="text-slate-400 text-sm">Total Spent</div>
              <div className="text-2xl font-bold text-red-400">${Math.abs(transactions.filter(t => t.amount < 0).reduce((sum, t) => sum + t.amount, 0)).toFixed(2)}</div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
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
                {transactions.map(transaction => (
                  <tr key={transaction.id} className="border-t border-slate-700 hover:bg-slate-700 transition">
                    <td className="p-4">{transaction.date}</td>
                    <td className="p-4 font-semibold">{transaction.description}</td>
                    <td className="p-4">
                      <span className="px-2 py-1 bg-slate-600 rounded text-sm">{transaction.category}</span>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded text-sm ${transaction.status === 'Completed' ? 'bg-green-600' : 'bg-yellow-600'}`}>
                        {transaction.status}
                      </span>
                    </td>
                    <td className={`p-4 text-right font-bold ${transaction.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {transaction.amount >= 0 ? '+' : ''}{transaction.amount.toFixed(2)}
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