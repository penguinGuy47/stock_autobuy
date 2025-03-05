import React, { useState, useEffect } from "react";
import { getData } from "../utils/localStorage";
import { toast } from 'react-toastify';
import api from '../services/api';

const TaskModal = ({ show, handleClose, handleSave, initialData, requireTwoFA, sessionId, method }) => {
  // Define default task details
  const defaultTaskDetails = {
    name: "",
    tickers: [""],
    broker: "",
    profile: "",
    quantity: "",
    action: "",
    username: "",
    password: ""
  };

  const [taskDetails, setTaskDetails] = useState(initialData || defaultTaskDetails);
  const [twoFaCode, setTwoFaCode] = useState("");
  const [filteredProfiles, setFilteredProfiles] = useState([]);

  // When initialData changes, update taskDetails state
  useEffect(() => {
    setTaskDetails(initialData || defaultTaskDetails);
  }, [initialData]);

  // Update filtered profiles when broker changes
  useEffect(() => {
    const allProfiles = getData("profiles") || [];
    const brokerProfiles = allProfiles.filter(
      (profile) => profile.broker === taskDetails.broker
    );
    setFilteredProfiles(brokerProfiles);
  }, [taskDetails.broker]);

  const handleTickerChange = (index, value) => {
    const updatedTickers = [...taskDetails.tickers];
    updatedTickers[index] = value.toUpperCase();
    setTaskDetails({ ...taskDetails, tickers: updatedTickers });
  };

  const addTickerField = () => {
    setTaskDetails({ ...taskDetails, tickers: [...taskDetails.tickers, ""] });
  };

  const removeTickerField = (index) => {
    const updatedTickers = [...taskDetails.tickers];
    updatedTickers.splice(index, 1);
    setTaskDetails({ ...taskDetails, tickers: updatedTickers });
  };

  const handleBrokerChange = (e) => {
    setTaskDetails({ ...taskDetails, broker: e.target.value, profile: "", username: "", password: "" });
  };

  const handleProfileChange = (e) => {
    const selectedUsername = e.target.value;
    const selectedProfile = filteredProfiles.find(profile => profile.username === selectedUsername);
    if (selectedProfile) {
      setTaskDetails({
        ...taskDetails,
        profile: selectedUsername,
        username: selectedProfile.username,
        password: selectedProfile.password
      });
    } else {
      setTaskDetails({ ...taskDetails, profile: "" });
    }
  };

  const handleChange = (e) => {
    setTaskDetails({ ...taskDetails, [e.target.name]: e.target.value });
  };

  // Handle normal save (when not in 2FA mode)
  const handleSubmit = () => {
    // Basic validation for required fields
    if (!taskDetails.name || !taskDetails.broker || !taskDetails.quantity || !taskDetails.action) {
      toast.error("Please fill in all required fields.");
      return;
    }
    // Validate quantity
    if (!/^\d+$/.test(taskDetails.quantity) || parseInt(taskDetails.quantity) <= 0) {
      toast.error('Please enter a valid quantity.');
      return;
    }
    // Validate profile selection if broker is selected
    if (taskDetails.broker && !taskDetails.username) {
      toast.error("Please select a valid profile.");
      return;
    }
    // Call parent's handleSave with task details
    handleSave(taskDetails);
  };

  // Handle 2FA submission
  const handle2FASubmit = async (e) => {
    e.preventDefault();
    if ((method === 'text' || method === 'captcha_and_text' || method === 'email') && !twoFaCode) {
      toast.error('Please enter the 2FA code.');
      return;
    }
    try {
      const payload = {
        session_id: sessionId,
        two_fa_code: method === 'app' ? null : twoFaCode,
      };
      const response = await api.post('/complete_2fa', payload);
      if (response.data.status === 'success') {
        const updatedTask = { ...taskDetails, status: 'Success' };
        toast.success('Trade successful.');
        handleSave(updatedTask);
      } else {
        const updatedTask = { ...taskDetails, status: 'Failed - Response' };
        toast.error(`2FA failed: ${response.data.message || 'Unknown error.'}`);
        handleSave(updatedTask);
      }
    } catch (error) {
      const updatedTask = { ...taskDetails, status: 'Failed - Unknown' };
      console.error('2FA failed:', error.response ? error.response.data : error.message);
      toast.error(`2FA failed: ${error.response?.data?.error || 'Unknown error.'}`);
      handleSave(updatedTask);
    } finally {
      setTwoFaCode("");
    }
  };

  if (!show) return null;

  return (
    <div className="modal show d-block" role="dialog">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title text-dark">
              {requireTwoFA ? "2FA Verification" : (initialData ? "Edit Task" : "Create Task")}
            </h5>
            <button
              type="button"
              className="btn-close"
              onClick={handleClose}
            ></button>
          </div>
          <div className="modal-body text-dark">
            {!requireTwoFA && (
              <form>
                {/* Task Name */}
                <div className="mb-3">
                  <label className="form-label text-dark">Task Name</label>
                  <input
                    type="text"
                    className="form-control"
                    name="name"
                    value={taskDetails.name}
                    onChange={handleChange}
                  />
                </div>

                {/* Ticker Fields */}
                <div className="mb-3">
                  <label className="form-label text-dark">Tickers</label>
                  {taskDetails.tickers.map((ticker, index) => (
                    <div key={index} className="d-flex align-items-center mb-2">
                      <input
                        type="text"
                        className="form-control me-2"
                        value={ticker}
                        onChange={(e) => handleTickerChange(index, e.target.value)}
                      />
                      {taskDetails.tickers.length > 1 && (
                        <button
                          type="button"
                          className="btn btn-danger btn-sm me-2"
                          onClick={() => removeTickerField(index)}
                        >
                          &ndash;
                        </button>
                      )}
                      {index === taskDetails.tickers.length - 1 && (
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
                    name="broker"
                    value={taskDetails.broker}
                    onChange={handleBrokerChange}
                  >
                    <option value="">Select Broker</option>
                    <option value="chase">Chase</option>
                    <option value="fidelity">Fidelity</option>
                    <option value="firstrade">Firstrade</option>
                    <option value="public">Public</option>
                    <option value="schwab">Schwab</option>
                    <option value="wells">Wells Fargo</option>
                    <option value="robinhood">Robinhood</option>
                    <option value="fennel">Fennel</option>
                  </select>
                </div>

                {/* Profile Selection */}
                {taskDetails.broker && (
                  <div className="mb-3">
                    <label className="form-label text-dark">Select Profile</label>
                    <select
                      className="form-select"
                      value={taskDetails.profile}
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
                )}

                {/* Quantity */}
                <div className="mb-3">
                  <label className="form-label text-dark">Quantity</label>
                  <input
                    type="number"
                    className="form-control"
                    name="quantity"
                    value={taskDetails.quantity}
                    onChange={handleChange}
                  />
                </div>

                {/* Action */}
                <div className="mb-3">
                  <label className="form-label text-dark">Action</label>
                  <select
                    className="form-select"
                    name="action"
                    value={taskDetails.action}
                    onChange={handleChange}
                  >
                    <option value="">Select Action</option>
                    <option value="Buy">Buy</option>
                    <option value="Sell">Sell</option>
                  </select>
                </div>
              </form>
            )}

            {/* 2FA Code Input */}
            {requireTwoFA && (
              <div className="mb-3">
                {method === 'app' ? (
                  <>
                    <div className="alert alert-info">
                      Please approve the authentication request in your app, then click Continue.
                    </div>
                    <button className="btn btn-primary" onClick={handle2FASubmit}>
                      Continue
                    </button>
                  </>
                ) : (
                  <>
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
                  </>
                )}
              </div>
            )}
          </div>
          <div className="modal-footer">
            <button
              type="button"
              className="btn btn-secondary"
              onClick={handleClose}
            >
              Close
            </button>
            {!requireTwoFA && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={handleSubmit}
              >
                Save Task
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default TaskModal;
