import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState(0);

  const accounts = [
    { id: 1, name: 'Checking Account', balance: 12450.75, number: '****2847' },
    { id: 2, name: 'Savings Account', balance: 35200.20, number: '****1923' },
    { id: 3, name: 'Credit Card', balance: -1250.30, number: '****4567' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Online Purchase - Amazon', amount: -89.99, category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3200.00, category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Coffee Shop', amount: -4.50, category: 'Food' },
    { id: 4, date: '2024-01-12', description: 'ATM Withdrawal', amount: -100.00, category: 'Cash' },
    { id: 5, date: '2024-01-11', description: 'Utilities Payment', amount: -156.78, category: 'Bills' }
  ];

  const [transferAmount, setTransferAmount] = React.useState('');
  const [transferTo, setTransferTo] = React.useState('');

  const handleTransfer = () => {
    alert(`Transfer of $${transferAmount} to ${transferTo} initiated successfully!`);
    setTransferAmount('');
    setTransferTo('');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="flex justify-between items-center max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="space-x-4">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transfer')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'transfer' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Transfer
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
        <div className="max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {accounts.map((account, index) => (
              <div 
                key={account.id}
                onClick={() => setSelectedAccount(index)}
                className={`bg-slate-800 p-6 rounded-lg cursor-pointer transition-all hover:bg-slate-700 ${selectedAccount === index ? 'border-2 border-blue-500' : 'border border-slate-600'}`}
              >
                <h3 className="text-lg font-semibold text-blue-300">{account.name}</h3>
                <p className="text-sm text-slate-400 mb-2">{account.number}</p>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <h3 className="text-xl font-semibold mb-4">Recent Transactions - {accounts[selectedAccount].name}</h3>
            <div className="space-y-3">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-slate-700 rounded border-l-4 border-blue-500">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date} • {transaction.category}</p>
                  </div>
                  <p className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'transfer' && (
        <div className="max-w-2xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Money Transfer</h2>
          
          <div className="bg-slate-800 rounded-lg p-6">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">From Account</label>
                <select className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 focus:outline-none">
                  <option>Checking Account (****2847)</option>
                  <option>Savings Account (****1923)</option>
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">To Account / Email</label>
                <input 
                  type="text"
                  value={transferTo}
                  onChange={(e) => setTransferTo(e.target.value)}
                  placeholder="Enter account number or email"
                  className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 focus:outline-none"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Amount ($)</label>
                <input 
                  type="number"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 focus:outline-none"
                />
              </div>
              
              <button 
                onClick={handleTransfer}
                className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded font-semibold transition-colors"
              >
                Transfer Money
              </button>
            </div>
          </div>
        </div>
      )}

      {currentPage === 'analytics' && (
        <div className="max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Monthly Spending</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Shopping</span>
                  <span className="text-red-400">$450.75</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-red-400 h-2 rounded-full" style={{width: '65%'}}></div>
                </div>
                
                <div className="flex justify-between">
                  <span>Food & Dining</span>
                  <span className="text-orange-400">$320.50</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-orange-400 h-2 rounded-full" style={{width: '45%'}}></div>
                </div>
                
                <div className="flex justify-between">
                  <span>Bills & Utilities</span>
                  <span className="text-yellow-400">$680.25</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-yellow-400 h-2 rounded-full" style={{width: '95%'}}></div>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Account Summary</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span>Total Assets</span>
                  <span className="text-green-400 font-bold">$47,650.95</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Total Liabilities</span>
                  <span className="text-red-400 font-bold">$1,250.30</span>
                </div>
                <div className="border-t border-slate-600 pt-3">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Net Worth</span>
                    <span className="text-blue-400 font-bold text-xl">$46,400.65</span>
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