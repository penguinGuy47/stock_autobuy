import React, { useState, useEffect } from "react";
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import "bootstrap/dist/css/bootstrap.min.css";
import api from '../services/api';
import "./Tasks.css";
import { saveData, getData, removeData } from '../utils/localStorage';

const Tasks = () => {
  const formKey = `tasksForm`;

  const [activeTab, setActiveTab] = useState("Tasks");
  const [taskGroups, setTaskGroups] = useState(() => getData(`${formKey}_taskGroups`) || []);
  const [tasks, setTasks] = useState(() => getData(`${formKey}_tasks`) || {});
  const [profiles, setProfiles] = useState(() => getData("profiles") || []);
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);
  const [method, setMethod] = useState(""); 
  const [twoFaCode, setTwoFaCode] = useState(""); 
  const [showTwoFaInput, setShowTwoFaInput] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  const [taskForm, setTaskForm] = useState({
    name: getData(`${formKey}_name`) || "",
    tickers: Array.isArray(getData(`${formKey}_tickers`)) ? getData(`${formKey}_tickers`) : [""], // Ensure tickers is an array
    broker: getData(`${formKey}_broker`) || "",
    quantity: getData(`${formKey}_quantity`) || "",
    action: getData(`${formKey}_action`) || "",
    username: getData(`${formKey}_username`) || "",
    password: getData(`${formKey}_password`) || "",
  });

  // const createProfile = () => {
  //   const broker = prompt("Enter broker:");
  //   const username = prompt("Enter username:");
  //   const password = prompt("Enter password:");
  //   if (broker && username && password) {
  //     const newProfile = { broker, username, password };
  //     setProfiles([...profiles, newProfile]);
  //   }
  // };

  // const deleteProfile = (index) => {
  //   const updatedProfiles = profiles.filter((_, i) => i !== index);
  //   setProfiles(updatedProfiles);
  // };

  // const getProfilesForBroker = (broker) => {
  //   return profiles.filter(profile => profile.broker === broker);
  // };
  
  // Save form data to localStorage when fields change
  useEffect(() => {
    saveData(`${formKey}_taskGroups`, taskGroups);
    saveData(`${formKey}_tasks`, tasks);
    saveData(`${formKey}_name`, taskForm.name);
    saveData(`${formKey}_profiles`, profiles);
    saveData(`${formKey}_tickers`, taskForm.tickers);
    saveData(`${formKey}_broker`, taskForm.broker);
    saveData(`${formKey}_quantity`, taskForm.quantity);
    saveData(`${formKey}_action`, taskForm.action);
    saveData(`${formKey}_username`, taskForm.username);
    saveData(`${formKey}_password`, taskForm.password);
  }, [taskGroups, tasks, taskForm]);

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

  const createTaskGroup = () => {
    const newGroup = prompt("Enter task group name:");
    if (newGroup && !taskGroups.includes(newGroup)) {
      setTaskGroups([...taskGroups, newGroup]);
      setTasks({ ...tasks, [newGroup]: [] });
    }
  };

  const handleStartTask = async (index) => {
    const taskToStart = tasks[selectedGroup][index];
  
    // Basic validation
    if (
      !taskToStart.name ||
      !taskToStart.tickers ||
      !taskToStart.broker ||
      !taskToStart.quantity ||
      !taskToStart.action ||
      !taskToStart.username ||
      !taskToStart.password
    ) {
      toast.error('Please fill in all required fields.');
      return;
    }
  
    // Validation for quantity
    if (!/^\d+$/.test(taskToStart.quantity) || parseInt(taskToStart.quantity) <= 0) {
      toast.error('Please enter a valid quantity.');
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
        updatedTasks[index].status = 'Success';
        toast.success(`${taskToStart.action} successful.`);
      } else if (response.data.status === '2FA_required') {
        updatedTasks[index].status = '2FA';
        setShowTwoFaInput(true); // Show 2FA input
        setSessionId(response.data.session_id); // Store session ID for 2FA
        setMethod(response.data.method); // Store method for 2FA
        toast.info('2FA is required.');
      }  else {
        updatedTasks[index].status = 'Failed';  // Change status on trade failure
        toast.error(`${taskToStart.action} failed: ${response.data.message || 'Unknown error.'}`);
      }
    } catch (error) {
      updatedTasks[index].status = 'Error';  // Handle errors gracefully
      toast.error(`Task failed: ${error.response?.data?.error || 'Unknown error.'}`);
    } finally {
      setTasks({ ...tasks, [selectedGroup]: updatedTasks });
    }
  };
  
  
  const handleTickerChange = (index, value) => {
    const updatedTickers = Array.isArray(taskForm.tickers) ? [...taskForm.tickers] : [""];
    updatedTickers[index] = value.toUpperCase();
    setTaskForm({ ...taskForm, tickers: updatedTickers });
  };

  const addTickerField = () => {
    setTaskForm({ ...taskForm, tickers: [...taskForm.tickers, ""] });
  };

  const removeTickerField = (index) => {
    const updatedTickers = [...taskForm.tickers];
    updatedTickers.splice(index, 1);
    setTaskForm({ ...taskForm, tickers: updatedTickers });
  };

  const handleTaskSubmit = () => {
    if (!taskForm.name || !taskForm.broker || !taskForm.quantity || !taskForm.action) {
        toast.error("Please fill in all required fields.");
        return;
    }

    const selectedProfile = profiles.find(profile => profile.username === taskForm.username);

    if (!selectedProfile) {
        toast.error("Selected profile does not exist.");
        return;
    }

    const payload = {
        ...taskForm,
        username: selectedProfile.username,
        password: selectedProfile.password,
    };

    console.log("Payload:", payload);
    setShowModal(false);
  };

  // const filteredProfiles = profiles.filter(profile => profile.broker === taskForm.broker);
    
  // const handleProfileChange = (e) => {
  //     const selectedProfile = profiles.find(profile => profile.username === e.target.value);
  
  //     if (selectedProfile) {
  //         setTaskForm({
  //             ...taskForm,
  //             username: selectedProfile.username,
  //             password: selectedProfile.password,
  //         });
  //     }
  // };


  const handle2FASubmit = async (e) => {
    e.preventDefault();
  
    if ((method === 'text' || method === 'captcha_and_text') && !twoFaCode) {
      toast.error('Please enter the 2FA code.');
      return;
    }

    const updatedTasks = [...tasks[selectedGroup]];
  
    try {
      const payload = {
        session_id: sessionId,
        two_fa_code: method === 'app' ? null : twoFaCode,
      };
  
      const response = await api.post('/complete_2fa', payload);
  
      if (response.data.status === 'success') {
        updatedTasks[editingIndex] = { ...taskForm, status: 'Success' };
        toast.success('Trade successful.');
        setShowTwoFaInput(false); // Hide the 2FA input
      } else {
        updatedTasks[editingIndex] = { ...taskForm, status: 'Failed - Response' };
        toast.error(`2FA failed: ${response.data.message || 'Unknown error.'}`);
      }
    } catch (error) {
      updatedTasks[editingIndex] = { ...taskForm, status: 'Failed - Unknown' };
      console.error('2FA failed:', error.response ? error.response.data : error.message);
      toast.error(`2FA failed: ${error.response?.data?.error || 'Unknown error.'}`);
    } finally {
      setTwoFaCode(""); // Clear the 2FA code
    }
  };
  
  

  const resetTaskForm = () => {
    setTaskForm({
      name: "",
      tickers: [""],
      broker: "",
      quantity: "",
      action: "",
      username: "",
      password: "",
    });
    setEditingIndex(null);

    // Remove data from localStorage
    removeData(`${formKey}_name`);
    removeData(`${formKey}_tickers`);
    removeData(`${formKey}_broker`);
    removeData(`${formKey}_quantity`);
    removeData(`${formKey}_action`);
    removeData(`${formKey}_username`);
    removeData(`${formKey}_password`);
  };

  const handleTaskEdit = (index) => {
    if (!selectedGroup) return;
    const taskToEdit = tasks[selectedGroup][index];
    setTaskForm({
      ...taskToEdit,
      tickers: Array.isArray(taskToEdit.tickers) ? taskToEdit.tickers : [""], // Ensure tickers is an array
    });
    setEditingIndex(index);
    setShowModal(true);
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

  return (
    <div className="container-fluid d-flex" style={{ height: "100vh" }}>
      {/* Middle Column for Task Groups */}
      <div className="col-3 bg-secondary text-white p-3 overflow-auto" style={{ height: "100%" }}>
        {activeTab === "Tasks" ? (
          <>
            <h5>Task Groups</h5>
            <button className="btn btn-success mb-2" onClick={createTaskGroup}>
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
            <button className="btn btn-primary mb-3" onClick={() => {
              resetTaskForm();
              setShowModal(true)
            }}>
              + Create Task
            </button>

            {/* Status Bar */}
            <div className="row text-start fw-bold mb-3">
              <div className="col-1">Task Name</div>
              <div className="col-1">Type</div>
              <div className="col-3">Tickers</div>
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
                  <div className="col-1 text-start">{task.name}</div>
                  <div className="col-1 text-start">{task.action}</div>
                  <div className="col-3 text-start">
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
                        onClick={() => handleTaskEdit(index)}
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

      {/* Task Form Modal */}
      {showModal && (
        <div className="modal show d-block" role="dialog">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title text-dark">Task Details</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <div className="modal-body text-dark">
                <form>
                  {/* Task Name */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Task Name</label>
                    <input
                      type="text"
                      className="form-control"
                      value={taskForm.name}
                      onChange={(e) => setTaskForm({ ...taskForm, name: e.target.value })}
                    />
                  </div>

                  {/* Ticker Fields */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Tickers</label>
                    {taskForm.tickers.map((ticker, index) => (
                      <div key={index} className="d-flex align-items-center mb-2">
                        <input
                          type="text"
                          className="form-control me-2"
                          value={ticker}
                          onChange={(e) => handleTickerChange(index, e.target.value)}
                        />
                        {taskForm.tickers.length > 1 && (
                          <button
                            type="button"
                            className="btn btn-danger btn-sm me-2"
                            onClick={() => removeTickerField(index)}
                          >
                            &ndash;
                          </button>
                        )}
                        {index === taskForm.tickers.length - 1 && (
                          <button
                            type="button"
                            className="btn btn-success btn-sm"
                            onClick={addTickerField}
                          >
                            +
                          </button>
                        )}
                      </div>
                    ))}
                  </div>

                  {/* Broker */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Broker</label>
                    <select
                      className="form-select"
                      value={taskForm.broker}
                      onChange={(e) => setTaskForm({ ...taskForm, broker: e.target.value })}
                    >
                      <option value="">Select Broker</option>
                      <option value="chase">Chase</option>
                      <option value="fidelity">Fidelity</option>
                      <option value="firstrade">Firstrade</option>
                      <option value="public">Public</option>
                      <option value="schwab">Schwab</option>
                      <option value="wells">Wells Fargo</option>
                    </select>
                  </div>

                  {/* Quantity */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Quantity</label>
                    <input
                      type="number"
                      className="form-control"
                      value={taskForm.quantity}
                      onChange={(e) => setTaskForm({ ...taskForm, quantity: e.target.value })}
                    />
                  </div>

                  {/* Action */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Action</label>
                    <select
                      className="form-select"
                      value={taskForm.action}
                      onChange={(e) => setTaskForm({ ...taskForm, action: e.target.value })}
                    >
                      <option value="">Select Action</option>
                      <option value="Buy">Buy</option>
                      <option value="Sell">Sell</option>
                    </select>
                  </div>

                  {/* Profile Selection
                  {taskForm.broker && (
                    <div className="mb-3">
                      <label className="form-label text-dark">Select Profile</label>
                      <select
                        className="form-select"
                        onChange={handleProfileChange}
                      >
                        <option value="">Select Profile</option>
                        {filteredProfiles.map((profile, index) => (
                          <option key={index} value={profile.username}>
                            {profile.username}
                          </option>
                        ))}
                      </select>
                    </div>
                  )} */}

                  {/* Username */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Username</label>
                    <input
                      type="text"
                      className="form-control"
                      value={taskForm.username}
                      onChange={(e) => setTaskForm({ ...taskForm, username: e.target.value })}
                    />
                  </div>

                  {/* Password */}
                  <div className="mb-3">
                    <label className="form-label text-dark">Password</label>
                    <input
                      type="password"
                      className="form-control"
                      value={taskForm.password}
                      onChange={(e) => setTaskForm({ ...taskForm, password: e.target.value })}
                    />
                  </div>

                  {/* 2FA Code Input (conditionally displayed) */}
                  {showTwoFaInput && (
                    <div className="mb-3">
                      <label className="form-label text-dark">2FA Code</label>
                      <input
                        type="text"
                        className="form-control"
                        value={twoFaCode}
                        onChange={(e) => setTwoFaCode(e.target.value)}
                      />
                      <button className="btn btn-primary mt-2" onClick={handle2FASubmit}>
                        Submit 2FA
                      </button>
                    </div>
                  )}
                </form>
              </div>
              <div className="modal-footer">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowModal(false)}
                >
                  Close
                </button>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleTaskSubmit}
                >
                  Save Task
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Tasks;