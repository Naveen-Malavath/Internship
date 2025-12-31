const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState(0);

  const accounts = [
    { id: 1, name: 'Checking Account', balance: 15420.50, type: 'checking' },
    { id: 2, name: 'Savings Account', balance: 48750.25, type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -2340.80, type: 'credit' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Direct Deposit - Salary', amount: 4500.00, type: 'credit' },
    { id: 2, date: '2024-01-14', description: 'Grocery Store Purchase', amount: -127.45, type: 'debit' },
    { id: 3, date: '2024-01-13', description: 'Online Transfer to Savings', amount: -1000.00, type: 'transfer' },
    { id: 4, date: '2024-01-12', description: 'ATM Withdrawal', amount: -200.00, type: 'debit' },
    { id: 5, date: '2024-01-11', description: 'Netflix Subscription', amount: -15.99, type: 'debit' }
  ];

  const payees = [
    { id: 1, name: 'Electric Company', account: '****1234' },
    { id: 2, name: 'Internet Provider', account: '****5678' },
    { id: 3, name: 'John Smith', account: '****9012' }
  ];

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(Math.abs(amount));
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-4 shadow-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('accounts')}
              className={`px-4 py-2 rounded transition ${currentPage === 'accounts' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Accounts
            </button>
            <button 
              onClick={() => setCurrentPage('payments')}
              className={`px-4 py-2 rounded transition ${currentPage === 'payments' ? 'bg-blue-600' : 'bg-slate-600 hover:bg-slate-500'}`}
            >
              Payments
            </button>
          </div>
        </div>
      </nav>

      {currentPage === 'dashboard' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {accounts.map((account) => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg">
                <h3 className="text-lg font-semibold mb-2">{account.name}</h3>
                <p className={`text-2xl font-bold ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                  {account.balance >= 0 ? '' : '-'}{formatCurrency(account.balance)}
                </p>
                <p className="text-slate-400 text-sm mt-1 capitalize">{account.type}</p>
              </div>
            ))}
          </div>
          
          <div className="bg-slate-800 rounded-lg p-6">
            <h2 className="text-xl font-bold mb-4">Recent Transactions</h2>
            <div className="space-y-3">
              {transactions.slice(0, 5).map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center border-b border-slate-700 pb-3">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-slate-400 text-sm">{transaction.date}</p>
                  </div>
                  <span className={`font-bold ${transaction.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {transaction.amount >= 0 ? '+' : '-'}{formatCurrency(transaction.amount)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'accounts' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Account Details</h1>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-slate-800 rounded-lg p-4">
              <h2 className="text-lg font-bold mb-4">Select Account</h2>
              {accounts.map((account, index) => (
                <button
                  key={account.id}
                  onClick={() => setSelectedAccount(index)}
                  className={`w-full text-left p-3 mb-2 rounded transition ${selectedAccount === index ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
                >
                  <div className="font-medium">{account.name}</div>
                  <div className={`text-sm ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {account.balance >= 0 ? '' : '-'}{formatCurrency(account.balance)}
                  </div>
                </button>
              ))}
            </div>
            
            <div className="lg:col-span-2 bg-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Transaction History - {accounts[selectedAccount].name}</h2>
              <div className="space-y-3">
                {transactions.map((transaction) => (
                  <div key={transaction.id} className="flex justify-between items-center bg-slate-700 p-4 rounded">
                    <div>
                      <p className="font-medium">{transaction.description}</p>
                      <p className="text-slate-400 text-sm">{transaction.date}</p>
                      <span className={`inline-block px-2 py-1 text-xs rounded mt-1 ${
                        transaction.type === 'credit' ? 'bg-green-600' : 
                        transaction.type === 'debit' ? 'bg-red-600' : 'bg-blue-600'
                      }`}>
                        {transaction.type}
                      </span>
                    </div>
                    <span className={`font-bold text-lg ${transaction.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {transaction.amount >= 0 ? '+' : '-'}{formatCurrency(transaction.amount)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'payments' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Send Payment</h1>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">New Payment</h2>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">From Account</label>
                  <select className="w-full p-3 bg-slate-700 rounded border border-slate-600 text-white">
                    {accounts.filter(acc => acc.type !== 'credit').map(account => (
                      <option key={account.id} value={account.id}>{account.name}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">To</label>
                  <select className="w-full p-3 bg-slate-700 rounded border border-slate-600 text-white">
                    <option value="">Select Payee</option>
                    {payees.map(payee => (
                      <option key={payee.id} value={payee.id}>{payee.name} - {payee.account}</option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Amount</label>
                  <input 
                    type="number" 
                    placeholder="0.00" 
                    className="w-full p-3 bg-slate-700 rounded border border-slate-600 text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium mb-2">Memo (Optional)</label>
                  <input 
                    type="text" 
                    placeholder="Payment description" 
                    className="w-full p-3 bg-slate-700 rounded border border-slate-600 text-white"
                  />
                </div>
                
                <button type="button" className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded transition">
                  Send Payment
                </button>
              </form>
            </div>
            
            <div className="bg-slate-800 rounded-lg p-6">
              <h2 className="text-xl font-bold mb-4">Saved Payees</h2>
              <div className="space-y-3">
                {payees.map(payee => (
                  <div key={payee.id} className="flex justify-between items-center bg-slate-700 p-4 rounded">
                    <div>
                      <p className="font-medium">{payee.name}</p>
                      <p className="text-slate-400 text-sm">{payee.account}</p>
                    </div>
                    <button className="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm transition">
                      Pay
                    </button>
                  </div>
                ))}
              </div>
              
              <button className="w-full mt-4 bg-slate-600 hover:bg-slate-500 text-white font-medium py-2 px-4 rounded transition">
                + Add New Payee
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;