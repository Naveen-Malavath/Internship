import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const mockAccounts = [
    { id: 'checking', name: 'Checking Account', balance: 5247.83, type: 'checking' },
    { id: 'savings', name: 'Savings Account', balance: 12840.52, type: 'savings' },
    { id: 'credit', name: 'Credit Card', balance: -1205.67, type: 'credit' }
  ];

  const mockTransactions = [
    { id: 1, description: 'Direct Deposit - Salary', amount: 3500.00, date: '2024-01-15', type: 'credit' },
    { id: 2, description: 'Grocery Store', amount: -87.43, date: '2024-01-14', type: 'debit' },
    { id: 3, description: 'Gas Station', amount: -45.20, date: '2024-01-13', type: 'debit' },
    { id: 4, description: 'Online Transfer', amount: -500.00, date: '2024-01-12', type: 'debit' }
  ];

  const mockPayments = [
    { id: 1, recipient: 'Electric Company', amount: 120.50, status: 'completed', date: '2024-01-10' },
    { id: 2, recipient: 'Internet Provider', amount: 79.99, status: 'pending', date: '2024-01-15' },
    { id: 3, recipient: 'John Smith', amount: 250.00, status: 'scheduled', date: '2024-01-20' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'} hover:bg-blue-500 transition-colors`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('payments')}
              className={`px-4 py-2 rounded ${currentPage === 'payments' ? 'bg-blue-600' : 'bg-slate-700'} hover:bg-blue-500 transition-colors`}
            >
              Payments
            </button>
            <button 
              onClick={() => setCurrentPage('analytics')}
              className={`px-4 py-2 rounded ${currentPage === 'analytics' ? 'bg-blue-600' : 'bg-slate-700'} hover:bg-blue-500 transition-colors`}
            >
              Analytics
            </button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && (
        <div className="max-w-6xl mx-auto p-6">
          <div className="mb-8">
            <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {mockAccounts.map(account => (
                <div key={account.id} className="bg-slate-800 rounded-lg p-6 hover:bg-slate-700 transition-colors cursor-pointer" onClick={() => setSelectedAccount(account.id)}>
                  <h3 className="text-lg font-semibold mb-2">{account.name}</h3>
                  <p className={`text-2xl font-bold ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${Math.abs(account.balance).toLocaleString('en-US', {minimumFractionDigits: 2})}
                  </p>
                  <p className="text-slate-400 text-sm mt-2">{account.type.toUpperCase()}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Recent Transactions</h3>
            <div className="space-y-3">
              {mockTransactions.map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-slate-400 text-sm">{transaction.date}</p>
                  </div>
                  <span className={`font-bold ${transaction.type === 'credit' ? 'text-green-400' : 'text-red-400'}`}>
                    {transaction.type === 'credit' ? '+' : '-'}${Math.abs(transaction.amount).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'payments' && (
        <div className="max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Payment Center</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Send Payment</h3>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Recipient</label>
                  <input type="text" className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none" placeholder="Enter recipient name" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Amount</label>
                  <input type="number" className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none" placeholder="0.00" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">From Account</label>
                  <select className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 outline-none">
                    <option>Checking Account</option>
                    <option>Savings Account</option>
                  </select>
                </div>
                <button type="submit" className="w-full bg-blue-600 hover:bg-blue-500 px-4 py-3 rounded font-medium transition-colors">
                  Send Payment
                </button>
              </form>
            </div>

            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Payment History</h3>
              <div className="space-y-3">
                {mockPayments.map(payment => (
                  <div key={payment.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                    <div>
                      <p className="font-medium">{payment.recipient}</p>
                      <p className="text-slate-400 text-sm">{payment.date}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-red-400">-${payment.amount.toFixed(2)}</p>
                      <span className={`text-xs px-2 py-1 rounded ${
                        payment.status === 'completed' ? 'bg-green-600 text-green-100' :
                        payment.status === 'pending' ? 'bg-yellow-600 text-yellow-100' :
                        'bg-blue-600 text-blue-100'
                      }`}>
                        {payment.status.toUpperCase()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'analytics' && (
        <div className="max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Monthly Spending</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Groceries</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-slate-700 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{width: '65%'}}></div>
                    </div>
                    <span className="text-sm">$420</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Utilities</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-slate-700 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '45%'}}></div>
                    </div>
                    <span className="text-sm">$290</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Entertainment</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-32 bg-slate-700 rounded-full h-2">
                      <div className="bg-purple-500 h-2 rounded-full" style={{width: '30%'}}></div>
                    </div>
                    <span className="text-sm">$195</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-bold mb-4">Account Growth</h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center">
                  <p className="text-2xl font-bold text-green-400">+8.5%</p>
                  <p className="text-slate-400 text-sm">This Month</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-blue-400">+24.2%</p>
                  <p className="text-slate-400 text-sm">This Year</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-white">$18,088</p>
                  <p className="text-slate-400 text-sm">Total Balance</p>
                </div>
                <div className="text-center">
                  <p className="text-2xl font-bold text-yellow-400">$2,340</p>
                  <p className="text-slate-400 text-sm">Monthly Income</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-xl font-bold mb-4">Financial Goals</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between mb-2">
                  <span>Emergency Fund</span>
                  <span>$5,000 / $10,000</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div className="bg-blue-500 h-3 rounded-full" style={{width: '50%'}}></div>
                </div>
              </div>
              <div>
                <div className="flex justify-between mb-2">
                  <span>Vacation Savings</span>
                  <span>$2,800 / $4,000</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-3">
                  <div className="bg-green-500 h-3 rounded-full" style={{width: '70%'}}></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;