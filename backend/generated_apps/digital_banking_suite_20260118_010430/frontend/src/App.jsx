import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12458.32, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 45230.18, number: '****7892' },
    { id: 'credit', name: 'Credit Card', balance: -2341.50, number: '****1234' }
  ];

  const recentTransactions = [
    { id: 1, date: '2024-01-15', merchant: 'Amazon', amount: -89.99, status: 'completed' },
    { id: 2, date: '2024-01-14', merchant: 'Salary Deposit', amount: 5000.00, status: 'completed' },
    { id: 3, date: '2024-01-13', merchant: 'Starbucks', amount: -5.75, status: 'completed' },
    { id: 4, date: '2024-01-12', merchant: 'Shell Gas', amount: -45.20, status: 'completed' },
    { id: 5, date: '2024-01-11', merchant: 'Whole Foods', amount: -127.34, status: 'completed' },
    { id: 6, date: '2024-01-10', merchant: 'Netflix', amount: -15.99, status: 'completed' }
  ];

  const quickStats = [
    { label: 'Total Balance', value: '$55,346.00', change: '+2.5%', trend: 'up' },
    { label: 'Monthly Spending', value: '$2,847.32', change: '-5.2%', trend: 'down' },
    { label: 'Pending Payments', value: '3', change: '', trend: 'neutral' },
    { label: 'Credit Score', value: '742', change: '+12', trend: 'up' }
  ];

  const monthlyData = [
    { month: 'Jan', income: 5000, expenses: 2847 },
    { month: 'Feb', income: 5000, expenses: 3120 },
    { month: 'Mar', income: 5200, expenses: 2950 },
    { month: 'Apr', income: 5000, expenses: 3200 }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-blue-400">BankSuite</h1>
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
        <div className="max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {quickStats.map((stat, idx) => (
              <div key={idx} className="bg-slate-800 rounded-lg p-6 border border-slate-700">
                <p className="text-slate-400 text-sm mb-2">{stat.label}</p>
                <p className="text-3xl font-bold mb-2">{stat.value}</p>
                {stat.change && (
                  <p className={`text-sm ${stat.trend === 'up' ? 'text-green-400' : 'text-red-400'}`}>
                    {stat.change}
                  </p>
                )}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-xl font-bold mb-4">My Accounts</h3>
              {accounts.map((account) => (
                <div key={account.id} className="bg-slate-700 rounded p-4 mb-3 cursor-pointer hover:bg-slate-600 transition" onClick={() => setSelectedAccount(account.id)}>
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-semibold">{account.name}</p>
                      <p className="text-sm text-slate-400">{account.number}</p>
                    </div>
                    <p className={`text-xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      ${Math.abs(account.balance).toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
              <h3 className="text-xl font-bold mb-4">Quick Actions</h3>
              <div className="grid grid-cols-2 gap-3">
                <button className="bg-blue-600 hover:bg-blue-700 rounded p-4 transition">
                  <p className="font-semibold">Transfer Money</p>
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 rounded p-4 transition">
                  <p className="font-semibold">Pay Bills</p>
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 rounded p-4 transition">
                  <p className="font-semibold">Deposit Check</p>
                </button>
                <button className="bg-blue-600 hover:bg-blue-700 rounded p-4 transition">
                  <p className="font-semibold">View Statements</p>
                </button>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700">
            <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
            <div className="space-y-2">
              {recentTransactions.slice(0, 4).map((tx) => (
                <div key={tx.id} className="flex justify-between items-center p-3 bg-slate-700 rounded hover:bg-slate-600 transition">
                  <div>
                    <p className="font-semibold">{tx.merchant}</p>
                    <p className="text-sm text-slate-400">{tx.date}</p>
                  </div>
                  <p className={`font-bold ${tx.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="max-w-7xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">All Transactions</h2>
          
          <div className="bg-slate-800 rounded-lg p-6 border border-slate-700 mb-6">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <input 
                type="text" 
                placeholder="Search transactions..." 
                className="px-4 py-2 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none"
              />
              <select className="px-4 py-2 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none">
                <option>All Accounts</option>
                <option>Checking</option>
                <option>Savings</option>
                <option>Credit Card</option>
              </select>
              <select className="px-4 py-2 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none">
                <option>All Types</option>
                <option>Income</option>
                <option>Expenses</option>
              </select>
              <select className="px-4 py-2 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none">
                <option>Last 30 Days</option>
                <option>Last 90 Days</option>
                <option>This Year</option>
              </select>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            <table className="w-full">
              <thead className="bg-slate-700">
                <tr>
                  <th className="text-left p-4">Date</th>
                  <th className="text-left p-4">Merchant</th>
                  <th className="text-left p-4">Status</th>
                  <th className="text-right p-4">Amount</th>
                </tr>
              </thead>
              <tbody>
                {recentTransactions.map((tx) => (
                  <tr key={tx.id} className="border-t border-slate-700 hover:bg-slate-700 transition">
                    <td className="p-4">{tx.date}</td>
                    <td className="p-4 font-semibold">{tx.merchant}</td>
                    <td className="p-4">
                      <span className="px-3 py-1 bg-green-600 rounded-full text-xs">
                        {tx.status}
                      </span>
                    </td>
                    <td className={`p-4 text-right font-bold ${tx.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {tx.amount < 0 ? '-' : '+'}${Math.abs(tx.amount).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-6 flex justify-between items-center">
            <p className="text-slate-400">Showing 6 of 156 transactions</p>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">Previous</button>
              <button className="px-4 py-2 bg-blue-600 rounded">1</button>
              <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">2</button>
              <button className="px-4 py-2 bg-slate-700 rounded hover:bg-slate-600 transition">3</button>
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