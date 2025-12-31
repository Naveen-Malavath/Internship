
const App = () => {
  const [currentPage, setCurrentPage] = React.useState('accounts');
  const [selectedAccount, setSelectedAccount] = React.useState(null);

  const accounts = [
    { id: 1, name: 'Checking Account', balance: 12450.89, type: 'checking', number: '****1234' },
    { id: 2, name: 'Savings Account', balance: 25680.45, type: 'savings', number: '****5678' },
    { id: 3, name: 'Credit Card', balance: -2340.12, type: 'credit', number: '****9012' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Online Purchase - Amazon', amount: -89.99, type: 'debit' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3500.00, type: 'credit' },
    { id: 3, date: '2024-01-13', description: 'ATM Withdrawal', amount: -200.00, type: 'debit' },
    { id: 4, date: '2024-01-12', description: 'Transfer to Savings', amount: -500.00, type: 'transfer' },
    { id: 5, date: '2024-01-11', description: 'Utility Payment', amount: -156.78, type: 'debit' }
  ];

  const paymentTemplates = [
    { id: 1, name: 'Electric Bill', recipient: 'Power Company', amount: 156.78 },
    { id: 2, name: 'Rent Payment', recipient: 'Property Management', amount: 1200.00 },
    { id: 3, name: 'Phone Bill', recipient: 'Telecom Provider', amount: 89.99 }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
          <div className="flex space-x-2">
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
            <button 
              onClick={() => setCurrentPage('analytics')}
              className={`px-4 py-2 rounded transition ${currentPage === 'analytics' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Analytics
            </button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'accounts' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {accounts.map(account => (
              <div key={account.id} className="bg-slate-800 p-6 rounded-lg shadow-lg">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold">{account.name}</h3>
                    <p className="text-slate-400">{account.number}</p>
                  </div>
                  <span className={`px-2 py-1 rounded text-sm ${account.type === 'credit' ? 'bg-red-600' : 'bg-green-600'}`}>
                    {account.type}
                  </span>
                </div>
                <p className={`text-3xl font-bold ${account.balance < 0 ? 'text-red-400' : 'text-green-400'}`}>
                  ${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
                <button 
                  onClick={() => setSelectedAccount(account)}
                  className="mt-4 w-full bg-blue-600 hover:bg-blue-700 py-2 rounded transition"
                >
                  View Details
                </button>
              </div>
            ))}
          </div>
          
          <div className="bg-slate-800 p-6 rounded-lg">
            <h3 className="text-2xl font-semibold mb-4">Recent Transactions</h3>
            <div className="space-y-3">
              {transactions.slice(0, 5).map(transaction => (
                <div key={transaction.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-slate-400 text-sm">{transaction.date}</p>
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
      
      {currentPage === 'payments' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Payments & Transfers</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Quick Payment</h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-1">From Account</label>
                  <select className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2">
                    <option>Checking Account (****1234)</option>
                    <option>Savings Account (****5678)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Recipient</label>
                  <input type="text" placeholder="Enter recipient name" className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">Amount</label>
                  <input type="number" placeholder="0.00" className="w-full bg-slate-700 border border-slate-600 rounded px-3 py-2" />
                </div>
                <button className="w-full bg-green-600 hover:bg-green-700 py-2 rounded transition">
                  Send Payment
                </button>
              </div>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Payment Templates</h3>
              <div className="space-y-3">
                {paymentTemplates.map(template => (
                  <div key={template.id} className="flex justify-between items-center p-3 bg-slate-700 rounded">
                    <div>
                      <p className="font-medium">{template.name}</p>
                      <p className="text-slate-400 text-sm">{template.recipient}</p>
                    </div>
                    <div className="text-right">
                      <p className="font-bold">${template.amount.toFixed(2)}</p>
                      <button className="text-blue-400 hover:text-blue-300 text-sm">Pay Now</button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'analytics' && (
        <div className="p-6">
          <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-4 rounded-lg text-center">
              <h4 className="text-lg font-semibold text-blue-400">Monthly Income</h4>
              <p className="text-2xl font-bold text-green-400">$3,500.00</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg text-center">
              <h4 className="text-lg font-semibold text-blue-400">Monthly Expenses</h4>
              <p className="text-2xl font-bold text-red-400">$2,156.78</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg text-center">
              <h4 className="text-lg font-semibold text-blue-400">Savings Rate</h4>
              <p className="text-2xl font-bold text-yellow-400">38.4%</p>
            </div>
            <div className="bg-slate-800 p-4 rounded-lg text-center">
              <h4 className="text-lg font-semibold text-blue-400">Credit Score</h4>
              <p className="text-2xl font-bold text-green-400">742</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Spending by Category</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span>Utilities</span>
                  <span className="font-bold">$456.78</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Groceries</span>
                  <span className="font-bold">$324.50</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Entertainment</span>
                  <span className="font-bold">$189.99</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Transportation</span>
                  <span className="font-bold">$267.45</span>
                </div>
              </div>
            </div>
            
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-xl font-semibold mb-4">Account Growth</h3>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-slate-400">This Month</p>
                  <p className="text-xl font-bold text-green-400">+$1,343.22</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Last Month</p>
                  <p className="text-xl font-bold text-green-400">+$987.65</p>
                </div>
                <div>
                  <p className="text-sm text-slate-400">Year to Date</p>
                  <p className="text-xl font-bold text-green-400">+$15,234.87</p>
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