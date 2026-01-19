import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import NoteCard from '../components/NoteCard';
import NoteModal from '../components/NoteModal';
import './Dashboard.css';

function Dashboard() {
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingNote, setEditingNote] = useState(null);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userEmail = localStorage.getItem('userEmail');
    
    if (!token) {
      navigate('/login');
      return;
    }

    setUser(userEmail);
    fetchNotes();
  }, [navigate]);

  const fetchNotes = async () => {
    const token = localStorage.getItem('token');
    
    try {
      const response = await fetch('http://localhost:8002/api/notes', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.status === 401) {
        localStorage.removeItem('token');
        localStorage.removeItem('userEmail');
        navigate('/login');
        return;
      }

      const data = await response.json();
      setNotes(data);
    } catch (err) {
      console.error('Failed to fetch notes:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail');
    navigate('/login');
  };

  const handleCreateNote = () => {
    setEditingNote(null);
    setShowModal(true);
  };

  const handleEditNote = (note) => {
    setEditingNote(note);
    setShowModal(true);
  };

  const handleDeleteNote = async (noteId) => {
    if (!window.confirm('Are you sure you want to delete this note?')) {
      return;
    }

    const token = localStorage.getItem('token');

    try {
      const response = await fetch(`http://localhost:8002/api/notes/${noteId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setNotes(notes.filter(note => note.id !== noteId));
      }
    } catch (err) {
      console.error('Failed to delete note:', err);
    }
  };

  const handleSaveNote = async (noteData) => {
    const token = localStorage.getItem('token');

    try {
      if (editingNote) {
        // Update existing note
        const response = await fetch(`http://localhost:8002/api/notes/${editingNote.id}`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(noteData),
        });

        if (response.ok) {
          const updatedNote = await response.json();
          setNotes(notes.map(note => note.id === editingNote.id ? updatedNote : note));
        }
      } else {
        // Create new note
        const response = await fetch('http://localhost:8002/api/notes', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(noteData),
        });

        if (response.ok) {
          const newNote = await response.json();
          setNotes([newNote, ...notes]);
        }
      }

      setShowModal(false);
      setEditingNote(null);
    } catch (err) {
      console.error('Failed to save note:', err);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <div className="header-left">
            <h1>📝 NoteVault</h1>
            <span className="user-email">{user}</span>
          </div>
          <div className="header-right">
            <button className="create-button" onClick={handleCreateNote}>
              + New Note
            </button>
            <button className="logout-button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="dashboard-main">
        <div className="notes-container">
          {notes.length === 0 ? (
            <div className="empty-state">
              <div className="empty-icon">📔</div>
              <h2>No notes yet</h2>
              <p>Create your first note to get started</p>
              <button className="create-button" onClick={handleCreateNote}>
                Create Note
              </button>
            </div>
          ) : (
            <div className="notes-grid">
              {notes.map(note => (
                <NoteCard
                  key={note.id}
                  note={note}
                  onEdit={handleEditNote}
                  onDelete={handleDeleteNote}
                />
              ))}
            </div>
          )}
        </div>
      </main>

      {showModal && (
        <NoteModal
          note={editingNote}
          onSave={handleSaveNote}
          onClose={() => {
            setShowModal(false);
            setEditingNote(null);
          }}
        />
      )}
    </div>
  );
}

export default Dashboard;
