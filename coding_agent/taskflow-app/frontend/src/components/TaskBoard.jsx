import { useState } from 'react';
import TaskColumn from './TaskColumn';
import TaskModal from './TaskModal';
import './TaskBoard.css';

const TaskBoard = ({ tasks, onUpdateTask, onDeleteTask, onCreateTask }) => {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState('all');

  const handleDrop = async (taskId, newStatus) => {
    const task = tasks.find(t => t.id === taskId);
    if (task && task.status !== newStatus) {
      await onUpdateTask(taskId, { ...task, status: newStatus });
    }
  };

  const handleEdit = (task) => {
    setEditingTask(task);
    setIsModalOpen(true);
  };

  const handleModalClose = () => {
    setIsModalOpen(false);
    setEditingTask(null);
  };

  const handleSaveTask = async (taskData) => {
    if (editingTask) {
      await onUpdateTask(editingTask.id, taskData);
    } else {
      await onCreateTask(taskData);
    }
    handleModalClose();
  };

  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         task.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
    return matchesSearch && matchesPriority;
  });

  const todoTasks = filteredTasks.filter(t => t.status === 'todo');
  const inProgressTasks = filteredTasks.filter(t => t.status === 'in-progress');
  const doneTasks = filteredTasks.filter(t => t.status === 'done');

  return (
    <div className="task-board">
      <div className="board-header">
        <div className="header-top">
          <h1 className="board-title">
            <span className="title-icon">📋</span>
            TaskFlow
          </h1>
          <button className="btn-create" onClick={() => setIsModalOpen(true)}>
            <span>+</span> New Task
          </button>
        </div>
        
        <div className="board-controls">
          <div className="search-box">
            <span className="search-icon">🔍</span>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
          
          <div className="filter-box">
            <label>Priority:</label>
            <select value={filterPriority} onChange={(e) => setFilterPriority(e.target.value)}>
              <option value="all">All</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>
        </div>
      </div>

      <div className="board-columns">
        <TaskColumn
          title="To Do"
          status="todo"
          tasks={todoTasks}
          onDrop={handleDrop}
          onEdit={handleEdit}
          onDelete={onDeleteTask}
        />
        <TaskColumn
          title="In Progress"
          status="in-progress"
          tasks={inProgressTasks}
          onDrop={handleDrop}
          onEdit={handleEdit}
          onDelete={onDeleteTask}
        />
        <TaskColumn
          title="Done"
          status="done"
          tasks={doneTasks}
          onDrop={handleDrop}
          onEdit={handleEdit}
          onDelete={onDeleteTask}
        />
      </div>

      {isModalOpen && (
        <TaskModal
          task={editingTask}
          onSave={handleSaveTask}
          onClose={handleModalClose}
        />
      )}
    </div>
  );
};

export default TaskBoard;
