import React from 'react';

const App = () => {
  const [currentPage, setCurrentPage] = React.useState('dashboard');
  const [selectedAccount, setSelectedAccount] = React.useState('checking');

  const accounts = [
    { id: 'checking', name: 'Checking Account', balance: 12458.32, number: '****4521' },
    { id: 'savings', name: 'Savings Account', balance: 45230.18, number: '****7832' },
    { id: 'credit', name: 'Credit Card', balance: -2341.50, number: '****9104' }
  ];

  const transactions = [
    { id: 1, date: '2024-01-15', description: 'Amazon Purchase', amount: -127.45, status: 'completed', category: 'Shopping' },
    { id: 2, date: '2024-01-14', description: 'Salary Deposit', amount: 5500.00, status: 'completed', category: 'Income' },
    { id: 3, date: '2024-01-13', description: 'Electric Bill', amount: -89.32, status: 'completed', category: 'Utilities' },
    { id: 4, date: '2024-01-12', description: 'Restaurant', amount: -65.80, status: 'completed', category: 'Dining' },
    { id: 5, date: '2024-01-11', description: 'Gas Station', amount: -52.10, status: 'pending', category: 'Transportation' },
    { id: 6, date: '2024-01-10', description: 'Transfer to Savings', amount: -1000.00, status: 'completed', category: 'Transfer' }
  ];

  const recentOrders = [
    { id: 'ORD-001', date: '2024-01-15', merchant: 'Amazon', amount: 127.45, status: 'delivered' },
    { id: 'ORD-002', date: '2024-01-10', merchant: 'Best Buy', amount: 349.99, status: 'shipped' },
    { id: 'ORD-003', date: '2024-01-08', merchant: 'Target', amount: 82.34, status: 'delivered' }
  ];

  const DashboardPage = () => (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Total Balance</div>
          <div className="text-3xl font-bold text-green-400">$55,347.00</div>
          <div className="text-xs text-slate-500 mt-2">+2.5% from last month</div>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Monthly Spending</div>
          <div className="text-3xl font-bold text-blue-400">$3,240.12</div>
          <div className="text-xs text-slate-500 mt-2">-5.2% vs last month</div>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Pending Orders</div>
          <div className="text-3xl font-bold text-yellow-400">2</div>
          <div className="text-xs text-slate-500 mt-2">1 shipped, 1 processing</div>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Credit Available</div>
          <div className="text-3xl font-bold text-purple-400">$7,658.50</div>
          <div className="text-xs text-slate-500 mt-2">of $10,000 limit</div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-semibold mb-4">Accounts</h2>
          {accounts.map(account => (
            <div key={account.id} className="flex justify-between items-center mb-3 p-3 bg-slate-700 rounded hover:bg-slate-650 cursor-pointer">
              <div>
                <div className="font-medium">{account.name}</div>
                <div className="text-sm text-slate-400">{account.number}</div>
              </div>
              <div className={`font-bold ${account.balance >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${Math.abs(account.balance).toFixed(2)}
              </div>
            </div>
          ))}
        </div>

        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <h2 className="text-xl font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 gap-3">
            <button className="bg-blue-600 hover:bg-blue-700 p-4 rounded-lg font-medium">
              Transfer Money
            </button>
            <button className="bg-green-600 hover:bg-green-700 p-4 rounded-lg font-medium">
              Pay Bills
            </button>
            <button className="bg-purple-600 hover:bg-purple-700 p-4 rounded-lg font-medium">
              Deposit Check
            </button>
            <button className="bg-orange-600 hover:bg-orange-700 p-4 rounded-lg font-medium">
              Send Money
            </button>
          </div>
          
          <div className="mt-6 p-4 bg-slate-700 rounded-lg">
            <h3 className="font-semibold mb-2">Recent Activity</h3>
            <div className="text-sm text-slate-300 space-y-2">
              <div className="flex justify-between">
                <span>Last login</span>
                <span className="text-slate-400">Today, 9:23 AM</span>
              </div>
              <div className="flex justify-between">
                <span>Last payment</span>
                <span className="text-slate-400">Jan 14, 2024</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
        <h2 className="text-xl font-semibold mb-4">Recent Transactions</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="pb-3">Date</th>
                <th className="pb-3">Description</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.slice(0, 5).map(tx => (
                <tr key={tx.id} className="border-b border-slate-700 hover:bg-slate-750">
                  <td className="py-3 text-slate-300">{tx.date}</td>
                  <td className="py-3">{tx.description}</td>
                  <td className="py-3 text-slate-400">{tx.category}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs ${tx.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                      {tx.status}
                    </span>
                  </td>
                  <td className={`py-3 text-right font-medium ${tx.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {tx.amount >= 0 ? '+' : ''}{tx.amount.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const OrdersPage = () => (
    <div className="p-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Orders & Transactions</h1>
        <div className="flex gap-3">
          <input 
            type="text" 
            placeholder="Search transactions..." 
            className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg text-white placeholder-slate-500"
          />
          <select className="bg-slate-800 border border-slate-700 px-4 py-2 rounded-lg text-white">
            <option>All Categories</option>
            <option>Shopping</option>
            <option>Dining</option>
            <option>Utilities</option>
            <option>Income</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Total Transactions</div>
          <div className="text-3xl font-bold">{transactions.length}</div>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Total Spent</div>
          <div className="text-3xl font-bold text-red-400">$1,334.67</div>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Total Received</div>
          <div className="text-3xl font-bold text-green-400">$5,500.00</div>
        </div>
        <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
          <div className="text-slate-400 text-sm mb-2">Pending</div>
          <div className="text-3xl font-bold text-yellow-400">1</div>
        </div>
      </div>

      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700 mb-6">
        <h2 className="text-xl font-semibold mb-4">All Transactions</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-700">
                <th className="pb-3">ID</th>
                <th className="pb-3">Date</th>
                <th className="pb-3">Description</th>
                <th className="pb-3">Category</th>
                <th className="pb-3">Status</th>
                <th className="pb-3 text-right">Amount</th>
              </tr>
            </thead>
            <tbody>
              {transactions.map(tx => (
                <tr key={tx.id} className="border-b border-slate-700 hover:bg-slate-750">
                  <td className="py-3 text-slate-400">#{tx.id}</td>
                  <td className="py-3 text-slate-300">{tx.date}</td>
                  <td className="py-3">{tx.description}</td>
                  <td className="py-3 text-slate-400">{tx.category}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs ${tx.status === 'completed' ? 'bg-green-900 text-green-300' : 'bg-yellow-900 text-yellow-300'}`}>
                      {tx.status}
                    </span>
                  </td>
                  <td className={`py-3 text-right font-medium ${tx.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {tx.amount >= 0 ? '+' : ''}{tx.amount.toFixed(2)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-slate-800 p-6 rounded-lg border border-slate-700">
        <h2 className="text-xl font-semibold mb-4">Recent Orders</h2>
        <div className="space-y-3">
          {recentOrders.map(order => (
            <div key={order.id} className="flex justify-between items-center p-4 bg-slate-700 rounded-lg">
              <div>
                <div className="font-medium">{order.id}</div>
                <div className="text-sm text-slate-400">{order.merchant} • {order.date}</div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`px-3 py-1 rounded text-sm ${order.status === 'delivered' ? 'bg-green-900 text-green-300' : 'bg-blue-900 text-blue-300'}`}>
                  {order.status}
                </span>
                <div className="font-bold">${order.amount.toFixed(2)}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <nav className="bg-slate-800 border-b border-slate-700 px-8 py-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center gap-6">
            <h1 className="text-2xl font-bold text-blue-400">SecureBank</h1>
            <button 
              onClick={() => setCurrentPage('dashboard')}
              className={`px-4 py-2 rounded-lg font-medium transition ${currentPage === 'dashboard' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Dashboard
            </button>
            <button 
              onClick={() => setCurrentPage('orders')}
              className={`px-4 py-2 rounded-lg font-medium transition ${currentPage === 'orders' ? 'bg-blue-600' : 'bg-slate-700 hover:bg-slate-600'}`}
            >
              Orders & Transactions
            </button>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="text-sm text-slate-400">Welcome back</div>
              <div className="font-medium">John Doe</div>
            </div>
            <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center font-bold">
              JD
            </div>
          </div>
        </div>
      </nav>
      
      {currentPage === 'dashboard' && <DashboardPage />}
      {currentPage === 'orders' && <OrdersPage />}
    </div>
  );
};

App;

export default App;