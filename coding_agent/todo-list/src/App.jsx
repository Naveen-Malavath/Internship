import { useState } from 'react'
import './App.css'

function App() {
  const [todos, setTodos] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [filter, setFilter] = useState('all')

  const addTodo = () => {
    if (inputValue.trim() !== '') {
      setTodos([...todos, { id: Date.now(), text: inputValue, completed: false }])
      setInputValue('')
    }
  }

  const toggleTodo = (id) => {
    setTodos(todos.map(todo => 
      todo.id === id ? { ...todo, completed: !todo.completed } : todo
    ))
  }

  const deleteTodo = (id) => {
    setTodos(todos.filter(todo => todo.id !== id))
  }

  const clearCompleted = () => {
    setTodos(todos.filter(todo => !todo.completed))
  }

  const filteredTodos = todos.filter(todo => {
    if (filter === 'active') return !todo.completed
    if (filter === 'completed') return todo.completed
    return true
  })

  const activeTodosCount = todos.filter(todo => !todo.completed).length

  return (
    <div className="App">
      <div className="todo-container">
        <h1>📝 Todo List</h1>
        
        <div className="input-section">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && addTodo()}
            placeholder="What needs to be done?"
            className="todo-input"
          />
          <button onClick={addTodo} className="add-button">Add</button>
        </div>

        {todos.length > 0 && (
          <>
            <div className="filter-section">
              <button 
                className={filter === 'all' ? 'active' : ''} 
                onClick={() => setFilter('all')}
              >
                All
              </button>
              <button 
                className={filter === 'active' ? 'active' : ''} 
                onClick={() => setFilter('active')}
              >
                Active
              </button>
              <button 
                className={filter === 'completed' ? 'active' : ''} 
                onClick={() => setFilter('completed')}
              >
                Completed
              </button>
            </div>

            <ul className="todo-list">
              {filteredTodos.map(todo => (
                <li key={todo.id} className={todo.completed ? 'completed' : ''}>
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                    className="checkbox"
                  />
                  <span className="todo-text">{todo.text}</span>
                  <button onClick={() => deleteTodo(todo.id)} className="delete-button">
                    ✕
                  </button>
                </li>
              ))}
            </ul>

            <div className="footer">
              <span className="count">{activeTodosCount} item{activeTodosCount !== 1 ? 's' : ''} left</span>
              {todos.some(todo => todo.completed) && (
                <button onClick={clearCompleted} className="clear-button">
                  Clear completed
                </button>
              )}
            </div>
          </>
        )}
      </div>
    </div>
  )
}

export default App
