import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState(0);

  const mockAccounts = [
    { id: 1, type: 'Checking', balance: 5420.50, number: '****1234' },
    { id: 2, type: 'Savings', balance: 12840.75, number: '****5678' },
    { id: 3, type: 'Credit Card', balance: -1250.30, number: '****9012' }
  ];

  const mockTransactions = [
    { id: 1, date: '2024-01-15', description: 'Amazon Purchase', amount: -89.99, category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3200.00, category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Starbucks', amount: -5.75, category: 'Food' },
    { id: 4, date: '2024-01-12', description: 'Gas Station', amount: -45.20, category: 'Transportation' }
  ];

  const mockPayments = [
    { id: 1, recipient: 'John Doe', amount: 150.00, status: 'Completed' },
    { id: 2, recipient: 'Electric Company', amount: 89.50, status: 'Pending' },
    { id: 3, recipient: 'Mom', amount: 50.00, status: 'Completed' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="bg-slate-800 p-4 shadow-lg">
        <div className="flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-1">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('accounts')}
              className={`px-4 py-2 rounded transition ${currentPage === 'accounts' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Accounts
            </button>
            <button 
              onClick={() => setCurrentPage('payments')}
              className={`px-4 py-2 rounded transition ${currentPage === 'payments' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Payments
            </button>
          </div>
        </div>
      </header>

      {currentPage === 'dashboard' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Welcome back, Sarah!</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {mockAccounts.map((account, index) => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                <div className="flex justify-between items-start mb-3">
                  <h3 className="text-lg font-semibold">{account.type}</h3>
                  <span className="text-sm text-slate-400">{account.number}</span>
                </div>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${Math.abs(account.balance).toFixed(2)}
                </p>
                {account.balance < 0 && <p className="text-sm text-red-400">Outstanding Balance</p>}
              </div>
            ))}
          </div>

          <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
            <h3 className="text-xl font-semibold mb-4">Recent Transactions</h3>
            <div className="space-y-3">
              {mockTransactions.slice(0, 4).map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center py-2 border-b border-slate-700">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date} • {transaction.category}</p>
                  </div>
                  <span className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'accounts' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Account Management</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-1">
              <h3 className="text-xl font-semibold mb-4">Your Accounts</h3>
              <div className="space-y-3">
                {mockAccounts.map((account, index) => (
                  <button
                    key={account.id}
                    onClick={() => setSelectedAccount(index)}
                    className={`w-full text-left p-4 rounded-lg border transition ${
                      selectedAccount === index 
                        ? 'bg-blue-600 border-blue-500' 
                        : 'bg-slate-800 border-slate-700 hover:bg-slate-700'
                    }`}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="font-semibold">{account.type}</p>
                        <p className="text-sm text-slate-400">{account.number}</p>
                      </div>
                      <span className={`font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                        ${Math.abs(account.balance).toFixed(2)}
                      </span>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            <div className="lg:col-span-2">
              <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                <h3 className="text-xl font-semibold mb-4">
                  {mockAccounts[selectedAccount].type} - Transaction History
                </h3>
                <div className="space-y-3">
                  {mockTransactions.map(transaction => (
                    <div key={transaction.id} className="flex justify-between items-center py-3 border-b border-slate-700">
                      <div className="flex-1">
                        <p className="font-medium">{transaction.description}</p>
                        <p className="text-sm text-slate-400">{transaction.date}</p>
                      </div>
                      <div className="text-right">
                        <span className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                          {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                        </span>
                        <p className="text-xs text-slate-400">{transaction.category}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'payments' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Payments & Transfers</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-semibold mb-4">Send Money</h3>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Recipient</label>
                  <input 
                    type="text" 
                    placeholder="Enter name or email"
                    className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Amount</label>
                  <input 
                    type="number" 
                    placeholder="0.00"
                    className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">From Account</label>
                  <select className="w-full p-3 bg-slate-700 border border-slate-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option>Checking ****1234</option>
                    <option>Savings ****5678</option>
                  </select>
                </div>
                <button 
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition"
                >
                  Send Payment
                </button>
              </form>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
              <h3 className="text-xl font-semibold mb-4">Recent Payments</h3>
              <div className="space-y-4">
                {mockPayments.map(payment => (
                  <div key={payment.id} className="flex justify-between items-center p-3 bg-slate-700 rounded-lg">
                    <div>
                      <p className="font-medium">{payment.recipient}</p>
                      <p className={`text-sm ${
                        payment.status === 'Completed' ? 'text-green-400' : 
                        payment.status === 'Pending' ? 'text-yellow-400' : 'text-red-400'
                      }`}>
                        {payment.status}
                      </p>
                    </div>
                    <span className="font-bold text-blue-400">${payment.amount.toFixed(2)}</span>
                  </div>
                ))}
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