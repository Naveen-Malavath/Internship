import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const mockAccounts = [
    { id: 'checking', name: 'Checking Account', balance: 12450.75, type: 'checking' },
    { id: 'savings', name: 'Savings Account', balance: 25890.32, type: 'savings' },
    { id: 'credit', name: 'Credit Card', balance: -1235.50, type: 'credit' }
  ];

  const mockTransactions = [
    { id: 1, date: '2024-01-15', description: 'Online Purchase - Amazon', amount: -89.99, type: 'debit', category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3200.00, type: 'credit', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Grocery Store', amount: -156.78, type: 'debit', category: 'Food' },
    { id: 4, date: '2024-01-12', description: 'Transfer to Savings', amount: -500.00, type: 'transfer', category: 'Transfer' },
    { id: 5, date: '2024-01-11', description: 'Electric Bill', amount: -125.40, type: 'debit', category: 'Utilities' }
  ];

  const totalBalance = mockAccounts.reduce((sum, account) => sum + account.balance, 0);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-400">SecureBank Digital</h1>
          <div className="space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transactions')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'transactions' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Transactions
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="p-6 max-w-7xl mx-auto">
          <div className="mb-8">
            <h2 className="text-3xl font-bold mb-2">Welcome back, John</h2>
            <p className="text-slate-400">Here's an overview of your accounts</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-r from-blue-600 to-blue-700 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-blue-100">Total Balance</h3>
              <p className="text-2xl font-bold text-white">${totalBalance.toLocaleString()}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-slate-400">Monthly Spending</h3>
              <p className="text-2xl font-bold text-white">$2,847</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-slate-400">Active Cards</h3>
              <p className="text-2xl font-bold text-white">3</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm font-medium text-slate-400">Credit Score</h3>
              <p className="text-2xl font-bold text-green-400">742</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Account Overview</h3>
              <div className="space-y-4">
                {mockAccounts.map(account => (
                  <div key={account.id} className="flex justify-between items-center p-4 bg-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium">{account.name}</p>
                      <p className="text-sm text-slate-400 capitalize">{account.type}</p>
                    </div>
                    <p className={`font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      ${Math.abs(account.balance).toLocaleString()}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-4">
                <button className="p-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-center transition-colors">
                  <div className="text-2xl mb-2">💳</div>
                  <p className="text-sm">Transfer Money</p>
                </button>
                <button className="p-4 bg-green-600 hover:bg-green-700 rounded-lg text-center transition-colors">
                  <div className="text-2xl mb-2">💰</div>
                  <p className="text-sm">Pay Bills</p>
                </button>
                <button className="p-4 bg-purple-600 hover:bg-purple-700 rounded-lg text-center transition-colors">
                  <div className="text-2xl mb-2">📊</div>
                  <p className="text-sm">View Reports</p>
                </button>
                <button className="p-4 bg-orange-600 hover:bg-orange-700 rounded-lg text-center transition-colors">
                  <div className="text-2xl mb-2">⚙️</div>
                  <p className="text-sm">Settings</p>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="p-6 max-w-7xl mx-auto">
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-4">Transaction History</h2>
            <div className="flex flex-col sm:flex-row gap-4">
              <select 
                value={selectedAccount} 
                onChange={(e) => setSelectedAccount(e.target.value)}
                className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white"
              >
                <option value="">All Accounts</option>
                {mockAccounts.map(account => (
                  <option key={account.id} value={account.id}>{account.name}</option>
                ))}
              </select>
              <input 
                type="text" 
                placeholder="Search transactions..."
                className="px-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white placeholder-slate-400"
              />
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Date</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Description</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Category</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-slate-300 uppercase tracking-wider">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-700">
                  {mockTransactions.map(transaction => (
                    <tr key={transaction.id} className="hover:bg-slate-700">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                        {transaction.date}
                      </td>
                      <td className="px-6 py-4 text-sm text-white">
                        {transaction.description}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className="px-2 py-1 bg-slate-700 text-slate-300 rounded-full text-xs">
                          {transaction.category}
                        </span>
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm font-medium ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                        {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;