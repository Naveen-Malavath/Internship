import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12450.32, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 35200.00, number: '****7893' },
    { id: 'credit', name: 'Credit Card', balance: -1250.50, number: '****2341' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Walmart Purchase', amount: -125.50, status: 'completed', category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 5000.00, status: 'completed', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Netflix Subscription', amount: -15.99, status: 'completed', category: 'Entertainment' },
    { id: 4, date: '2024-01-12', description: 'Transfer to Savings', amount: -500.00, status: 'completed', category: 'Transfer' },
    { id: 5, date: '2024-01-11', description: 'Restaurant', amount: -78.20, status: 'completed', category: 'Dining' },
    { id: 6, date: '2024-01-10', description: 'Gas Station', amount: -45.00, status: 'pending', category: 'Transportation' }
  ];

  const chartData = [
    { month: 'Jan', income: 5000, expenses: 3200 },
    { month: 'Feb', income: 5000, expenses: 2800 },
    { month: 'Mar', income: 5200, expenses: 3500 },
    { month: 'Apr', income: 5000, expenses: 2900 }
  ];

  const totalBalance = accounts.reduce((sum, acc) => sum + acc.balance, 0);
  const monthlyIncome = 5000;
  const monthlyExpenses = 2850;

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 shadow-lg border-b border-slate-700">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">Digital Banking</h1>
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
        <div className="max-w-7xl mx-auto p-6">
          <div className="mb-6">
            <h2 className="text-3xl font-bold mb-2">Account Overview</h2>
            <p className="text-slate-400">Welcome back! Here is your financial summary</p>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-600 to-blue-700 p-6 rounded-lg shadow-lg">
              <p className="text-blue-200 text-sm mb-2">Total Balance</p>
              <p className="text-3xl font-bold">${totalBalance.toFixed(2)}</p>
              <p className="text-blue-200 text-xs mt-2">All accounts</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-2">Monthly Income</p>
              <p className="text-3xl font-bold text-green-400">${monthlyIncome.toFixed(2)}</p>
              <p className="text-slate-500 text-xs mt-2">+8% from last month</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-2">Monthly Expenses</p>
              <p className="text-3xl font-bold text-red-400">${monthlyExpenses.toFixed(2)}</p>
              <p className="text-slate-500 text-xs mt-2">-5% from last month</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-2">Savings Rate</p>
              <p className="text-3xl font-bold text-purple-400">43%</p>
              <p className="text-slate-500 text-xs mt-2">Above average</p>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-6 mb-6">
            {accounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700 hover:border-blue-500 transition cursor-pointer" onClick={() => setSelectedAccount(account.id)}>
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <p className="text-slate-400 text-sm">{account.name}</p>
                    <p className="text-slate-500 text-xs">{account.number}</p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs ${account.balance >= 0 ? 'bg-green-900 text-green-300' : 'bg-red-900 text-red-300'}`}>
                    {account.balance >= 0 ? 'Active' : 'Credit'}
                  </span>
                </div>
                <p className="text-2xl font-bold">${Math.abs(account.balance).toFixed(2)}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
              <div className="space-y-3">
                {transactions.slice(0, 4).map(tx => (
                  <div key={tx.id} className="flex justify-between items-center p-3 bg-slate-900 rounded hover:bg-slate-700 transition">
                    <div>
                      <p className="font-medium">{tx.description}</p>
                      <p className="text-xs text-slate-400">{tx.date}</p>
                    </div>
                    <p className={`font-bold ${tx.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {tx.amount > 0 ? '+' : ''}{tx.amount.toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Income vs Expenses</h3>
              <div className="space-y-4">
                {chartData.map((data, idx) => (
                  <div key={idx}>
                    <div className="flex justify-between text-sm mb-2">
                      <span>{data.month}</span>
                      <span className="text-slate-400">${data.income} / ${data.expenses}</span>
                    </div>
                    <div className="flex gap-1 h-8">
                      <div className="bg-green-600 rounded" style={{width: `${(data.income / 6000) * 100}%`}}></div>
                      <div className="bg-red-600 rounded" style={{width: `${(data.expenses / 6000) * 100}%`}}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'transactions' && (
        <div className="max-w-7xl mx-auto p-6">
          <div className="mb-6 flex justify-between items-center">
            <div>
              <h2 className="text-3xl font-bold mb-2">Transactions & Orders</h2>
              <p className="text-slate-400">Track and manage all your financial activities</p>
            </div>
            <button className="px-6 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition">
              Export
            </button>
          </div>

          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Total Transactions</p>
              <p className="text-2xl font-bold">{transactions.length}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Completed</p>
              <p className="text-2xl font-bold text-green-400">{transactions.filter(t => t.status === 'completed').length}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Pending</p>
              <p className="text-2xl font-bold text-yellow-400">{transactions.filter(t => t.status === 'pending').length}</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg border border-slate-700">
              <p className="text-slate-400 text-sm mb-1">Total Spent</p>
              <p className="text-2xl font-bold text-red-400">${transactions.filter(t => t.amount < 0).reduce((sum, t) => sum + Math.abs(t.amount), 0).toFixed(2)}</p>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg shadow-lg border border-slate-700 p-6">
            <div className="flex gap-4 mb-6">
              <input type="text" placeholder="Search transactions..." className="flex-1 px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500" />
              <select className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500">
                <option>All Categories</option>
                <option>Shopping</option>
                <option>Dining</option>
                <option>Transportation</option>
              </select>
              <select className="px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg focus:outline-none focus:border-blue-500">
                <option>All Status</option>
                <option>Completed</option>
                <option>Pending</option>
              </select>
            </div>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Date</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Description</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Category</th>
                    <th className="text-left py-3 px-4 text-slate-400 font-medium">Status</th>
                    <th className="text-right py-3 px-4 text-slate-400 font-medium">Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map(tx => (
                    <tr key={tx.id} className="border-b border-slate-700 hover:bg-slate-700 transition">
                      <td className="py-4 px-4 text-slate-300">{tx.date}</td>
                      <td className="py-4 px-4 font-medium">{tx.description}</td>
                      <td className="py-4 px-4">
                        <span className="px-3 py-1 bg-slate-900 rounded-full text-xs">{tx.category}</span>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-3 py-1 rounded-full text-xs ${tx.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                          {tx.status}
                        </span>
                      </td>
                      <td className={`py-4 px-4 text-right font-bold ${tx.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {tx.amount > 0 ? '+' : ''}{tx.amount.toFixed(2)}
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