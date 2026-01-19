"""
Production-Ready Code Templates
High-quality, beautiful templates for React applications with proper CSS
"""

from typing import Dict, List, Optional
from pathlib import Path


class ProductionTemplates:
    """
    Production-ready code templates with beautiful, modern styling
    """
    
    @staticmethod
    def get_react_package_json(project_name: str, features: Optional[List[str]] = None) -> str:
        """Generate production-ready package.json"""
        features = features or []
        
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
        }
        
        if "routing" in features:
            dependencies["react-router-dom"] = "^6.20.0"
        
        if "state" in features or "state-management" in features:
            dependencies["zustand"] = "^4.4.0"
        
        if "icons" in features:
            dependencies["lucide-react"] = "^0.294.0"
        
        if "animation" in features:
            dependencies["framer-motion"] = "^10.16.0"
        
        deps_str = ",\n    ".join([f'"{k}": "{v}"' for k, v in dependencies.items()])
        
        return f'''{{
  "name": "{project_name}",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {{
    "dev": "vite --host",
    "build": "vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext js,jsx --report-unused-disable-directives --max-warnings 0"
  }},
  "dependencies": {{
    {deps_str}
  }},
  "devDependencies": {{
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }}
}}'''

    @staticmethod
    def get_vite_config() -> str:
        """Generate Vite config"""
        return '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true,
  },
})'''

    @staticmethod
    def get_index_html(project_name: str) -> str:
        """Generate index.html with font imports"""
        return f'''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <title>{project_name}</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>'''

    @staticmethod
    def get_main_jsx() -> str:
        """Generate main.jsx"""
        return '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''

    @staticmethod
    def get_todo_app_jsx() -> str:
        """Generate production-ready Todo App component"""
        return '''import { useState } from 'react'
import './App.css'

function App() {
  const [todos, setTodos] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [filter, setFilter] = useState('all')

  const addTodo = () => {
    if (inputValue.trim() !== '') {
      setTodos([
        ...todos,
        {
          id: Date.now(),
          text: inputValue.trim(),
          completed: false,
          createdAt: new Date().toISOString(),
        },
      ])
      setInputValue('')
    }
  }

  const toggleTodo = (id) => {
    setTodos(
      todos.map((todo) =>
        todo.id === id ? { ...todo, completed: !todo.completed } : todo
      )
    )
  }

  const deleteTodo = (id) => {
    setTodos(todos.filter((todo) => todo.id !== id))
  }

  const clearCompleted = () => {
    setTodos(todos.filter((todo) => !todo.completed))
  }

  const filteredTodos = todos.filter((todo) => {
    if (filter === 'active') return !todo.completed
    if (filter === 'completed') return todo.completed
    return true
  })

  const activeTodosCount = todos.filter((todo) => !todo.completed).length
  const completedTodosCount = todos.filter((todo) => todo.completed).length

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      addTodo()
    }
  }

  return (
    <div className="app">
      <div className="todo-container">
        <header className="todo-header">
          <h1 className="todo-title">
            <span className="todo-icon">✓</span>
            Todo List
          </h1>
          <p className="todo-subtitle">Stay organized, get things done</p>
        </header>

        <div className="todo-input-section">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="What needs to be done?"
            className="todo-input"
            autoFocus
          />
          <button onClick={addTodo} className="btn btn-primary">
            <span>Add</span>
          </button>
        </div>

        {todos.length > 0 && (
          <>
            <div className="todo-filters">
              <button
                className={`todo-filter-btn ${filter === 'all' ? 'active' : ''}`}
                onClick={() => setFilter('all')}
              >
                All ({todos.length})
              </button>
              <button
                className={`todo-filter-btn ${filter === 'active' ? 'active' : ''}`}
                onClick={() => setFilter('active')}
              >
                Active ({activeTodosCount})
              </button>
              <button
                className={`todo-filter-btn ${filter === 'completed' ? 'active' : ''}`}
                onClick={() => setFilter('completed')}
              >
                Completed ({completedTodosCount})
              </button>
            </div>

            <ul className="todo-list">
              {filteredTodos.map((todo, index) => (
                <li
                  key={todo.id}
                  className={`todo-item ${todo.completed ? 'completed' : ''}`}
                  style={{ animationDelay: `${index * 50}ms` }}
                >
                  <input
                    type="checkbox"
                    checked={todo.completed}
                    onChange={() => toggleTodo(todo.id)}
                    className="todo-checkbox"
                  />
                  <span className="todo-text">{todo.text}</span>
                  <button
                    onClick={() => deleteTodo(todo.id)}
                    className="todo-delete-btn"
                    aria-label="Delete todo"
                  >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M18 6L6 18M6 6l12 12" />
                    </svg>
                  </button>
                </li>
              ))}
            </ul>

            <footer className="todo-footer">
              <span className="todo-count">
                {activeTodosCount} {activeTodosCount === 1 ? 'item' : 'items'} left
              </span>
              {completedTodosCount > 0 && (
                <button onClick={clearCompleted} className="todo-clear-btn">
                  Clear completed ({completedTodosCount})
                </button>
              )}
            </footer>
          </>
        )}

        {todos.length === 0 && (
          <div className="todo-empty">
            <div className="todo-empty-icon">📝</div>
            <p className="todo-empty-text">No todos yet</p>
            <p className="todo-empty-hint">Add your first task above to get started!</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default App'''

    @staticmethod
    def get_todo_app_css() -> str:
        """Generate production-ready Todo App CSS"""
        return '''/* ==============================================
   PRODUCTION-READY TODO APP STYLES
   Beautiful, modern dark theme with animations
   ============================================== */

/* CSS Variables - Design Tokens */
:root {
  /* Colors */
  --color-bg-primary: #0a0a0f;
  --color-bg-secondary: #12121a;
  --color-bg-card: #16161f;
  --color-bg-hover: #1e1e28;
  
  --color-primary: #6366f1;
  --color-primary-hover: #818cf8;
  --color-primary-glow: rgba(99, 102, 241, 0.3);
  
  --color-success: #10b981;
  --color-success-glow: rgba(16, 185, 129, 0.3);
  
  --color-error: #ef4444;
  --color-error-bg: rgba(239, 68, 68, 0.1);
  
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  
  --color-border: #2d2d3a;
  --color-border-hover: #3d3d4a;
  
  /* Typography */
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  
  /* Spacing */
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  
  /* Border Radius */
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.5);
  
  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);
}

/* Reset & Base */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  font-family: var(--font-family);
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.6;
  min-height: 100vh;
}

/* App Container */
.app {
  min-height: 100vh;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: var(--spacing-8);
  background: 
    radial-gradient(ellipse at top, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
    var(--color-bg-primary);
}

/* Todo Container */
.todo-container {
  width: 100%;
  max-width: 560px;
  margin-top: var(--spacing-8);
  animation: slideUp 0.5s ease-out;
}

/* Header */
.todo-header {
  text-align: center;
  margin-bottom: var(--spacing-8);
}

.todo-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--color-text-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-2);
}

.todo-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  border-radius: var(--radius-lg);
  font-size: 1.5rem;
  box-shadow: 0 0 20px var(--color-primary-glow);
}

.todo-subtitle {
  color: var(--color-text-muted);
  font-size: 1rem;
}

/* Input Section */
.todo-input-section {
  display: flex;
  gap: var(--spacing-3);
  margin-bottom: var(--spacing-6);
}

.todo-input {
  flex: 1;
  padding: var(--spacing-4) var(--spacing-5);
  font-family: var(--font-family);
  font-size: 1rem;
  color: var(--color-text-primary);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  outline: none;
  transition: all var(--transition-fast);
}

.todo-input:hover {
  border-color: var(--color-border-hover);
}

.todo-input:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.todo-input::placeholder {
  color: var(--color-text-muted);
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-4) var(--spacing-6);
  font-family: var(--font-family);
  font-size: 0.9375rem;
  font-weight: 600;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  white-space: nowrap;
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  color: white;
  box-shadow: var(--shadow-md), 0 0 20px var(--color-primary-glow);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg), 0 0 30px var(--color-primary-glow);
}

.btn-primary:active {
  transform: translateY(0);
}

/* Filters */
.todo-filters {
  display: flex;
  gap: var(--spacing-2);
  margin-bottom: var(--spacing-6);
  padding: var(--spacing-2);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.todo-filter-btn {
  flex: 1;
  padding: var(--spacing-3) var(--spacing-4);
  font-family: var(--font-family);
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.todo-filter-btn:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-hover);
}

.todo-filter-btn.active {
  color: var(--color-primary);
  background: var(--color-bg-card);
  box-shadow: var(--shadow-sm);
}

/* Todo List */
.todo-list {
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-3);
}

/* Todo Item */
.todo-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-4) var(--spacing-5);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-fast);
  animation: slideUp 0.3s ease-out backwards;
}

.todo-item:hover {
  border-color: var(--color-border-hover);
  box-shadow: var(--shadow-md);
  transform: translateX(4px);
}

.todo-item.completed {
  opacity: 0.6;
}

.todo-item.completed .todo-text {
  text-decoration: line-through;
  color: var(--color-text-muted);
}

/* Checkbox */
.todo-checkbox {
  width: 22px;
  height: 22px;
  appearance: none;
  border: 2px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
  position: relative;
  flex-shrink: 0;
}

.todo-checkbox:hover {
  border-color: var(--color-primary);
}

.todo-checkbox:checked {
  background: linear-gradient(135deg, var(--color-success) 0%, #059669 100%);
  border-color: var(--color-success);
}

.todo-checkbox:checked::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

/* Todo Text */
.todo-text {
  flex: 1;
  font-size: 1rem;
  color: var(--color-text-primary);
  word-break: break-word;
}

/* Delete Button */
.todo-delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: all var(--transition-fast);
  opacity: 0;
  flex-shrink: 0;
}

.todo-item:hover .todo-delete-btn {
  opacity: 1;
}

.todo-delete-btn:hover {
  background: var(--color-error-bg);
  color: var(--color-error);
}

/* Footer */
.todo-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-6);
  padding-top: var(--spacing-4);
  border-top: 1px solid var(--color-border);
}

.todo-count {
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.todo-clear-btn {
  padding: var(--spacing-2) var(--spacing-3);
  font-family: var(--font-family);
  font-size: 0.875rem;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.todo-clear-btn:hover {
  color: var(--color-error);
  background: var(--color-error-bg);
}

/* Empty State */
.todo-empty {
  text-align: center;
  padding: var(--spacing-10);
  color: var(--color-text-muted);
}

.todo-empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-4);
  opacity: 0.5;
}

.todo-empty-text {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-2);
}

.todo-empty-hint {
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

/* Animations */
@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 640px) {
  .app {
    padding: var(--spacing-4);
  }
  
  .todo-container {
    margin-top: var(--spacing-4);
  }
  
  .todo-title {
    font-size: 2rem;
  }
  
  .todo-icon {
    width: 40px;
    height: 40px;
    font-size: 1.25rem;
  }
  
  .todo-input-section {
    flex-direction: column;
  }
  
  .btn-primary {
    width: 100%;
  }
  
  .todo-filter-btn {
    padding: var(--spacing-2) var(--spacing-3);
    font-size: 0.8125rem;
  }
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: var(--radius-full);
}

::-webkit-scrollbar-thumb:hover {
  background: var(--color-border-hover);
}

/* Selection */
::selection {
  background: var(--color-primary);
  color: white;
}'''

    @staticmethod
    def get_index_css() -> str:
        """Generate index.css with resets"""
        return '''/* Global Styles */
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
}

body {
  min-height: 100vh;
}

#root {
  min-height: 100vh;
}'''

    @staticmethod
    def get_readme(project_name: str, description: str = "") -> str:
        """Generate README.md"""
        return f'''# {project_name}

{description if description else "A modern React application built with Vite."}

## Features

- ⚡ Built with Vite for lightning-fast development
- 🎨 Beautiful dark theme with modern design
- 📱 Fully responsive
- ✨ Smooth animations and transitions
- 🔧 Production-ready code

## Getting Started

### Prerequisites

- Node.js 18+ installed
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

### Building for Production

```bash
npm run build
```

## Tech Stack

- React 18
- Vite 5
- CSS3 with Custom Properties
- Modern JavaScript (ES6+)

## License

MIT
'''


class ProductionCodeGenerator:
    """
    Generates production-ready code using templates
    """
    
    def __init__(self, workspace: Path):
        self.workspace = workspace
        self.templates = ProductionTemplates()
    
    def generate_todo_app(self, project_name: str) -> Dict[str, str]:
        """Generate a complete, production-ready Todo application"""
        files = {}
        
        # Package files
        files[f"{project_name}/package.json"] = self.templates.get_react_package_json(
            project_name, features=["icons"]
        )
        files[f"{project_name}/vite.config.js"] = self.templates.get_vite_config()
        files[f"{project_name}/index.html"] = self.templates.get_index_html(project_name)
        
        # Source files
        files[f"{project_name}/src/main.jsx"] = self.templates.get_main_jsx()
        files[f"{project_name}/src/App.jsx"] = self.templates.get_todo_app_jsx()
        files[f"{project_name}/src/App.css"] = self.templates.get_todo_app_css()
        files[f"{project_name}/src/index.css"] = self.templates.get_index_css()
        
        # Documentation
        files[f"{project_name}/README.md"] = self.templates.get_readme(
            project_name,
            "A beautiful, production-ready Todo application with modern dark theme."
        )
        
        return files
    
    def generate_react_app(
        self,
        project_name: str,
        app_type: str = "generic",
        features: Optional[List[str]] = None
    ) -> Dict[str, str]:
        """Generate a production-ready React application"""
        
        if app_type == "todo":
            return self.generate_todo_app(project_name)
        
        # Generic React app
        files = {}
        features = features or []
        
        files[f"{project_name}/package.json"] = self.templates.get_react_package_json(
            project_name, features
        )
        files[f"{project_name}/vite.config.js"] = self.templates.get_vite_config()
        files[f"{project_name}/index.html"] = self.templates.get_index_html(project_name)
        files[f"{project_name}/src/main.jsx"] = self.templates.get_main_jsx()
        files[f"{project_name}/src/index.css"] = self.templates.get_index_css()
        files[f"{project_name}/README.md"] = self.templates.get_readme(project_name)
        
        # Generate App.jsx and App.css based on app type
        files[f"{project_name}/src/App.jsx"] = self._generate_generic_app_jsx(project_name)
        files[f"{project_name}/src/App.css"] = self._generate_generic_app_css()
        
        return files
    
    def _generate_generic_app_jsx(self, project_name: str) -> str:
        """Generate a generic App.jsx"""
        return f'''import {{ useState }} from 'react'
import './App.css'

function App() {{
  const [count, setCount] = useState(0)

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">{project_name}</span>
          </div>
        </header>
        
        <main className="main">
          <div className="hero">
            <h1 className="hero-title">
              Welcome to <span className="highlight">{project_name}</span>
            </h1>
            <p className="hero-description">
              A modern React application built with Vite. Fast, beautiful, and ready for production.
            </p>
            
            <div className="counter-card">
              <p className="counter-label">Click counter</p>
              <div className="counter-value">{{count}}</div>
              <button 
                className="btn btn-primary"
                onClick={{() => setCount(count + 1)}}
              >
                Increment
              </button>
            </div>
          </div>
          
          <div className="features">
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3 className="feature-title">Lightning Fast</h3>
              <p className="feature-description">
                Built with Vite for instant hot module replacement and blazing fast builds.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🎨</div>
              <h3 className="feature-title">Modern Design</h3>
              <p className="feature-description">
                Beautiful dark theme with smooth animations and responsive layout.
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">🚀</div>
              <h3 className="feature-title">Production Ready</h3>
              <p className="feature-description">
                Optimized for performance with best practices baked in.
              </p>
            </div>
          </div>
        </main>
        
        <footer className="footer">
          <p>Built with ❤️ using React + Vite</p>
        </footer>
      </div>
    </div>
  )
}}

export default App'''

    def _generate_generic_app_css(self) -> str:
        """Generate generic App.css with modern styling"""
        return '''/* ==============================================
   MODERN REACT APP STYLES
   ============================================== */

:root {
  --color-bg-primary: #0a0a0f;
  --color-bg-secondary: #12121a;
  --color-bg-card: #16161f;
  --color-bg-hover: #1e1e28;
  
  --color-primary: #6366f1;
  --color-primary-hover: #818cf8;
  --color-primary-glow: rgba(99, 102, 241, 0.3);
  
  --color-text-primary: #f8fafc;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  
  --color-border: #2d2d3a;
  
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  
  --spacing-1: 4px;
  --spacing-2: 8px;
  --spacing-3: 12px;
  --spacing-4: 16px;
  --spacing-5: 20px;
  --spacing-6: 24px;
  --spacing-8: 32px;
  --spacing-10: 40px;
  --spacing-12: 48px;
  
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.4);
  
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-normal: 200ms cubic-bezier(0.4, 0, 0.2, 1);
}

*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
}

body {
  font-family: var(--font-family);
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  line-height: 1.6;
  min-height: 100vh;
}

.app {
  min-height: 100vh;
  background: 
    radial-gradient(ellipse at top, rgba(99, 102, 241, 0.1) 0%, transparent 50%),
    var(--color-bg-primary);
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-6);
}

/* Header */
.header {
  padding: var(--spacing-6) 0;
  border-bottom: 1px solid var(--color-border);
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-3);
}

.logo-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  border-radius: var(--radius-lg);
  font-size: 1.25rem;
}

.logo-text {
  font-size: 1.25rem;
  font-weight: 700;
}

/* Main */
.main {
  padding: var(--spacing-12) 0;
}

/* Hero */
.hero {
  text-align: center;
  margin-bottom: var(--spacing-12);
}

.hero-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: var(--spacing-4);
  line-height: 1.2;
}

.highlight {
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-description {
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  max-width: 600px;
  margin: 0 auto var(--spacing-8);
}

/* Counter Card */
.counter-card {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-4);
  padding: var(--spacing-8);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
}

.counter-label {
  color: var(--color-text-muted);
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.counter-value {
  font-size: 4rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Button */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3) var(--spacing-6);
  font-family: var(--font-family);
  font-size: 0.9375rem;
  font-weight: 600;
  border: none;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary {
  background: linear-gradient(135deg, var(--color-primary) 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 0 20px var(--color-primary-glow);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 0 30px var(--color-primary-glow), var(--shadow-lg);
}

/* Features */
.features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-6);
}

@media (max-width: 768px) {
  .features {
    grid-template-columns: 1fr;
  }
}

.feature-card {
  padding: var(--spacing-6);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  transition: all var(--transition-normal);
}

.feature-card:hover {
  border-color: var(--color-primary);
  transform: translateY(-4px);
  box-shadow: 0 0 20px var(--color-primary-glow);
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: var(--spacing-4);
}

.feature-title {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: var(--spacing-2);
}

.feature-description {
  color: var(--color-text-muted);
  font-size: 0.9375rem;
}

/* Footer */
.footer {
  padding: var(--spacing-6) 0;
  border-top: 1px solid var(--color-border);
  text-align: center;
  color: var(--color-text-muted);
}

/* Responsive */
@media (max-width: 640px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .counter-value {
    font-size: 3rem;
  }
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
}

::-webkit-scrollbar-track {
  background: var(--color-bg-secondary);
}

::-webkit-scrollbar-thumb {
  background: var(--color-border);
  border-radius: 9999px;
}

::selection {
  background: var(--color-primary);
  color: white;
}'''
