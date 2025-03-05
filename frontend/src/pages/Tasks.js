import React, { useState, useEffect } from "react";
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import "bootstrap/dist/css/bootstrap.min.css";
import api from '../services/api';
import "./Tasks.css";
import { saveData, getData } from '../utils/localStorage';
import TaskModal from '../components/TaskModal';

const Tasks = () => {
  const formKey = `tasksForm`;

  const [activeTab, setActiveTab] = useState("Tasks");
  const [taskGroups, setTaskGroups] = useState(() => getData(`${formKey}_taskGroups`) || []);
  const [tasks, setTasks] = useState(() => getData(`${formKey}_tasks`) || {});
  const [profiles, setProfiles] = useState(() => getData("profiles") || []);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [editingIndex, setEditingIndex] = useState(null);
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");


  // 2FA related state for modal (for starting task)
  const [requireTwoFA, setRequireTwoFA] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const [method, setMethod] = useState("");

  // Save task groups, tasks, and profiles to localStorage when they change
  useEffect(() => {
    saveData(`${formKey}_taskGroups`, taskGroups);
    saveData(`${formKey}_tasks`, tasks);
    saveData(`${formKey}_profiles`, profiles);
  }, [taskGroups, tasks, profiles]);

  useEffect(() => {
    if (selectedGroup !== null) {
      localStorage.setItem('selectedTaskGroup', selectedGroup);
    }
  }, [selectedGroup]);

  useEffect(() => {
    const savedSelectedGroup = localStorage.getItem('selectedTaskGroup');
    if (savedSelectedGroup) {
      setSelectedGroup(savedSelectedGroup);
    }
  }, []);

  const openGroupModal = () => {
    setNewGroupName("");
    setShowGroupModal(true);
  };
  
  const handleCreateGroup = () => {
    const trimmedName = newGroupName.trim();
    if (!trimmedName) {
      toast.error("Group name cannot be empty.");
      return;
    }
    if (taskGroups.includes(trimmedName)) {
      toast.error("Group already exists.");
      return;
    }
    setTaskGroups([...taskGroups, trimmedName]);
    setTasks({ ...tasks, [trimmedName]: [] });
    toast.success("Task group created.");
    setNewGroupName("");
    setShowGroupModal(false);
  };
  

  const handleStartTask = async (index) => {
    if (!selectedGroup) return;
    const taskToStart = tasks[selectedGroup][index];
  
    // Basic validation
    if (
      !taskToStart.name ||
      !taskToStart.tickers ||
      !taskToStart.broker ||
      !taskToStart.quantity ||
      !taskToStart.action ||
      !taskToStart.username ||
      (taskToStart.broker !== 'fennel' && !taskToStart.password)
    ) {
      toast.error('Please fill in all required fields.');
      return;
    }
  
    const updatedTasks = [...tasks[selectedGroup]];
    updatedTasks[index].status = 'Starting';
    setTasks({ ...tasks, [selectedGroup]: updatedTasks });
  
    try {
      const endpoint = taskToStart.action.toLowerCase() === 'buy' ? '/buy' : '/sell';
      const payload = {
        tickers: taskToStart.tickers,
        broker: taskToStart.broker,
        quantity: parseInt(taskToStart.quantity),
        username: taskToStart.username,
        password: taskToStart.password,
      };
  
      const response = await api.post(endpoint, payload);
  
      if (response.data.status === 'success') {
        const newTransaction = {
          date: new Date().toLocaleString(),
          tickers: taskToStart.tickers,
          action: taskToStart.action,
          quantity: taskToStart.quantity,
          broker: taskToStart.broker,
          status: 'Success',
        };
        recordTransaction(newTransaction);

        updatedTasks[index].status = 'Success';
        toast.success(`${taskToStart.action} successful.`);
        setTasks({ ...tasks, [selectedGroup]: updatedTasks });
      } else if (response.data.status === '2FA_required') {
        updatedTasks[index].status = '2FA';
        setRequireTwoFA(true);
        setSessionId(response.data.session_id);
        setMethod(response.data.method);
        setEditingIndex(index);
        setEditingTask(taskToStart);
        setShowModal(true);
        toast.info('2FA is required.');
      }  else {
        const failedTransaction = {
          date: new Date().toLocaleString(),
          tickers: taskToStart.tickers,
          action: taskToStart.action,
          quantity: taskToStart.quantity,
          broker: taskToStart.broker,
          status: 'Failed',
        };
        recordTransaction(failedTransaction);

        updatedTasks[index].status = 'Failed';
        toast.error(`${taskToStart.action} failed: ${response.data.message || 'Unknown error.'}`);
        setTasks({ ...tasks, [selectedGroup]: updatedTasks });
      }
    } catch (error) {
      updatedTasks[index].status = 'Error';
      toast.error(`Task failed: ${error.response?.data?.error || 'Unknown error.'}`);
      setTasks({ ...tasks, [selectedGroup]: updatedTasks });
    }
  };
  
  const handleTaskDuplicate = (index) => {
    if (!selectedGroup) return;
    const taskToDuplicate = tasks[selectedGroup][index];
    setTasks({
      ...tasks,
      [selectedGroup]: [...tasks[selectedGroup], { ...taskToDuplicate }],
    });
  };

  const handleTaskDelete = (index) => {
    if (!selectedGroup) return;
    const updatedTasks = tasks[selectedGroup].filter((_, i) => i !== index);
    setTasks({ ...tasks, [selectedGroup]: updatedTasks });
  };

  const handleTaskGroupDelete = (index) => {
    const groupToDelete = taskGroups[index];
    if (groupToDelete === selectedGroup) {
      setSelectedGroup(null);
    }
    const updatedTaskGroups = taskGroups.filter((_, i) => i !== index);
    const updatedTasks = { ...tasks };
    delete updatedTasks[groupToDelete];
    setTaskGroups(updatedTaskGroups);
    setTasks(updatedTasks);
  };

  const openTaskModalForEdit = (index) => {
    if (!selectedGroup) return;
    setEditingTask(tasks[selectedGroup][index]);
    setEditingIndex(index);
    setRequireTwoFA(false);
    setShowModal(true);
  };

  const openTaskModalForCreate = () => {
    setEditingTask(null);
    setEditingIndex(null);
    setRequireTwoFA(false);
    setShowModal(true);
  };

  const handleTaskModalSave = (payload) => {
    if (!selectedGroup) return;
    if (editingIndex === null) {
      // Create new task
      const newTask = {...payload, status: 'New'};
      const updatedTasks = tasks[selectedGroup] ? [...tasks[selectedGroup], newTask] : [newTask];
      setTasks({ ...tasks, [selectedGroup]: updatedTasks });
    } else {
      // Update existing task
      const updatedTasks = [...tasks[selectedGroup]];
      updatedTasks[editingIndex] = {...payload, status: 'Edited'};
      setTasks({ ...tasks, [selectedGroup]: updatedTasks });
      updatedTasks[editingIndex].status = 'Edited';
    }
    setShowModal(false);
    setEditingTask(null);
    setEditingIndex(null);
    setRequireTwoFA(false);
    setSessionId(null);
    setMethod("");
  };

  return (
    <div className="container-fluid d-flex" style={{ height: "100vh" }}>
      {/* Middle Column for Task Groups */}
      <div className="col-3 bg-secondary text-white p-3 overflow-auto" style={{ height: "100%" }}>
        {activeTab === "Tasks" ? (
          <>
            <h5>Task Groups</h5>
            <button className="btn btn-success mb-2" onClick={openGroupModal}>
              + Create Group
            </button>
            <ul className="list-group">
              {taskGroups.map((group, index) => (
                <li
                  className={`list-group-item ${selectedGroup === group ? "active" : ""}`}
                  key={index}
                  onClick={() => setSelectedGroup(group)}
                  style={{ cursor: "pointer", display: "flex", justifyContent: "space-between" }}
                >
                  {group}
                  <button
                    className="btn btn-danger btn-sm"
                    onClick={() => handleTaskGroupDelete(index)}
                    style={{ marginLeft: "auto" }}
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          </>
        ) : (
          <div className="text-center mt-5">Select "Tasks" to view content</div>
        )}
      </div>

      {/* Right Column for Task Details */}
      <div className="col-9 bg-dark text-white p-3 overflow-auto" style={{ height: "100%" }}>
        {activeTab === "Tasks" && selectedGroup ? (
          <>
            <h5>Tasks in {selectedGroup}</h5>
            <button className="btn btn-primary mb-3" onClick={openTaskModalForCreate}>
              + Create Task
            </button>

            {/* Status Bar */}
            <div className="row text-start fw-bold mb-3">
              <div className="col-2">Task Name</div>
              <div className="col-1">Type</div>
              <div className="col-2">Tickers</div>
              <div className="col">Broker</div>
              <div className="col-1">Quantity</div>
              <div className="col-2">Status</div>
              <div className="col-2">Actions</div>
            </div>

            {/* Task List */}
            {tasks[selectedGroup] &&
            Array.isArray(tasks[selectedGroup]) &&
            tasks[selectedGroup].length > 0 ? (
              tasks[selectedGroup].map((task, index) => (
                <div
                  className="row align-items-center mb-2 bg-secondary text-white p-2 rounded"
                  key={index}
                >
                  <div className="col-2 text-start">{task.name}</div>
                  <div className="col-1 text-start">{task.action}</div>
                  <div className="col-2 text-start">
                    {Array.isArray(task.tickers) ? task.tickers.join(', ') : task.tickers}
                  </div>
                  <div className="col text-start">{task.broker}</div>
                  <div className="col-1 text-start">{task.quantity}</div>
                  <div className="col-2 text-start">{task.status}</div>
                  <div className="col-2 text-start">
                    <div className="btn-group">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => handleStartTask(index)}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-play-fill"
                          viewBox="0 0 16 16"
                        >
                          <path d="m11.596 8.697-6.363 3.692c-.54.313-1.233-.066-1.233-.697V4.308c0-.63.692-1.01 1.233-.696l6.363 3.692a.802.802 0 0 1 0 1.393" />
                        </svg>
                      </button>
                      <button
                        className="btn btn-secondary btn-sm"
                        onClick={() => openTaskModalForEdit(index)}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-pencil-fill"
                          viewBox="0 0 16 16"
                        >
                          <path d="M12.854.146a.5.5 0 0 0-.707 0L10.5 1.793 14.207 5.5l1.647-1.646a.5.5 0 0 0 0-.708zm.646 6.061L9.793 2.5 3.293 9H3.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.207zm-7.468 7.468A.5.5 0 0 1 6 13.5V13h-.5a.5.5 0 0 1-.5-.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.5-.5V10h-.5a.5.5 0 0 1-.175-.032l-.179.178a.5.5 0 0 0-.11.168l-2 5a.5.5 0 0 0 .65.65l5-2a.5.5 0 0 0 .168-.11z" />
                        </svg>
                      </button>
                      <button
                        className="btn btn-info btn-sm"
                        onClick={() => handleTaskDuplicate(index)}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-clipboard2-fill"
                          viewBox="0 0 16 16"
                        >
                          <path d="M9.5 0a.5.5 0 0 1 .5.5.5.5 0 0 0 .5.5.5.5 0 0 1 .5.5V2a.5.5 0 0 1-.5.5h-5A.5.5 0 0 1 5 2v-.5a.5.5 0 0 1 .5-.5.5.5 0 0 0 .5-.5.5.5 0 0 1 .5-.5z" />
                          <path d="M3.5 1h.585A1.5 1.5 0 0 0 4 1.5V2a1.5 1.5 0 0 0 1.5 1.5h5A1.5 1.5 0 0 0 12 2v-.5q-.001-.264-.085-.5h.585A1.5 1.5 0 0 1 14 2.5v12a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 14.5v-12A1.5 1.5 0 0 1 3.5 1" />
                        </svg>
                      </button>
                      <button
                        className="btn btn-danger btn-sm"
                        onClick={() => handleTaskDelete(index)}
                      >
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="16"
                          height="16"
                          fill="currentColor"
                          className="bi bi-x-square-fill"
                          viewBox="0 0 16 16"
                        >
                          <path d="M2 0a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2zm3.354 4.646L8 7.293l2.646-2.647a.5.5 0 0 1 .708.708L8.707 8l2.647 2.646a.5.5 0 0 1-.708.708L8 8.707l-2.646 2.647a.5.5 0 0 1-.708-.708L7.293 8 4.646 5.354a.5.5 0 1 1 .708-.708" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div>No tasks available</div>
            )}
          </>
        ) : (
          <div className="text-center mt-5">
            {activeTab === "Tasks" ? "Select a task group" : "No content"}
          </div>
        )}
      </div>

      {/* Task Modal */}
      <TaskModal
        show={showModal}
        handleClose={() => {
          setShowModal(false);
          setRequireTwoFA(false);
          setSessionId(null);
          setMethod("");
          setEditingTask(null);
          setEditingIndex(null);
        }}
        handleSave={handleTaskModalSave}
        initialData={editingTask}
        requireTwoFA={requireTwoFA}
        sessionId={sessionId}
        method={method}
      />
      {showGroupModal && (
        <div className="modal show d-block" role="dialog">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title text-dark">Create Task Group</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => {
                    setShowGroupModal(false);
                    setNewGroupName("");
                  }}
                ></button>
              </div>
              <div className="modal-body text-dark">
                <div className="mb-3">
                  <label className="form-label">Group Name</label>
                  <input
                    type="text"
                    className="form-control"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                  />
                </div>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowGroupModal(false);
                    setNewGroupName("");
                  }}
                >
                  Close
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleCreateGroup}
                >
                  Save Group
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export const recordTransaction = (transaction) => {
  // Retrieve existing history or initialize an empty array
  const currentHistory = getData('transactionHistory') || [];
  // Add the new transaction at the beginning (so the newest is first)
  currentHistory.unshift(transaction);
  saveData('transactionHistory', currentHistory);
};

export default Tasks;
