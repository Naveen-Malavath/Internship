
const App = () => {
  const [currentPage, setCurrentPage] = React.useState('accounts');

  const mockAccounts = [
    { id: 1, name: 'Checking Account', balance: 5240.50, type: 'checking' },
    { id: 2, name: 'Savings Account', balance: 12890.75, type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -1250.00, type: 'credit' }
  ];

  const mockTransactions = [
    { id: 1, date: '2024-01-15', description: 'Direct Deposit', amount: 3200.00, type: 'credit' },
    { id: 2, date: '2024-01-14', description: 'Coffee Shop', amount: -4.50, type: 'debit' },
    { id: 3, date: '2024-01-13', description: 'Gas Station', amount: -45.20, type: 'debit' },
    { id: 4, date: '2024-01-12', description: 'Online Transfer', amount: -500.00, type: 'debit' },
    { id: 5, date: '2024-01-11', description: 'Interest Payment', amount: 25.30, type: 'credit' }
  ];

  const [transferAmount, setTransferAmount] = React.useState('');
  const [transferFrom, setTransferFrom] = React.useState('1');
  const [transferTo, setTransferTo] = React.useState('2');

  const handleTransfer = () => {
    alert(`Transfer of $${transferAmount} from account ${transferFrom} to account ${transferTo} initiated`);
    setTransferAmount('');
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
            <button 
              onClick={() => setCurrentPage('accounts')}
              className={`px-4 py-2 rounded transition-colors ${currentPage === 'accounts' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Accounts
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
      
      {currentPage === 'accounts' && (
        <div className="max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {mockAccounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg border border-slate-700">
                <h3 className="text-xl font-semibold mb-2">{account.name}</h3>
                <p className="text-3xl font-bold text-green-400 mb-2">
                  ${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
                <span className={`inline-block px-3 py-1 rounded-full text-sm ${
                  account.type === 'credit' ? 'bg-red-600' : 'bg-blue-600'
                }`}>
                  {account.type.toUpperCase()}
                </span>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <h3 className="text-2xl font-semibold mb-4">Recent Transactions</h3>
            <div className="space-y-3">
              {mockTransactions.map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center py-3 border-b border-slate-700 last:border-b-0">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date}</p>
                  </div>
                  <span className={`font-bold ${transaction.type === 'credit' ? 'text-green-400' : 'text-red-400'}`}>
                    {transaction.type === 'credit' ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'transfer' && (
        <div className="max-w-2xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Transfer Funds</h2>
          
          <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium mb-2">From Account</label>
                <select 
                  value={transferFrom}
                  onChange={(e) => setTransferFrom(e.target.value)}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {mockAccounts.map(account => (
                    <option key={account.id} value={account.id}>{account.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">To Account</label>
                <select 
                  value={transferTo}
                  onChange={(e) => setTransferTo(e.target.value)}
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {mockAccounts.map(account => (
                    <option key={account.id} value={account.id}>{account.name}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium mb-2">Amount ($)</label>
                <input 
                  type="number"
                  value={transferAmount}
                  onChange={(e) => setTransferAmount(e.target.value)}
                  placeholder="0.00"
                  className="w-full p-3 bg-slate-700 border border-slate-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              
              <button 
                onClick={handleTransfer}
                disabled={!transferAmount || transferFrom === transferTo}
                className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 disabled:cursor-not-allowed rounded-md font-semibold transition-colors"
              >
                Transfer Funds
              </button>
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'analytics' && (
        <div className="max-w-6xl mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-semibold mb-2">Total Balance</h3>
              <p className="text-2xl font-bold text-green-400">$16,881.25</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-semibold mb-2">Monthly Income</h3>
              <p className="text-2xl font-bold text-blue-400">$3,225.30</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-semibold mb-2">Monthly Expenses</h3>
              <p className="text-2xl font-bold text-red-400">$2,549.70</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-lg font-semibold mb-2">Net Savings</h3>
              <p className="text-2xl font-bold text-green-400">$675.60</p>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-semibold mb-4">Spending Categories</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Groceries</span>
                  <span className="font-bold">$650.20</span>
                </div>
                <div className="flex justify-between">
                  <span>Utilities</span>
                  <span className="font-bold">$280.15</span>
                </div>
                <div className="flex justify-between">
                  <span>Entertainment</span>
                  <span className="font-bold">$195.80</span>
                </div>
                <div className="flex justify-between">
                  <span>Transportation</span>
                  <span className="font-bold">$320.45</span>
                </div>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
              <h3 className="text-xl font-semibold mb-4">Account Performance</h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span>Savings Growth</span>
                  <span className="font-bold text-green-400">+2.3%</span>
                </div>
                <div className="flex justify-between">
                  <span>Credit Utilization</span>
                  <span className="font-bold text-yellow-400">18.5%</span>
                </div>
                <div className="flex justify-between">
                  <span>Investment Returns</span>
                  <span className="font-bold text-green-400">+5.7%</span>
                </div>
                <div className="flex justify-between">
                  <span>Monthly Cashflow</span>
                  <span className="font-bold text-green-400">+$675</span>
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