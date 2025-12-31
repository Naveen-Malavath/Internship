import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  const mockAccounts = [
    { id: 1, name: 'Checking', balance: 5420.50, type: 'checking' },
    { id: 2, name: 'Savings', balance: 12850.00, type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -1205.30, type: 'credit' }
  ];

  const mockTransactions = [
    { id: 1, description: 'Grocery Store', amount: -85.40, date: '2024-01-15', category: 'Food' },
    { id: 2, description: 'Salary Deposit', amount: 3200.00, date: '2024-01-14', category: 'Income' },
    { id: 3, description: 'Gas Station', amount: -42.50, date: '2024-01-13', category: 'Transport' },
    { id: 4, description: 'Online Transfer', amount: -500.00, date: '2024-01-12', category: 'Transfer' }
  ];

  const [transferAmount, setTransferAmount] = React.useState('');
  const [transferTo, setTransferTo] = React.useState('');

  const handleTransfer = () => {
    if (transferAmount && transferTo) {
      alert(`Transfer of $${transferAmount} to ${transferTo} initiated successfully!`);
      setTransferAmount('');
      setTransferTo('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-4 shadow-lg">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('transfer')}
              className={`px-4 py-2 rounded ${currentPage === 'transfer' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Transfer
            </button>
            <button 
              onClick={() => setCurrentPage('analytics')}
              className={`px-4 py-2 rounded ${currentPage === 'analytics' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Analytics
            </button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Account Dashboard</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {mockAccounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg">
                <h3 className="text-lg font-semibold mb-2">{account.name}</h3>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${account.balance.toFixed(2)}
                </p>
                <p className="text-slate-400 capitalize">{account.type} Account</p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
            <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
            <div className="space-y-3">
              {mockTransactions.map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date} • {transaction.category}</p>
                  </div>
                  <span className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    ${Math.abs(transaction.amount).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'transfer' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Money Transfer</h1>
          
          <div className="max-w-md mx-auto bg-slate-800 p-6 rounded-lg shadow-lg">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">From Account</label>
              <select className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500">
                <option>Checking - $5,420.50</option>
                <option>Savings - $12,850.00</option>
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">To Account/Recipient</label>
              <input 
                type="text"
                value={transferTo}
                onChange={(e) => setTransferTo(e.target.value)}
                placeholder="Enter account number or email"
                className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500"
              />
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Amount</label>
              <input 
                type="number"
                value={transferAmount}
                onChange={(e) => setTransferAmount(e.target.value)}
                placeholder="0.00"
                className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500"
              />
            </div>
            
            <button 
              onClick={handleTransfer}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded transition duration-200"
            >
              Transfer Money
            </button>
          </div>
        </div>
      )}
      
      {currentPage === 'analytics' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Financial Analytics</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-lg font-semibold mb-4">Monthly Spending</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Food & Dining</span>
                  <span className="text-red-400">$340.50</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Transportation</span>
                  <span className="text-red-400">$180.20</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Shopping</span>
                  <span className="text-red-400">$225.80</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Utilities</span>
                  <span className="text-red-400">$150.00</span>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
              <h3 className="text-lg font-semibold mb-4">Account Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Total Assets</span>
                  <span className="text-green-400">$18,270.50</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Total Liabilities</span>
                  <span className="text-red-400">$1,205.30</span>
                </div>
                <div className="flex justify-between items-center font-bold">
                  <span>Net Worth</span>
                  <span className="text-green-400">$17,065.20</span>
                </div>
              </div>
            </div>
          </div>
          
          <div className="bg-slate-800 p-6 rounded-lg shadow-lg">
            <h3 className="text-lg font-semibold mb-4">Spending Trends</h3>
            <div className="flex justify-center items-center h-32 text-slate-400">
              <p>Chart visualization would appear here</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

App;

export default App;