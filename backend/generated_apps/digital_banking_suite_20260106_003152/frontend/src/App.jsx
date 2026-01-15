import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 5420.50, number: '****1234' },
    { id: 'savings', name: 'Savings Account', balance: 12850.75, number: '****5678' },
    { id: 'credit', name: 'Credit Card', balance: -1240.30, number: '****9012' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Grocery Store', amount: -125.50, status: 'Completed' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 3500.00, status: 'Completed' },
    { id: 3, date: '2024-01-13', description: 'Electric Bill', amount: -89.25, status: 'Completed' },
    { id: 4, date: '2024-01-12', description: 'Online Transfer', amount: -250.00, status: 'Pending' },
    { id: 5, date: '2024-01-11', description: 'Restaurant', amount: -65.80, status: 'Completed' }
  ];

  const payments = [
    { id: 1, payee: 'John Doe', account: '****4567', amount: 500, date: '2024-01-10' },
    { id: 2, payee: 'Electric Company', account: '****7890', amount: 89.25, date: '2024-01-13' },
    { id: 3, payee: 'Credit Card Payment', account: '****9012', amount: 1000, date: '2024-01-05' }
  ];

  const [transferForm, setTransferForm] = React.useState({
    from: 'checking',
    to: 'savings',
    amount: ''
  });

  const handleTransfer = (e) => {
    e.preventDefault();
    alert(`Transfer of $${transferForm.amount} initiated successfully!`);
    setTransferForm({ ...transferForm, amount: '' });
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage('dashboard')}
                className={`px-4 py-2 rounded transition ${
                  currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'
                }`}
              >
                Dashboard
              </button>
              <button
                onClick={() => setCurrentPage('payments')}
                className={`px-4 py-2 rounded transition ${
                  currentPage === 'payments' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'
                }`}
              >
                Payments
              </button>
              <button
                onClick={() => setCurrentPage('analytics')}
                className={`px-4 py-2 rounded transition ${
                  currentPage === 'analytics' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'
                }`}
              >
                Analytics
              </button>
            </div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-6 py-8">
        {currentPage === 'dashboard' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Account Overview</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  onClick={() => setSelectedAccount(account.id)}
                  className={`bg-slate-800 p-6 rounded-lg cursor-pointer transition border-2 ${
                    selectedAccount === account.id ? 'border-blue-500' : 'border-transparent hover:border-slate-600'
                  }`}
                >
                  <div className="text-slate-400 text-sm mb-2">{account.name}</div>
                  <div className="text-3xl font-bold mb-2">
                    ${Math.abs(account.balance).toLocaleString('en-US', { minimumFractionDigits: 2 })}
                  </div>
                  <div className="text-slate-500 text-sm">{account.number}</div>
                </div>
              ))}
            </div>

            <div className="bg-slate-800 rounded-lg p-6">
              <h3 className="text-xl font-semibold mb-4">Recent Transactions</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-slate-700">
                      <th className="text-left py-3 px-2 text-slate-400 font-medium">Date</th>
                      <th className="text-left py-3 px-2 text-slate-400 font-medium">Description</th>
                      <th className="text-right py-3 px-2 text-slate-400 font-medium">Amount</th>
                      <th className="text-right py-3 px-2 text-slate-400 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((txn) => (
                      <tr key={txn.id} className="border-b border-slate-700 hover:bg-slate-700">
                        <td className="py-3 px-2">{txn.date}</td>
                        <td className="py-3 px-2">{txn.description}</td>
                        <td className={`py-3 px-2 text-right font-semibold ${txn.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                          {txn.amount > 0 ? '+' : ''}{txn.amount.toFixed(2)}
                        </td>
                        <td className="py-3 px-2 text-right">
                          <span className={`px-2 py-1 rounded text-xs ${txn.status === 'Completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                            {txn.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'payments' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Payments & Transfers</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-800 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4">Quick Transfer</h3>
                <form onSubmit={handleTransfer} className="space-y-4">
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">From Account</label>
                    <select
                      value={transferForm.from}
                      onChange={(e) => setTransferForm({ ...transferForm, from: e.target.value })}
                      className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
                    >
                      {accounts.map((acc) => (
                        <option key={acc.id} value={acc.id}>{acc.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">To Account</label>
                    <select
                      value={transferForm.to}
                      onChange={(e) => setTransferForm({ ...transferForm, to: e.target.value })}
                      className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
                    >
                      {accounts.map((acc) => (
                        <option key={acc.id} value={acc.id}>{acc.name}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-slate-400 mb-2">Amount</label>
                    <input
                      type="number"
                      value={transferForm.amount}
                      onChange={(e) => setTransferForm({ ...transferForm, amount: e.target.value })}
                      placeholder="0.00"
                      className="w-full bg-slate-700 border border-slate-600 rounded px-4 py-2 text-white"
                      required
                    />
                  </div>
                  <button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 rounded px-4 py-3 font-semibold transition">
                    Transfer Now
                  </button>
                </form>
              </div>

              <div className="bg-slate-800 rounded-lg p-6">
                <h3 className="text-xl font-semibold mb-4">Recent Payments</h3>
                <div className="space-y-3">
                  {payments.map((payment) => (
                    <div key={payment.id} className="bg-slate-700 rounded p-4 flex justify-between items-center">
                      <div>
                        <div className="font-semibold">{payment.payee}</div>
                        <div className="text-sm text-slate-400">{payment.account} • {payment.date}</div>
                      </div>
                      <div className="text-lg font-bold text-red-400">-${payment.amount.toFixed(2)}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {currentPage === 'analytics' && (
          <div>
            <h2 className="text-3xl font-bold mb-6">Financial Analytics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm mb-2">Total Balance</div>
                <div className="text-2xl font-bold text-green-400">$17,031.00</div>
                <div className="text-xs text-slate-500 mt-1">+2.5% from last month</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm mb-2">Monthly Income</div>
                <div className="text-2xl font-bold text-blue-400">$3,500.00</div>
                <div className="text-xs text-slate-500 mt-1">Last deposit: Jan 14</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm mb-2">Monthly Expenses</div>
                <div className="text-2xl font-bold text-red-400">$1,530.55</div>
                <div className="text-xs text-slate-500 mt-1">-12% from last month</div>
              </div>
              <div className="bg-slate-800 p-6 rounded-lg">
                <div className="text-slate-400 text-sm mb-2">Savings Rate</div>
                <div className="text-2xl font-bold text-purple-400">56%</div>
                <div className="text-xs text-slate-500 mt-1">Above average</div>
              </div>
            </div>

            <div className="bg-slate-800 rounded-lg p-6 mb-6">
              <h3 className="text-xl font-semibold mb-4">Spending by Category</h3>
              <div className="space-y-4">
                {[
                  { category: 'Groceries', amount: 450, percent: 29, color: 'bg-blue-500' },
                  { category: 'Utilities', amount: 320, percent: 21, color: 'bg-green-500' },
                  { category: 'Dining', amount: 280, percent: 18, color: 'bg-yellow-500' },
                  { category: 'Transportation', amount: 220, percent: 14, color: 'bg-purple-500' },
                  { category: 'Entertainment', amount: 180, percent: 12, color: 'bg-pink-500' },
                  { category: 'Other', amount: 80, percent: 6, color: 'bg-slate-600' }
                ].map((item) => (
                  <div key={item.category}>
                    <div className="flex justify-between mb-1">
                      <span>{item.category}</span>
                      <span className="font-semibold">${item.amount.toFixed(2)} ({item.percent}%)</span>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div className={`${item.color} h-2 rounded-full`} style={{ width: `${item.percent}%` }}></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

App;

export default App;