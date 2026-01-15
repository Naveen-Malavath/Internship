import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  
  // Mock data
  const accountSummary = {
    balance: 15420.50,
    accountNumber: "**** 4729",
    totalTransactions: 24,
    pendingPayments: 3
  };

  const recentTransactions = [
    { id: 1, description: "Online Purchase", amount: -129.99, date: "2024-01-15", status: "Completed" },
    { id: 2, description: "Salary Deposit", amount: 3200.00, date: "2024-01-14", status: "Completed" },
    { id: 3, description: "Utility Payment", amount: -85.40, date: "2024-01-13", status: "Completed" },
    { id: 4, description: "Transfer to Savings", amount: -500.00, date: "2024-01-12", status: "Completed" }
  ];

  const orders = [
    { id: "ORD001", merchant: "Amazon", amount: 129.99, date: "2024-01-15", status: "Processing" },
    { id: "ORD002", merchant: "Netflix", amount: 15.99, date: "2024-01-10", status: "Completed" },
    { id: "ORD003", merchant: "Spotify", amount: 9.99, date: "2024-01-08", status: "Completed" },
    { id: "ORD004", merchant: "Grocery Store", amount: 89.45, date: "2024-01-05", status: "Completed" }
  ];

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 p-4 mb-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold">Digital Banking Suite</h1>
          <div>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded mr-2 ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('orders')}
              className={`px-4 py-2 rounded ${currentPage === 'orders' ? 'bg-blue-600' : 'bg-slate-700'}`}
            >
              Orders & Transactions
            </button>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
          
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Account Balance</h3>
              <p className="text-2xl font-bold text-green-400">${accountSummary.balance.toLocaleString()}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Account</h3>
              <p className="text-2xl font-bold">{accountSummary.accountNumber}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Total Transactions</h3>
              <p className="text-2xl font-bold">{accountSummary.totalTransactions}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Pending Payments</h3>
              <p className="text-2xl font-bold text-yellow-400">{accountSummary.pendingPayments}</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
              <div className="space-y-3">
                <button className="w-full bg-blue-600 hover:bg-blue-700 p-3 rounded-lg text-left">
                  Transfer Money
                </button>
                <button className="w-full bg-green-600 hover:bg-green-700 p-3 rounded-lg text-left">
                  Pay Bills
                </button>
                <button className="w-full bg-purple-600 hover:bg-purple-700 p-3 rounded-lg text-left">
                  Mobile Top-up
                </button>
              </div>
            </div>

            <div className="bg-slate-800 p-6 rounded-lg">
              <h2 className="text-xl font-bold mb-4">Recent Transactions</h2>
              <div className="space-y-3">
                {recentTransactions.slice(0, 4).map(transaction => (
                  <div key={transaction.id} className="flex justify-between items-center border-b border-slate-700 pb-2">
                    <div>
                      <p className="text-sm">{transaction.description}</p>
                      <p className="text-xs text-gray-400">{transaction.date}</p>
                    </div>
                    <p className={`font-bold ${transaction.amount > 0 ? 'text-green-400' : 'text-red-400'}`}>
                      ${Math.abs(transaction.amount).toFixed(2)}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
      
      {currentPage === 'orders' && (
        <div className="p-8">
          <h1 className="text-3xl font-bold mb-6">Orders & Transactions</h1>
          
          <div className="grid grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Total Orders</h3>
              <p className="text-2xl font-bold">{orders.length}</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">This Month</h3>
              <p className="text-2xl font-bold">4</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Amount Spent</h3>
              <p className="text-2xl font-bold text-red-400">$245.42</p>
            </div>
            <div className="bg-slate-800 p-6 rounded-lg">
              <h3 className="text-gray-400 text-sm">Processing</h3>
              <p className="text-2xl font-bold text-yellow-400">1</p>
            </div>
          </div>

          <div className="bg-slate-800 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Transaction History</h2>
              <input 
                type="text" 
                placeholder="Search transactions..." 
                className="bg-slate-700 px-4 py-2 rounded-lg text-white placeholder-gray-400"
              />
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left p-3">Order ID</th>
                    <th className="text-left p-3">Merchant</th>
                    <th className="text-left p-3">Amount</th>
                    <th className="text-left p-3">Date</th>
                    <th className="text-left p-3">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map(order => (
                    <tr key={order.id} className="border-b border-slate-700 hover:bg-slate-700">
                      <td className="p-3">{order.id}</td>
                      <td className="p-3">{order.merchant}</td>
                      <td className="p-3 text-red-400">-${order.amount}</td>
                      <td className="p-3 text-gray-400">{order.date}</td>
                      <td className="p-3">
                        <span className={`px-2 py-1 rounded text-xs ${
                          order.status === 'Completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'
                        }`}>
                          {order.status}
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
    </div>
  );
};

App;

export default App;