import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState(0);

  const mockAccounts = [
    { id: 1, type: 'Checking', balance: 2847.32, number: '****1234' },
    { id: 2, type: 'Savings', balance: 15623.78, number: '****5678' },
    { id: 3, type: 'Credit Card', balance: -1245.90, number: '****9012' }
  ];

  const mockTransactions = [
    { id: 1, date: '2024-01-15', description: 'Direct Deposit', amount: 3500.00, type: 'credit' },
    { id: 2, date: '2024-01-14', description: 'Grocery Store', amount: -87.43, type: 'debit' },
    { id: 3, date: '2024-01-13', description: 'Online Transfer', amount: -500.00, type: 'debit' },
    { id: 4, date: '2024-01-12', description: 'ATM Withdrawal', amount: -100.00, type: 'debit' }
  ];

  const mockPayments = [
    { id: 1, payee: 'Electric Company', amount: 125.50, dueDate: '2024-01-20', status: 'pending' },
    { id: 2, payee: 'Internet Provider', amount: 89.99, dueDate: '2024-01-22', status: 'scheduled' },
    { id: 3, payee: 'Credit Card Payment', amount: 450.00, dueDate: '2024-01-25', status: 'pending' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('payments')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'payments' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Payments
            </button>
            <button 
              onClick={() => setCurrentPage('analytics')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'analytics' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Analytics
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="p-8">
          <h2 className="text-3xl font-bold mb-6">Account Dashboard</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            {mockAccounts.map((account, index) => (
              <div 
                key={account.id}
                onClick={() => setSelectedAccount(index)}
                className={`bg-slate-800 p-6 rounded-lg cursor-pointer transition-all hover:bg-slate-700 ${selectedAccount === index ? 'ring-2 ring-blue-500' : ''}`}
              >
                <h3 className="text-lg font-semibold text-blue-400">{account.type}</h3>
                <p className="text-sm text-slate-400 mb-2">{account.number}</p>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${Math.abs(account.balance).toLocaleString()}
                </p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4">Recent Transactions</h3>
            <div className="space-y-3">
              {mockTransactions.map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center py-3 border-b border-slate-700">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date}</p>
                  </div>
                  <p className={`font-semibold ${transaction.type === 'credit' ? 'text-green-400' : 'text-red-400'}`}>
                    {transaction.type === 'credit' ? '+' : '-'}${Math.abs(transaction.amount).toLocaleString()}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'payments' && (
        <div className="p-8">
          <h2 className="text-3xl font-bold mb-6">Bill Pay & Transfers</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Quick Transfer</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">From Account</label>
                  <select className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2">
                    <option>Checking ****1234</option>
                    <option>Savings ****5678</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Amount</label>
                  <input type="number" placeholder="0.00" className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2" />
                </div>
                <button className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded font-medium transition-colors">
                  Transfer Now
                </button>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Scheduled Payments</h3>
              <div className="space-y-3">
                {mockPayments.map(payment => (
                  <div key={payment.id} className="flex justify-between items-center py-3 border-b border-slate-700">
                    <div>
                      <p className="font-medium">{payment.payee}</p>
                      <p className="text-sm text-slate-400">Due: {payment.dueDate}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold">${payment.amount.toLocaleString()}</p>
                      <span className={`text-xs px-2 py-1 rounded ${payment.status === 'pending' ? 'bg-yellow-600' : 'bg-blue-600'}`}>
                        {payment.status}
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
        <div className="p-8">
          <h2 className="text-3xl font-bold mb-6">Spending Analytics</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Monthly Overview</h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Total Income</span>
                  <span className="text-green-400 font-semibold">$3,500.00</span>
                </div>
                <div className="flex justify-between">
                  <span>Total Expenses</span>
                  <span className="text-red-400 font-semibold">$2,187.43</span>
                </div>
                <div className="flex justify-between border-t border-slate-700 pt-2">
                  <span className="font-semibold">Net Balance</span>
                  <span className="text-blue-400 font-bold">$1,312.57</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Top Categories</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Groceries</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-slate-700 rounded-full h-2">
                      <div className="bg-blue-500 h-2 rounded-full" style={{width: '60%'}}></div>
                    </div>
                    <span className="text-sm">$456</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Utilities</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-slate-700 rounded-full h-2">
                      <div className="bg-green-500 h-2 rounded-full" style={{width: '40%'}}></div>
                    </div>
                    <span className="text-sm">$312</span>
                  </div>
                </div>
                <div className="flex justify-between items-center">
                  <span>Entertainment</span>
                  <div className="flex items-center space-x-2">
                    <div className="w-20 bg-slate-700 rounded-full h-2">
                      <div className="bg-purple-500 h-2 rounded-full" style={{width: '25%'}}></div>
                    </div>
                    <span className="text-sm">$189</span>
                  </div>
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