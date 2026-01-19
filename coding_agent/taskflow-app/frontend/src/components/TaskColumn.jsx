import { useState } from 'react';
import TaskCard from './TaskCard';
import './TaskColumn.css';

const TaskColumn = ({ title, status, tasks, onDrop, onEditTask, onDeleteTask }) => {
  const [isDraggingOver, setIsDraggingOver] = useState(false);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDraggingOver(true);
  };

  const handleDragLeave = () => {
    setIsDraggingOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDraggingOver(false);
    const taskId = e.dataTransfer.getData('taskId');
    onDrop(parseInt(taskId), status);
  };

  const getStatusColor = () => {
    switch (status) {
      case 'todo':
        return '#3b82f6';
      case 'in-progress':
        return '#f59e0b';
      case 'done':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  return (
    <div 
      className={`task-column ${isDraggingOver ? 'dragging-over' : ''}`}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <div className="column-header" style={{ borderColor: getStatusColor() }}>
        <h2>{title}</h2>
        <span className="task-count" style={{ backgroundColor: getStatusColor() }}>
          {tasks.length}
        </span>
      </div>
      <div className="column-content">
        {tasks.map((task) => (
          <TaskCard
            key={task.id}
            task={task}
            onEdit={onEditTask}
            onDelete={onDeleteTask}
          />
        ))}
        {tasks.length === 0 && (
          <div className="empty-state">
            <p>No tasks yet</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskColumn;
