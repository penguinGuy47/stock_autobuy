import React, { useState } from 'react';
import TaskModal from './TaskModal';
import TaskRow from './TaskRow';

function TaskManager() {
  const [tasks, setTasks] = useState([]);  // List of tasks
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);

  const handleAddTask = () => {
    setEditingTask(null);  // Create new task
    setShowModal(true);
  };

  const handleEditTask = (task) => {
    setEditingTask(task);  // Edit existing task
    setShowModal(true);
  };

  const handleSaveTask = (task) => {
    if (editingTask) {
      // Update existing task
      setTasks(tasks.map(t => t === editingTask ? task : t));
    } else {
      // Add new task
      setTasks([...tasks, task]);
    }
  };

  const handleDeleteTask = (task) => {
    setTasks(tasks.filter(t => t !== task));
  };

  const handleCloseModal = () => {
    setShowModal(false);
  };

  return (
    <div>
      <div className="task-header">
        <h2>Tasks</h2>
        <button onClick={handleAddTask}>Create Task</button>
      </div>

      <div className="task-list">
        {tasks.map((task, index) => (
          <TaskRow key={index} task={task} onEdit={handleEditTask} onDelete={handleDeleteTask} />
        ))}
      </div>

      <TaskModal
        show={showModal}
        handleClose={handleCloseModal}
        task={editingTask}
        handleSave={handleSaveTask}
      />
    </div>
  );
}

export default TaskManager;
