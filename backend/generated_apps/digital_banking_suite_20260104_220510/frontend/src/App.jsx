import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 5420.50, number: '**** 1234' },
    { id: 'savings', name: 'Savings Account', balance: 12850.75, number: '**** 5678' },
    { id: 'credit', name: 'Credit Card', balance: -1250.25, number: '**** 9012' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Online Purchase - Amazon', amount: -89.99, status: 'Completed' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3500.00, status: 'Completed' },
    { id: 3, date: '2024-01-13', description: 'ATM Withdrawal', amount: -200.00, status: 'Completed' },
    { id: 4, date: '2024-01-12', description: 'Transfer to Savings', amount: -500.00, status: 'Completed' },
    { id: 5, date: '2024-01-11', description: 'Grocery Store', amount: -125.43, status: 'Pending' }
  ];

  const orders = [
    { id: 'ORD-001', date: '2024-01-15', merchant: 'Amazon', amount: 89.99, status: 'Delivered' },
    { id: 'ORD-002', date: '2024-01-10', merchant: 'Best Buy', amount: 299.99, status: 'Shipped' },
    { id: 'ORD-003', date: '2024-01-08', merchant: 'Target', amount: 45.67, status: 'Processing' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('orders')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'orders' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Orders & Transactions
            </button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Account Dashboard</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Total Balance</h3>
              <p className="text-2xl font-bold text-green-400">$17,021.00</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Monthly Spending</h3>
              <p className="text-2xl font-bold text-red-400">$2,450.67</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Pending Orders</h3>
              <p className="text-2xl font-bold text-yellow-400">3</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Credit Available</h3>
              <p className="text-2xl font-bold text-blue-400">$8,749.75</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-bold mb-4">Accounts</h2>
              <div className="space-y-4">
                {accounts.map(account => (
                  <div key={account.id} className="flex justify-between items-center p-4 bg-slate-700 rounded">
                    <div>
                      <p className="font-medium">{account.name}</p>
                      <p className="text-sm text-slate-400">{account.number}</p>
                    </div>
                    <p className={`font-bold ${account.balance > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${Math.abs(account.balance).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 p-3 rounded-lg text-left">
                  Transfer Money
                </button>
                <button className="w-full bg-green-600 hover:bg-green-700 p-3 rounded-lg text-left">
                  Pay Bills
                </button>
                <button className="w-full bg-purple-600 hover:bg-purple-700 p-3 rounded-lg text-left">
                  Mobile Deposit
                </button>
                <button className="w-full bg-orange-600 hover:bg-orange-700 p-3 rounded-lg text-left">
                  Request Money
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'orders' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Orders & Transactions</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Total Orders</h3>
              <p className="text-2xl font-bold text-blue-400">12</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">This Month</h3>
              <p className="text-2xl font-bold text-green-400">$435.65</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Pending</h3>
              <p className="text-2xl font-bold text-yellow-400">1</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-sm text-slate-400 mb-2">Refunded</h3>
              <p className="text-2xl font-bold text-red-400">$89.99</p>
            </div>
          </div>

          <div className="mb-6">
            <input 
              type="text" 
              placeholder="Search transactions..." 
              className="w-full md:w-1/3 p-3 bg-slate-800 rounded-lg border border-slate-700 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div className="bg-slate-800 rounded-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-slate-700">
                  <tr>
                    <th className="text-left p-4">Date</th>
                    <th className="text-left p-4">Description</th>
                    <th className="text-left p-4">Amount</th>
                    <th className="text-left p-4">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {transactions.map(transaction => (
                    <tr key={transaction.id} className="border-t border-slate-700">
                      <td className="p-4 text-slate-300">{transaction.date}</td>
                      <td className="p-4">{transaction.description}</td>
                      <td className={`p-4 font-medium ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                        ${Math.abs(transaction.amount).toFixed(2)}
                      </td>
                      <td className="p-4">
                        <span className={`px-2 py-1 rounded text-xs ${transaction.status === 'Completed' ? 'bg-green-800 text-green-200' : 'bg-yellow-800 text-yellow-200'}`}>
                          {transaction.status}
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