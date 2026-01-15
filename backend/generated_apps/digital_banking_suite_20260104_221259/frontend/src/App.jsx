import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 5420.50, number: '****1234' },
    { id: 'savings', name: 'Savings Account', balance: 12750.25, number: '****5678' },
    { id: 'credit', name: 'Credit Card', balance: -2340.75, number: '****9012' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Amazon Purchase', amount: -89.99, type: 'debit', category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3500.00, type: 'credit', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Coffee Shop', amount: -12.45, type: 'debit', category: 'Food' },
    { id: 4, date: '2024-01-12', description: 'Transfer to Savings', amount: -500.00, type: 'debit', category: 'Transfer' },
    { id: 5, date: '2024-01-11', description: 'Gas Station', amount: -45.60, type: 'debit', category: 'Transportation' }
  ];

  const recentOrders = [
    { id: 'ORD001', date: '2024-01-15', merchant: 'Amazon', amount: 89.99, status: 'completed' },
    { id: 'ORD002', date: '2024-01-13', merchant: 'Starbucks', amount: 12.45, status: 'completed' },
    { id: 'ORD003', date: '2024-01-11', merchant: 'Shell Gas', amount: 45.60, status: 'pending' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="flex items-center justify-between max-w-7xl mx-auto">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-6 py-2 rounded-lg transition-colors ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transactions')}
              className={`px-6 py-2 rounded-lg transition-colors ${currentPage === 'transactions' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Transactions
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="p-8 max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold mb-8">Account Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            {accounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg">
                <h3 className="text-lg font-semibold mb-2">{account.name}</h3>
                <p className="text-sm text-slate-400 mb-3">{account.number}</p>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${Math.abs(account.balance).toFixed(2)}
                </p>
              </div>
            ))}
            
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-lg font-semibold mb-2">Quick Transfer</h3>
              <input type="number" placeholder="Amount" className="w-full p-2 mb-3 bg-slate-700 rounded text-white" />
              <button className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded transition-colors">
                Transfer
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-4">Recent Transactions</h3>
              <div className="space-y-3">
                {transactions.slice(0, 5).map(transaction => (
                  <div key={transaction.id} className="flex justify-between items-center border-b border-slate-700 pb-2">
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-slate-400">{transaction.date}</p>
                    </div>
                    <span className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                      {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-xl font-semibold mb-4">Monthly Spending</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Food & Dining</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-slate-700 rounded-full h-3">
                      <div className="bg-blue-500 h-3 rounded-full w-3/4"></div>
                    </div>
                    <span>$450</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Shopping</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-slate-700 rounded-full h-3">
                      <div className="bg-green-500 h-3 rounded-full w-1/2"></div>
                    </div>
                    <span>$320</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Transportation</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-24 bg-slate-700 rounded-full h-3">
                      <div className="bg-yellow-500 h-3 rounded-full w-1/3"></div>
                    </div>
                    <span>$180</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transactions' && (
        <div className="p-8 max-w-7xl mx-auto">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold">Orders & Transactions</h2>
            <div className="flex space-x-4">
              <select className="bg-slate-800 p-2 rounded border border-slate-600">
                <option>All Categories</option>
                <option>Shopping</option>
                <option>Food</option>
                <option>Transportation</option>
              </select>
              <input 
                type="text" 
                placeholder="Search transactions..." 
                className="bg-slate-800 p-2 rounded border border-slate-600 text-white"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Total Spent</h3>
              <p className="text-2xl font-bold text-red-400">$2,847.39</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Total Received</h3>
              <p className="text-2xl font-bold text-green-400">$7,250.00</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Pending Orders</h3>
              <p className="text-2xl font-bold text-yellow-400">3</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">This Month</h3>
              <p className="text-2xl font-bold text-blue-400">47</p>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg shadow-lg overflow-hidden">
            <div className="p-6 border-b border-slate-700">
              <h3 className="text-xl font-semibold">All Transactions</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="px-6 py-4 text-left">Date</th>
                    <th className="px-6 py-4 text-left">Description</th>
                    <th className="px-6 py-4 text-left">Category</th>
                    <th className="px-6 py-4 text-right">Amount</th>
                    <th className="px-6 py-4 text-left">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map(transaction => (
                    <tr key={transaction.id} className="border-b border-slate-700 hover:bg-slate-750">
                      <td className="px-6 py-4">{transaction.date}</td>
                      <td className="px-6 py-4 font-medium">{transaction.description}</td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-slate-600 rounded-full text-xs">
                          {transaction.category}
                        </span>
                      </td>
                      <td className={`px-6 py-4 text-right font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                        {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                      </td>
                      <td className="px-6 py-4">
                        <span className="px-2 py-1 bg-green-600 rounded-full text-xs">
                          Completed
                        </span>
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