import { useState } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  const increment = () => setCount(count + 1)
  const decrement = () => setCount(count - 1)

  return (
    <div className="app">
      <div className="counter-container">
        <h1>Counter App</h1>
        <div className="counter-display">
          <span className="count-number">{count}</span>
        </div>
        <div className="button-group">
          <button 
            className="counter-btn decrement-btn" 
            onClick={decrement}
          >
            -
          </button>
          <button 
            className="counter-btn increment-btn" 
            onClick={increment}
          >
            +
          </button>
        </div>
      </div>
    </div>
  )
}

export default App