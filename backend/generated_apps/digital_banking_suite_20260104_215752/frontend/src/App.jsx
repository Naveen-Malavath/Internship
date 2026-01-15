import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  const mockAccounts = [
    { id: 1, name: 'Checking Account', balance: 5430.20, type: 'checking' },
    { id: 2, name: 'Savings Account', balance: 12750.85, type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -1240.50, type: 'credit' }
  ];

  const mockTransactions = [
    { id: 1, description: 'Amazon Purchase', amount: -89.99, date: '2024-01-15', category: 'Shopping' },
    { id: 2, description: 'Salary Deposit', amount: 3500.00, date: '2024-01-14', category: 'Income' },
    { id: 3, description: 'Coffee Shop', amount: -4.75, date: '2024-01-13', category: 'Food' },
    { id: 4, description: 'Gas Station', amount: -45.20, date: '2024-01-12', category: 'Transport' }
  ];

  const [transferAmount, setTransferAmount] = React.useState('');
  const [fromAccount, setFromAccount] = React.useState('1');
  const [toAccount, setToAccount] = React.useState('2');

  const handleTransfer = () => {
    alert(`Transfer of $${transferAmount} from Account ${fromAccount} to Account ${toAccount} initiated!`);
    setTransferAmount('');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transfer')}
              className={`px-4 py-2 rounded ${currentPage === 'transfer' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Transfer
            </button>
            <button 
              onClick={() => setCurrentPage('transactions')}
              className={`px-4 py-2 rounded ${currentPage === 'transactions' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Transactions
            </button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && (
        <div className="p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">Welcome back, John!</h1>
            <p className="text-slate-400">Here's your financial overview</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {mockAccounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold">{account.name}</h3>
                  <span className={`px-2 py-1 rounded text-xs ${
                    account.type === 'checking' ? 'bg-green-900 text-green-300' :
                    account.type === 'savings' ? 'bg-blue-900 text-blue-300' :
                    'bg-red-900 text-red-300'
                  }`}>
                    {account.type}
                  </span>
                </div>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${account.balance.toFixed(2)}
                </p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
            <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {mockTransactions.slice(0, 3).map(transaction => (
                <div key={transaction.id} className="flex items-center justify-between p-3 bg-slate-700 rounded">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date}</p>
                  </div>
                  <span className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    ${transaction.amount.toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'transfer' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Transfer Funds</h1>
          
          <div className="max-w-md mx-auto bg-slate-800 p-6 rounded-lg border border-slate-700">
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">From Account</label>
                <select 
                  value={fromAccount} 
                  onChange={(e) => setFromAccount(e.target.value)}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                >
                  {mockAccounts.map(account => (
                    <option key={account.id} value={account.id.toString()}>
                      {account.name} - ${account.balance.toFixed(2)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">To Account</label>
                <select 
                  value={toAccount} 
                  onChange={(e) => setToAccount(e.target.value)}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                >
                  {mockAccounts.map(account => (
                    <option key={account.id} value={account.id.toString()}>
                      {account.name} - ${account.balance.toFixed(2)}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Amount</label>
                <input
                  type="number"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded focus:outline-none focus:border-blue-500"
                />
              </div>
              
              <button 
                onClick={handleTransfer}
                disabled={!transferAmount || fromAccount === toAccount}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded font-medium transition-colors"
              >
                Transfer Funds
              </button>
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'transactions' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Transaction History</h1>
          
          <div className="bg-slate-800 rounded-lg border border-slate-700 overflow-hidden">
            <div className="p-4 border-b border-slate-700">
              <h3 className="text-lg font-semibold">All Transactions</h3>
            </div>
            
            <div className="divide-y divide-slate-700">
              {mockTransactions.map(transaction => (
                <div key={transaction.id} className="p-4 hover:bg-slate-750">
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <p className="font-medium">{transaction.description}</p>
                      <div className="flex items-center space-x-4 text-sm text-slate-400 mt-1">
                        <span>{transaction.date}</span>
                        <span className="px-2 py-1 bg-slate-700 rounded text-xs">{transaction.category}</span>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-lg font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                        {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;