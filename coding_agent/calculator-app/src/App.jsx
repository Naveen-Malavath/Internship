import { useState } from 'react'
import './App.css'

function App() {
  const [display, setDisplay] = useState('0')
  const [previousValue, setPreviousValue] = useState(null)
  const [operation, setOperation] = useState(null)
  const [waitingForOperand, setWaitingForOperand] = useState(false)

  const inputDigit = (digit) => {
    if (waitingForOperand) {
      setDisplay(String(digit))
      setWaitingForOperand(false)
    } else {
      setDisplay(display === '0' ? String(digit) : display + digit)
    }
  }

  const inputDecimal = () => {
    if (waitingForOperand) {
      setDisplay('0.')
      setWaitingForOperand(false)
    } else if (display.indexOf('.') === -1) {
      setDisplay(display + '.')
    }
  }

  const clear = () => {
    setDisplay('0')
    setPreviousValue(null)
    setOperation(null)
    setWaitingForOperand(false)
  }

  const performOperation = (nextOperation) => {
    const inputValue = parseFloat(display)

    if (previousValue === null) {
      setPreviousValue(inputValue)
    } else if (operation) {
      const currentValue = previousValue || 0
      const newValue = calculate(currentValue, inputValue, operation)

      setDisplay(String(newValue))
      setPreviousValue(newValue)
    }

    setWaitingForOperand(true)
    setOperation(nextOperation)
  }

  const calculate = (firstValue, secondValue, operation) => {
    switch (operation) {
      case '+':
        return firstValue + secondValue
      case '-':
        return firstValue - secondValue
      case '*':
        return firstValue * secondValue
      case '/':
        return firstValue / secondValue
      case '=':
        return secondValue
      default:
        return secondValue
    }
  }

  const handleEquals = () => {
    const inputValue = parseFloat(display)

    if (previousValue !== null && operation) {
      const newValue = calculate(previousValue, inputValue, operation)
      setDisplay(String(newValue))
      setPreviousValue(null)
      setOperation(null)
      setWaitingForOperand(true)
    }
  }

  const toggleSign = () => {
    const value = parseFloat(display)
    setDisplay(String(value * -1))
  }

  const inputPercent = () => {
    const value = parseFloat(display)
    setDisplay(String(value / 100))
  }

  return (
    <div className="calculator">
      <div className="calculator-display">{display}</div>
      <div className="calculator-keypad">
        <div className="calculator-row">
          <button className="calculator-key key-clear" onClick={clear}>AC</button>
          <button className="calculator-key key-sign" onClick={toggleSign}>±</button>
          <button className="calculator-key key-percent" onClick={inputPercent}>%</button>
          <button className="calculator-key key-operator" onClick={() => performOperation('/')}>÷</button>
        </div>
        <div className="calculator-row">
          <button className="calculator-key" onClick={() => inputDigit(7)}>7</button>
          <button className="calculator-key" onClick={() => inputDigit(8)}>8</button>
          <button className="calculator-key" onClick={() => inputDigit(9)}>9</button>
          <button className="calculator-key key-operator" onClick={() => performOperation('*')}>×</button>
        </div>
        <div className="calculator-row">
          <button className="calculator-key" onClick={() => inputDigit(4)}>4</button>
          <button className="calculator-key" onClick={() => inputDigit(5)}>5</button>
          <button className="calculator-key" onClick={() => inputDigit(6)}>6</button>
          <button className="calculator-key key-operator" onClick={() => performOperation('-')}>−</button>
        </div>
        <div className="calculator-row">
          <button className="calculator-key" onClick={() => inputDigit(1)}>1</button>
          <button className="calculator-key" onClick={() => inputDigit(2)}>2</button>
          <button className="calculator-key" onClick={() => inputDigit(3)}>3</button>
          <button className="calculator-key key-operator" onClick={() => performOperation('+')}>+</button>
        </div>
        <div className="calculator-row">
          <button className="calculator-key key-zero" onClick={() => inputDigit(0)}>0</button>
          <button className="calculator-key" onClick={inputDecimal}>.</button>
          <button className="calculator-key key-equals" onClick={handleEquals}>=</button>
        </div>
      </div>
    </div>
  )
}

export default App
