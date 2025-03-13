import React, { useState, useEffect } from "react";
import { getData } from "../utils/localStorage";
import { toast } from 'react-toastify';
import api from '../services/api';

const TaskModal = ({ 
  show, 
  handleClose, 
  handleSave, 
  initialData, 
  pendingTwoFAs = [], 
  onTwoFAComplete 
}) => {
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
  const [currentTwoFAIndex, setCurrentTwoFAIndex] = useState(0);
  const [displayAllTwoFAs, setDisplayAllTwoFAs] = useState(false);
  const [twoFaCodes, setTwoFaCodes] = useState({});
  const [filteredProfiles, setFilteredProfiles] = useState([]);

  // Reset codes when modal opens or closes
  useEffect(() => {
    if (show && pendingTwoFAs.length > 0) {
      setTwoFaCode("");
      setCurrentTwoFAIndex(0);
      setTwoFaCodes({});
    }
  }, [show, pendingTwoFAs]);

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

  // Handle 2FA submission for a specific request
  const handle2FASubmit = async (sessionId, method, index = null) => {
    let code;
    
    if (displayAllTwoFAs) {
      // If displaying all, get code from the object using sessionId
      code = twoFaCodes[sessionId] || "";
      if ((method === 'text' || method === 'captcha_and_text' || method === 'email') && !code) {
        toast.error('Please enter the 2FA code.');
        return;
      }
    } else {
      // If displaying one at a time, use the single input field
      code = twoFaCode;
      if ((method === 'text' || method === 'captcha_and_text' || method === 'email') && !code) {
        toast.error('Please enter the 2FA code.');
        return;
      }
    }
    
    try {
      const payload = {
        session_id: sessionId,
        two_fa_code: method === 'app' ? null : code,
      };
      
      const response = await api.post('/complete_2fa', payload);
      
      if (response.data.status === 'success') {
        // Notify parent component of successful 2FA completion
        onTwoFAComplete(sessionId, true);
        
        // Get updated list of pending 2FAs (removing the one we just processed)
        const remainingTwoFAs = pendingTwoFAs.filter(item => item.sessionId !== sessionId);
        
        // If showing one at a time
        if (!displayAllTwoFAs) {
          if (remainingTwoFAs.length > 0) {
            // There are more 2FAs to process, show the next one
            // Reset the index if needed to prevent out-of-bounds
            const nextIndex = Math.min(currentTwoFAIndex, remainingTwoFAs.length - 1);
            setCurrentTwoFAIndex(nextIndex);
            setTwoFaCode(""); // Clear the input field for the next code
          } else {
            // No more 2FAs, close the modal
            handleClose();
          }
        } else {
          // For all-at-once mode
          // Remove this code from the inputs object
          setTwoFaCodes(prev => {
            const updated = {...prev};
            delete updated[sessionId];
            return updated;
          });
          
          // If all 2FAs are now processed, close the modal
          if (remainingTwoFAs.length === 0) {
            handleClose();
          }
        }
      } else {
        onTwoFAComplete(sessionId, false, response.data.message || 'Unknown error.');
      }
    } catch (error) {
      onTwoFAComplete(
        sessionId, 
        false, 
        error.response?.data?.error || 'Unknown error.'
      );
    }
  };
  
  // Handle change for individual 2FA code inputs (when showing all)
  const handleTwoFACodeChange = (sessionId, value) => {
    setTwoFaCodes(prev => ({
      ...prev,
      [sessionId]: value
    }));
  };
  
  // Toggle between showing one at a time or all at once
  const toggleDisplayMode = () => {
    setDisplayAllTwoFAs(!displayAllTwoFAs);
  };
  
  if (!show) return null;
  
  // Determine if we're showing the 2FA section
  const showingTwoFA = pendingTwoFAs && pendingTwoFAs.length > 0;
  
  // Current 2FA request when showing one at a time
  const currentTwoFA = showingTwoFA && !displayAllTwoFAs && pendingTwoFAs.length > 0 
    ? pendingTwoFAs[currentTwoFAIndex] 
    : null;

  return (
    <div className="modal show d-block" role="dialog">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title text-dark">
              {showingTwoFA ? "2FA Verification" : (initialData ? "Edit Task" : "Create Task")}
            </h5>
            <button
              type="button"
              className="btn-close"
              onClick={handleClose}
            ></button>
          </div>
          <div className="modal-body text-dark">
            {!showingTwoFA && (
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

            {/* 2FA Code Input Section */}
            {showingTwoFA && (
              <div>
                {pendingTwoFAs.length > 1 && (
                  <div className="d-flex justify-content-between mb-3">
                    <span>{pendingTwoFAs.length} 2FA requests pending</span>
                    <button 
                      className="btn btn-sm btn-outline-secondary"
                      onClick={toggleDisplayMode}
                    >
                      {displayAllTwoFAs ? "Show One at a Time" : "Show All Requests"}
                    </button>
                  </div>
                )}
                
                {!displayAllTwoFAs ? (
                  /* One at a time display */
                  <div className="mb-3">
                    <div className="alert alert-info mb-3">
                      <strong>Account:</strong> {currentTwoFA.username} ({currentTwoFA.broker})
                      <br />
                      <strong>Request:</strong> {currentTwoFAIndex + 1} of {pendingTwoFAs.length}
                    </div>
                    
                    {currentTwoFA.method === 'app' ? (
                      <>
                        <div className="alert alert-info">
                          Please approve the authentication request in your app for {currentTwoFA.broker} account ({currentTwoFA.username}), then click Continue.
                        </div>
                        <button 
                          className="btn btn-primary" 
                          onClick={() => handle2FASubmit(currentTwoFA.sessionId, currentTwoFA.method)}
                        >
                          Continue
                        </button>
                      </>
                    ) : (
                      <>
                        <label className="form-label text-dark">
                          Enter 2FA Code for {currentTwoFA.broker} ({currentTwoFA.username})
                        </label>
                        <input
                          type="text"
                          className="form-control"
                          value={twoFaCode}
                          onChange={(e) => setTwoFaCode(e.target.value)}
                          placeholder={`Code for ${currentTwoFA.broker}`}
                        />
                        <button 
                          className="btn btn-primary mt-2" 
                          onClick={() => handle2FASubmit(currentTwoFA.sessionId, currentTwoFA.method)}
                        >
                          Submit 2FA
                        </button>
                      </>
                    )}
                  </div>
                ) : (
                  /* All at once display */
                  <div>
                    {pendingTwoFAs.map((twoFA, index) => (
                      <div key={twoFA.sessionId} className="card mb-3">
                        <div className="card-header">
                          {twoFA.broker} - {twoFA.username}
                        </div>
                        <div className="card-body">
                          {twoFA.method === 'app' ? (
                            <>
                              <p>Please approve the authentication request in your app.</p>
                              <button 
                                className="btn btn-primary" 
                                onClick={() => handle2FASubmit(twoFA.sessionId, twoFA.method, index)}
                              >
                                Continue
                              </button>
                            </>
                          ) : (
                            <>
                              <label className="form-label">Enter 2FA Code</label>
                              <input
                                type="text"
                                className="form-control mb-2"
                                value={twoFaCodes[twoFA.sessionId] || ""}
                                onChange={(e) => handleTwoFACodeChange(twoFA.sessionId, e.target.value)}
                                placeholder="Enter code"
                              />
                              <button 
                                className="btn btn-primary" 
                                onClick={() => {
                                  handle2FASubmit(twoFA.sessionId, twoFA.method, index);
                                }}
                              >
                                Submit
                              </button>
                            </>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
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
            {!showingTwoFA && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={(e) => {
                  handleSubmit();
                }}
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
