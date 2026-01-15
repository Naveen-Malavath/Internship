import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('accounts');
  const [selectedAccount, setSelectedAccount] = React.useState(null);

  const accounts = [
    { id: 1, name: 'Checking Account', balance: 5420.50, type: 'checking', number: '****1234' },
    { id: 2, name: 'Savings Account', balance: 12850.75, type: 'savings', number: '****5678' },
    { id: 3, name: 'Credit Card', balance: -1200.00, type: 'credit', number: '****9012' }
  ];

  const transactions = [
    { id: 1, description: 'Grocery Store', amount: -89.50, date: '2024-01-15', category: 'Food' },
    { id: 2, description: 'Salary Deposit', amount: 3500.00, date: '2024-01-14', category: 'Income' },
    { id: 3, description: 'Electric Bill', amount: -125.30, date: '2024-01-13', category: 'Utilities' },
    { id: 4, description: 'ATM Withdrawal', amount: -100.00, date: '2024-01-12', category: 'Cash' }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <header className="bg-slate-800 p-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('accounts')}
              className={`px-4 py-2 rounded ${currentPage === 'accounts' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Accounts
            </button>
            <button 
              onClick={() => setCurrentPage('transfer')}
              className={`px-4 py-2 rounded ${currentPage === 'transfer' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Transfer
            </button>
            <button 
              onClick={() => setCurrentPage('analytics')}
              className={`px-4 py-2 rounded ${currentPage === 'analytics' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Analytics
            </button>
          </div>
        </div>
      </header>

      {currentPage === 'accounts' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">My Accounts</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {accounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg border border-slate-700">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold">{account.name}</h3>
                    <p className="text-slate-400">{account.number}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${account.type === 'credit' ? 'bg-orange-600' : 'bg-green-600'}`}>
                    {account.type.toUpperCase()}
                  </span>
                </div>
                <div className="text-3xl font-bold mb-4">
                  <span className={account.balance < 0 ? 'text-red-400' : 'text-green-400'}>
                    {formatCurrency(Math.abs(account.balance))}
                  </span>
                </div>
                <button 
                  onClick={() => setSelectedAccount(account)}
                  className="w-full bg-blue-600 hover:bg-blue-700 py-2 px-4 rounded"
                >
                  View Details
                </button>
              </div>
            ))}
          </div>

          {selectedAccount && (
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-2xl font-bold mb-4">{selectedAccount.name} - Recent Transactions</h3>
              <div className="space-y-3">
                {transactions.map(transaction => (
                  <div key={transaction.id} className="flex justify-between items-center p-4 bg-slate-700 rounded">
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-sm text-slate-400">{transaction.date} • {transaction.category}</p>
                    </div>
                    <span className={`font-bold ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {transaction.amount > 0 ? '+' : ''}{formatCurrency(transaction.amount)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {currentPage === 'transfer' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Transfer Money</h2>
          <div className="max-w-md mx-auto bg-slate-800 p-6 rounded-lg">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">From Account</label>
                <select className="w-full p-3 bg-slate-700 rounded border border-slate-600">
                  {accounts.filter(acc => acc.type !== 'credit').map(account => (
                    <option key={account.id} value={account.id}>
                      {account.name} - {formatCurrency(account.balance)}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">To Account</label>
                <select className="w-full p-3 bg-slate-700 rounded border border-slate-600">
                  {accounts.map(account => (
                    <option key={account.id} value={account.id}>
                      {account.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Amount</label>
                <input 
                  type="number" 
                  placeholder="0.00" 
                  className="w-full p-3 bg-slate-700 rounded border border-slate-600"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <input 
                  type="text" 
                  placeholder="Optional description" 
                  className="w-full p-3 bg-slate-700 rounded border border-slate-600"
                />
              </div>
              <button className="w-full bg-blue-600 hover:bg-blue-700 py-3 px-4 rounded font-medium">
                Transfer Money
              </button>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'analytics' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-slate-400">Total Balance</h3>
              <p className="text-3xl font-bold text-green-400">{formatCurrency(17070.25)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-slate-400">Monthly Income</h3>
              <p className="text-3xl font-bold text-blue-400">{formatCurrency(3500.00)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-slate-400">Monthly Expenses</h3>
              <p className="text-3xl font-bold text-red-400">{formatCurrency(2314.80)}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-medium text-slate-400">Savings Rate</h3>
              <p className="text-3xl font-bold text-purple-400">34%</p>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <h3 className="text-xl font-bold mb-4">Spending by Category</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>Food & Dining</span>
                <div className="flex items-center">
                  <div className="w-48 bg-slate-700 rounded-full h-3 mr-4">
                    <div className="bg-red-500 h-3 rounded-full" style={{width: '45%'}}></div>
                  </div>
                  <span>{formatCurrency(890.50)}</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>Utilities</span>
                <div className="flex items-center">
                  <div className="w-48 bg-slate-700 rounded-full h-3 mr-4">
                    <div className="bg-blue-500 h-3 rounded-full" style={{width: '25%'}}></div>
                  </div>
                  <span>{formatCurrency(425.30)}</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span>Shopping</span>
                <div className="flex items-center">
                  <div className="w-48 bg-slate-700 rounded-full h-3 mr-4">
                    <div className="bg-purple-500 h-3 rounded-full" style={{width: '35%'}}></div>
                  </div>
                  <span>{formatCurrency(650.00)}</span>
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