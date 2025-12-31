import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState(0);

  const accounts = [
    { id: 1, name: 'Checking Account', balance: 12450.75, accountNumber: '****1234', type: 'checking' },
    { id: 2, name: 'Savings Account', balance: 35200.00, accountNumber: '****5678', type: 'savings' },
    { id: 3, name: 'Credit Card', balance: -2850.25, accountNumber: '****9012', type: 'credit' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Grocery Store Payment', amount: -125.50, category: 'Food' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3500.00, category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Netflix Subscription', amount: -15.99, category: 'Entertainment' },
    { id: 4, date: '2024-01-12', description: 'Gas Station', amount: -45.20, category: 'Transportation' },
    { id: 5, date: '2024-01-11', description: 'Online Transfer', amount: -500.00, category: 'Transfer' }
  ];

  const paymentContacts = [
    { id: 1, name: 'John Smith', email: 'john@email.com', lastPaid: '$250.00' },
    { id: 2, name: 'Sarah Johnson', email: 'sarah@email.com', lastPaid: '$75.50' },
    { id: 3, name: 'Mike Wilson', email: 'mike@email.com', lastPaid: '$120.00' }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-6 shadow-lg">
        <div className="flex justify-between items-center">
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
          <h1 className="text-3xl font-bold mb-6">Account Dashboard</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            {accounts.map((account, index) => (
              <div 
                key={account.id} 
                className={`bg-slate-800 p-6 rounded-lg cursor-pointer transition-all hover:bg-slate-700 ${selectedAccount === index ? 'ring-2 ring-blue-500' : ''}`}
                onClick={() => setSelectedAccount(index)}
              >
                <h3 className="text-lg font-semibold mb-2">{account.name}</h3>
                <p className="text-2xl font-bold text-green-400 mb-1">
                  ${account.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                </p>
                <p className="text-slate-400 text-sm">{account.accountNumber}</p>
              </div>
            ))}
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
            <div className="space-y-3">
              {transactions.map((transaction) => (
                <div key={transaction.id} className="flex justify-between items-center py-3 border-b border-slate-700 last:border-b-0">
                  <div>
                    <p className="font-medium">{transaction.description}</p>
                    <p className="text-sm text-slate-400">{transaction.date} • {transaction.category}</p>
                  </div>
                  <span className={`font-bold ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {transaction.amount > 0 ? '+' : ''}${Math.abs(transaction.amount).toFixed(2)}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {currentPage === 'payments' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Send Money</h1>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">New Payment</h2>
              <form className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Recipient</label>
                  <input type="text" placeholder="Email or phone number" className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Amount</label>
                  <input type="number" placeholder="0.00" className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 focus:outline-none" />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-2">Message (Optional)</label>
                  <textarea placeholder="What's this for?" className="w-full p-3 bg-slate-700 rounded border border-slate-600 focus:border-blue-500 focus:outline-none h-24 resize-none"></textarea>
                </div>
                <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 py-3 rounded font-medium transition-colors">
                  Send Payment
                </button>
              </form>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-semibold mb-4">Quick Pay Contacts</h2>
              <div className="space-y-3">
                {paymentContacts.map((contact) => (
                  <div key={contact.id} className="flex justify-between items-center p-3 bg-slate-700 rounded hover:bg-slate-600 cursor-pointer transition-colors">
                    <div>
                      <p className="font-medium">{contact.name}</p>
                      <p className="text-sm text-slate-400">{contact.email}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm text-slate-400">Last: {contact.lastPaid}</p>
                      <button className="text-blue-400 hover:text-blue-300 text-sm font-medium">Pay Now</button>
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
          <h1 className="text-3xl font-bold mb-6">Spending Analytics</h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">This Month</h3>
              <p className="text-2xl font-bold text-red-400">-$1,256.89</p>
              <p className="text-sm text-slate-400">↑ 12% from last month</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Average Daily</h3>
              <p className="text-2xl font-bold text-yellow-400">$83.79</p>
              <p className="text-sm text-slate-400">↓ 5% from last month</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Top Category</h3>
              <p className="text-2xl font-bold text-blue-400">Food</p>
              <p className="text-sm text-slate-400">$423.67 this month</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-lg font-semibold mb-2">Budget Left</h3>
              <p className="text-2xl font-bold text-green-400">$743.11</p>
              <p className="text-sm text-slate-400">63% remaining</p>
            </div>
          </div>

          <div className="bg-slate-800 p-6 rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Spending by Category</h2>
            <div className="space-y-4">
              {[
                { category: 'Food', amount: 423.67, percentage: 34 },
                { category: 'Transportation', amount: 256.89, percentage: 20 },
                { category: 'Entertainment', amount: 189.45, percentage: 15 },
                { category: 'Shopping', amount: 234.12, percentage: 19 },
                { category: 'Utilities', amount: 152.76, percentage: 12 }
              ].map((item) => (
                <div key={item.category} className="flex justify-between items-center">
                  <div className="flex items-center flex-1">
                    <span className="w-20 text-sm">{item.category}</span>
                    <div className="flex-1 mx-4 bg-slate-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full" 
                        style={{ width: `${item.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-slate-400">{item.percentage}%</span>
                  </div>
                  <span className="ml-4 font-medium">${item.amount.toFixed(2)}</span>
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