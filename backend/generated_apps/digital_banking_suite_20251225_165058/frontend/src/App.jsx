import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');

  const mockAccounts = [
    { id: 1, name: 'Checking Account', balance: 2450.75, type: 'checking' },
    { id: 2, name: 'Savings Account', balance: 15680.20, type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -850.45, type: 'credit' }
  ];

  const mockTransactions = [
    { id: 1, date: '2024-01-15', description: 'Coffee Shop', amount: -4.50, type: 'debit' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3200.00, type: 'credit' },
    { id: 3, date: '2024-01-13', description: 'Gas Station', amount: -45.20, type: 'debit' },
    { id: 4, date: '2024-01-12', description: 'Online Transfer', amount: -150.00, type: 'debit' }
  ];

  const [transferAmount, setTransferAmount] = React.useState('');
  const [selectedFromAccount, setSelectedFromAccount] = React.useState('');
  const [selectedToAccount, setSelectedToAccount] = React.useState('');

  const handleTransfer = () => {
    if (transferAmount && selectedFromAccount && selectedToAccount) {
      alert(`Transfer of $${transferAmount} initiated from ${selectedFromAccount} to ${selectedToAccount}`);
      setTransferAmount('');
      setSelectedFromAccount('');
      setSelectedToAccount('');
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-4 shadow-lg">
        <div className="flex justify-between items-center">
          <h1 className="text-xl font-bold text-blue-400">SecureBank</h1>
          <div className="space-x-2">
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
          <h2 className="text-3xl font-bold mb-6">Account Dashboard</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {mockAccounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg">
                <h3 className="text-lg font-semibold mb-2 text-blue-400">{account.name}</h3>
                <p className={`text-2xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${account.balance.toFixed(2)}
                </p>
                <p className="text-slate-400 text-sm capitalize">{account.type} Account</p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <h3 className="text-xl font-semibold mb-4">Recent Transactions</h3>
            <div className="space-y-3">
              {mockTransactions.map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-slate-400 text-sm">{transaction.date}</p>
                  </div>
                  <div className={`font-bold ${transaction.amount < 0 ? 'text-red-400' : 'text-green-400'}`}>
                    {transaction.amount < 0 ? '-' : '+'}${Math.abs(transaction.amount).toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'transfer' && (
        <div className="p-8">
          <h2 className="text-3xl font-bold mb-6">Money Transfer</h2>
          
          <div className="max-w-md mx-auto bg-slate-800 p-6 rounded-lg">
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">From Account</label>
              <select 
                value={selectedFromAccount}
                onChange={(e) => setSelectedFromAccount(e.target.value)}
                className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500"
              >
                <option value="">Select Account</option>
                {mockAccounts.map(account => (
                  <option key={account.id} value={account.name}>
                    {account.name} - ${account.balance.toFixed(2)}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">To Account</label>
              <select 
                value={selectedToAccount}
                onChange={(e) => setSelectedToAccount(e.target.value)}
                className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500"
              >
                <option value="">Select Account</option>
                {mockAccounts.map(account => (
                  <option key={account.id} value={account.name}>
                    {account.name}
                  </option>
                ))}
              </select>
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
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded transition-colors"
            >
              Transfer Funds
            </button>
          </div>
        </div>
      )}
      
      {currentPage === 'analytics' && (
        <div className="p-8">
          <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Spending Overview</h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span>Dining</span>
                  <span className="font-bold">$245.50</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full" style={{width: '60%'}}></div>
                </div>
                
                <div className="flex justify-between">
                  <span>Transportation</span>
                  <span className="font-bold">$180.20</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-green-600 h-2 rounded-full" style={{width: '45%'}}></div>
                </div>
                
                <div className="flex justify-between">
                  <span>Shopping</span>
                  <span className="font-bold">$320.75</span>
                </div>
                <div className="w-full bg-slate-700 rounded-full h-2">
                  <div className="bg-purple-600 h-2 rounded-full" style={{width: '80%'}}></div>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Monthly Summary</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Total Income</span>
                  <span className="text-green-400 font-bold">+$6,400.00</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Total Expenses</span>
                  <span className="text-red-400 font-bold">-$2,850.45</span>
                </div>
                <div className="border-t border-slate-600 pt-3">
                  <div className="flex justify-between items-center">
                    <span className="font-semibold">Net Income</span>
                    <span className="text-blue-400 font-bold">+$3,549.55</span>
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