import { useState, useEffect, useRef } from 'react'
import './App.css'

function App() {
  const [prompt, setPrompt] = useState('')
  const [events, setEvents] = useState([])
  const [isRunning, setIsRunning] = useState(false)
  const [ws, setWs] = useState(null)
  const eventsEndRef = useRef(null)
  const eventsListRef = useRef(null)
  const [shouldAutoScroll, setShouldAutoScroll] = useState(true)

  const isNearBottom = (element) => {
    if (!element) return true
    const threshold = 100 // pixels from bottom
    const distanceFromBottom = element.scrollHeight - element.scrollTop - element.clientHeight
    return distanceFromBottom < threshold
  }

  const handleScroll = () => {
    if (eventsListRef.current) {
      setShouldAutoScroll(isNearBottom(eventsListRef.current))
    }
  }

  const scrollToBottom = () => {
    eventsEndRef.current?.scrollIntoView({ behavior: "smooth" })
    setShouldAutoScroll(true)
  }

  useEffect(() => {
    // Only auto-scroll if user is near bottom
    if (shouldAutoScroll && eventsListRef.current && isNearBottom(eventsListRef.current)) {
      scrollToBottom()
    }
  }, [events, shouldAutoScroll])

  const startAgent = async () => {
    if (!prompt.trim()) return

    setIsRunning(true)
    setEvents([])
    setShouldAutoScroll(true) // Reset auto-scroll when starting new session

    // Connect WebSocket
    const clientId = 'client-' + Date.now()
    const websocket = new WebSocket(`ws://localhost:8000/ws/${clientId}`)
    
    websocket.onopen = () => {
      console.log('WebSocket connected')
      setWs(websocket)
    }

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data)
      console.log('Event received:', data)
      
      // CRITICAL: Log terminal command results for debugging
      if (data.type === 'tool_result' && data.data?.tool_name === 'terminal') {
        console.log('🔍 TERMINAL RESULT DEBUG:', {
          tool_name: data.data.tool_name,
          success: data.data.success,
          result_keys: data.data.result ? Object.keys(data.data.result) : 'no result',
          result_structure: data.data.result,
          exit_code: data.data.result?.exit_code,
          stdout_length: data.data.result?.stdout?.length || 0,
          stderr_length: data.data.result?.stderr?.length || 0,
          error_length: data.data.result?.error?.length || 0,
        })
      }
      
      setEvents(prev => [...prev, data])
      
      if (data.type === 'session_complete' || data.type === 'error') {
        setIsRunning(false)
      }
    }

    websocket.onerror = (error) => {
      console.error('WebSocket error:', error)
      setIsRunning(false)
    }

    websocket.onclose = () => {
      console.log('WebSocket closed')
      setIsRunning(false)
    }

    // Start agent execution
    try {
      const response = await fetch('http://localhost:8000/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt,
          max_iterations: 150,
          client_id: clientId  // Send the same client_id as WebSocket
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
    } catch (error) {
      console.error('Error starting agent:', error)
      setEvents(prev => [...prev, {
        type: 'error',
        source: 'system',
        target: 'user',
        data: { error: error.message },
        timestamp: new Date().toISOString()
      }])
      setIsRunning(false)
    }
  }

  const getEventIcon = (source, type) => {
    if (type === 'error' || type === 'error_detected') return '⚠️'
    if (type === 'task_complete') return '🎯'
    if (type === 'session_complete') return '✅'
    if (source === 'user') return '👤'
    if (source === 'agent') return '🤖'
    if (source === 'llm') return '🧠'
    if (source === 'tool') return '🔧'
    if (source === 'self_healing') return '🔄'
    if (source === 'system') return '⚙️'
    return '💬'
  }

  const getEventColor = (source, type) => {
    if (type === 'error' || type === 'error_detected') return 'red'
    if (type === 'task_complete' || type === 'session_complete') return 'green'
    if (source === 'user') return 'blue'
    if (source === 'agent') return 'purple'
    if (source === 'llm') return 'orange'
    if (source === 'tool') return 'teal'
    if (source === 'self_healing') return 'yellow'
    return 'gray'
  }

  const formatData = (data, type) => {
    if (type === 'llm_request') {
      return {
        'Messages': data.messages?.length || 0,
        'Tools Available': data.tools_available
      }
    }
    if (type === 'llm_response') {
      return {
        'Content': data.content || '(no text response)',
        'Tool Calls': data.tool_calls
      }
    }
    if (type === 'tool_call') {
      // For terminal commands, show command prominently
      if (data.tool_name === 'terminal') {
        return {
          '🔧 Tool': data.tool_name,
          '▶️ Command': data.parameters?.command || '(no command)',
          '📁 Working Directory': data.parameters?.cwd || '(default)',
          '⏱️ Timeout': data.parameters?.timeout ? `${data.parameters.timeout}s` : '60s (default)',
          '🔄 Background': data.parameters?.background ? 'Yes' : 'No'
        }
      }
      return {
        'Tool': data.tool_name,
        'Parameters': data.parameters
      }
    }
    if (type === 'tool_result') {
      // For terminal commands, show full output
      if (data.tool_name === 'terminal' && data.result) {
        const result = data.result
        return {
          '🔧 Tool': data.tool_name,
          '✅ Success': result.success ? '✓ YES' : '✗ NO',
          '▶️ Command': result.command || '(unknown)',
          '📍 Exit Code': result.exit_code ?? '(unknown)',
          '📁 Working Directory': result.cwd || '(default)',
          '📤 STDOUT': result.stdout ? result.stdout.trim() || '(empty)' : '(not captured)',
          '📥 STDERR': result.stderr ? result.stderr.trim() || '(empty)' : '(not captured)',
          '❌ Error': result.error ? result.error : (result.success ? '(none - command succeeded)' : '(no error message)')
        }
      }
      return {
        'Tool': data.tool_name,
        'Success': data.success ? '✓' : '✗',
        'Result': data.result
      }
    }
    if (type === 'parallel_batch_start') {
      return {
        'Total Tools': data.total_tools,
        'Batches': data.batches,
        'Batch Sizes': data.batch_sizes?.join(', ')
      }
    }
    return data
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🤖 AI Coding Agent - Conversation View</h1>
      </header>

      <div className="input-section">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Enter your prompt... (e.g., 'Create a Python file called hello.py that prints Hello World')"
          disabled={isRunning}
          rows="3"
        />
        <button 
          onClick={startAgent} 
          disabled={isRunning || !prompt.trim()}
          className="run-button"
        >
          {isRunning ? '⏳ Running...' : '▶ Run Agent'}
        </button>
      </div>

      <div className="events-container">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <h2>💬 Live Conversation Stream</h2>
          {!shouldAutoScroll && (
            <button 
              onClick={scrollToBottom}
              className="scroll-to-bottom-btn"
              title="Scroll to bottom"
            >
              ⬇️ Scroll to Bottom
            </button>
          )}
        </div>
        <div 
          className="events-list"
          ref={eventsListRef}
          onScroll={handleScroll}
        >
          {events.length === 0 && !isRunning && (
            <div className="empty-state">
              No events yet. Enter a prompt and click "Run Agent" to start.
            </div>
          )}
          
          {events.map((event, index) => (
            <div key={index} className={`event event-${getEventColor(event.source, event.type)}`}>
              <div className="event-header">
                <span className="event-icon">{getEventIcon(event.source, event.type)}</span>
                <span className="event-flow">
                  <strong>{event.source}</strong> → <strong>{event.target}</strong>
                </span>
                <span className="event-type">{event.type}</span>
                <span className="event-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="event-body">
                {event.type === 'tool_call' && event.data?.tool_name === 'terminal' ? (
                  <div className="terminal-command">
                    <div className="terminal-command-header">
                      <span>▶️</span>
                      <code className="command-text">{event.data.parameters?.command || '(no command)'}</code>
                      <span style={{color: '#666', fontSize: '0.8rem'}}>
                        {event.data.parameters?.cwd ? `📁 ${event.data.parameters.cwd}` : ''}
                      </span>
                    </div>
                  </div>
                ) : event.type === 'terminal_output_stream' ? (
                  // Real-time streaming output
                  <div className="terminal-command">
                    <div className="terminal-command-header">
                      <span>⏳</span>
                      <code className="command-text">{event.data?.command || '(unknown command)'}</code>
                      <span style={{color: '#888', fontSize: '0.75rem', fontStyle: 'italic'}}>
                        Streaming...
                      </span>
                    </div>
                    <div className="terminal-output">
                      {event.data?.stdout && (
                        <div className="terminal-output-section stdout">
                          <div className="terminal-output-label">📤 STDOUT (live)</div>
                          <div className="terminal-output-content" style={{fontFamily: 'monospace', whiteSpace: 'pre-wrap'}}>
                            {event.data.stdout}
                          </div>
                        </div>
                      )}
                      {event.data?.stderr && (
                        <div className="terminal-output-section stderr">
                          <div className="terminal-output-label">📥 STDERR (live)</div>
                          <div className="terminal-output-content" style={{fontFamily: 'monospace', whiteSpace: 'pre-wrap'}}>
                            {event.data.stderr}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : event.type === 'tool_result' && event.data?.tool_name === 'terminal' && event.data?.result ? (
                  <div className="terminal-command">
                    <div className="terminal-command-header">
                      <span>{event.data.result.success ? '✅' : '❌'}</span>
                      <code className="command-text">{event.data.result.command || '(unknown command)'}</code>
                      <span style={{
                        color: event.data.result.success ? '#22c55e' : '#ef4444',
                        fontSize: '0.85rem',
                        fontWeight: 600
                      }}>
                        Exit Code: {event.data.result.exit_code ?? '?'}
                      </span>
                    </div>
                    <div className="terminal-output">
                      {/* Always show STDOUT section, even if empty */}
                      <div className="terminal-output-section stdout">
                        <div className="terminal-output-label">📤 STDOUT</div>
                        <div className="terminal-output-content">
                          {event.data.result.stdout && event.data.result.stdout.trim() 
                            ? event.data.result.stdout.trim() 
                            : '(empty - no output)'}
                        </div>
                      </div>
                      {/* Always show STDERR section, even if empty */}
                      <div className="terminal-output-section stderr">
                        <div className="terminal-output-label">📥 STDERR</div>
                        <div className="terminal-output-content">
                          {event.data.result.stderr && event.data.result.stderr.trim() 
                            ? event.data.result.stderr.trim() 
                            : '(empty - no errors)'}
                        </div>
                      </div>
                      {/* Always show ERROR section for failed commands */}
                      {!event.data.result.success && (
                        <div className="terminal-output-section error">
                          <div className="terminal-output-label">❌ ERROR MESSAGE</div>
                          <div className="terminal-output-content">
                            {event.data.result.error && event.data.result.error.trim() 
                              ? event.data.result.error.trim() 
                              : `Command failed with exit code ${event.data.result.exit_code ?? '?'} but no error message was captured. This may indicate the command was not found or there was a system error.`}
                          </div>
                        </div>
                      )}
                      {event.data.result.success && !event.data.result.stdout?.trim() && !event.data.result.stderr?.trim() && (
                        <div className="terminal-output-section success">
                          <div className="terminal-output-label">✅ SUCCESS</div>
                          <div className="terminal-output-content">Command executed successfully (no output)</div>
                        </div>
                      )}
                      {/* Debug info - show all result fields - ALWAYS VISIBLE */}
                      <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: '#1a1a1a', borderRadius: '4px', fontSize: '0.75rem', color: '#888', border: '1px solid #333' }}>
                        <strong style={{color: '#fff'}}>🔍 Debug: Result Structure</strong>
                        <div style={{marginTop: '0.25rem'}}>
                          Success: {String(event.data.result?.success ?? 'undefined')} | 
                          Exit Code: {String(event.data.result?.exit_code ?? 'undefined')} | 
                          Has STDOUT: {String(!!event.data.result?.stdout)} ({String(event.data.result?.stdout?.length || 0)} chars) | 
                          Has STDERR: {String(!!event.data.result?.stderr)} ({String(event.data.result?.stderr?.length || 0)} chars) | 
                          Has ERROR: {String(!!event.data.result?.error)} ({String(event.data.result?.error?.length || 0)} chars)
                        </div>
                        <details style={{marginTop: '0.5rem'}}>
                          <summary style={{cursor: 'pointer', color: '#4a9eff'}}>View Full Result JSON</summary>
                          <pre style={{background: '#000', padding: '0.5rem', borderRadius: '4px', overflow: 'auto', marginTop: '0.25rem', fontSize: '0.7rem'}}>
                            {JSON.stringify({
                              success: event.data.result?.success,
                              exit_code: event.data.result?.exit_code,
                              has_stdout: !!event.data.result?.stdout,
                              has_stderr: !!event.data.result?.stderr,
                              has_error: !!event.data.result?.error,
                              stdout_len: event.data.result?.stdout?.length || 0,
                              stderr_len: event.data.result?.stderr?.length || 0,
                              error_len: event.data.result?.error?.length || 0,
                              stdout_preview: event.data.result?.stdout?.substring(0, 100),
                              stderr_preview: event.data.result?.stderr?.substring(0, 100),
                              error_preview: event.data.result?.error?.substring(0, 100),
                              all_result_keys: event.data.result ? Object.keys(event.data.result) : [],
                              full_result: event.data.result
                            }, null, 2)}
                          </pre>
                        </details>
                      </div>
                    </div>
                  </div>
                ) : (
                  <pre>{JSON.stringify(formatData(event.data, event.type), null, 2)}</pre>
                )}
              </div>
              {event.metadata && Object.keys(event.metadata).length > 0 && (
                <div className="event-metadata">
                  <small>Iteration: {event.metadata.iteration}</small>
                </div>
              )}
            </div>
          ))}
          <div ref={eventsEndRef} />
        </div>
      </div>
    </div>
  )
}

export default App

