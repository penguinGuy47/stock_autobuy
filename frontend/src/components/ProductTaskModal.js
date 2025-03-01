import React, { useState, useEffect } from "react";
import { getData } from "../utils/localStorage";
import { toast } from "react-toastify";

const ProductTaskModal = ({ show, handleClose, handleSave, initialData, groupSite }) => {
  const defaultTask = {
    name: "",
    sku: "",
    profile: ""
  };

  const [task, setTask] = useState(initialData || defaultTask);
  const [billingProfiles, setBillingProfiles] = useState([]);

  useEffect(() => {
    const allProfiles = getData("profiles") || [];
    let siteKeyword = "";
    if (groupSite.includes("bestbuy")) {
      siteKeyword = "bestbuy";
    } else if (groupSite.includes("walmart")) {
      siteKeyword = "walmart";
    } else if (groupSite.includes("supreme")) {
      siteKeyword = "supreme";
    }
    
    const siteSpecificProfiles = allProfiles.filter(
      (p) => p.type === "retail" && p.retailer === siteKeyword
    );
    setBillingProfiles(siteSpecificProfiles);
  }, [groupSite]);  

  const handleChange = (e) => {
    setTask({ ...task, [e.target.name]: e.target.value });
  };

  const handleProfileChange = (e) => {
    const selectedUsername = e.target.value;
    if (selectedUsername) {
      const selectedProfile = billingProfiles.find(p => p.username === selectedUsername);
      // Store the complete profile object
      setTask({ 
        ...task, 
        profile: selectedProfile 
      });
    } else {
      setTask({ 
        ...task, 
        profile: null 
      });
    }
  };
  
  const onSave = () => {
    if (!task.name || !task.sku || !task.profile) {
      toast.error("Please fill in all required fields.");
      return;
    }
    
    // Create a task object with the complete profile object
    const taskToSave = {
      ...task,
      site: groupSite,
      // Pass the complete profile object
      profile: task.profile
    };
    
    handleSave(taskToSave);
  };

  if (!show) return null;

  return (
    <div className="modal show d-block" role="dialog">
      <div className="modal-dialog">
        <div className="modal-content">
          <div className="modal-header">
            <h5 className="modal-title text-dark">
              {initialData ? "Edit Product Task" : "Create Product Task"}
            </h5>
            <button type="button" className="btn-close" onClick={handleClose}></button>
          </div>
          <div className="modal-body text-dark">
            <form>
              {/* Task Name */}
              <div className="mb-3">
                <label className="form-label">Task Name</label>
                <input 
                  type="text" 
                  className="form-control" 
                  name="name" 
                  value={task.name} 
                  onChange={handleChange} 
                />
              </div>
              {/* SKU Input */}
              <div className="mb-3">
                <label className="form-label">SKU</label>
                <input 
                  type="text" 
                  className="form-control" 
                  name="sku" 
                  value={task.sku} 
                  onChange={handleChange} 
                  placeholder="Enter SKU" 
                />
              </div>
              {/* Profile Selector */}
              <div className="mb-3">
                <label className="form-label">Select Billing Profile</label>
                <select
                  className="form-select"
                  name="profile"
                  value={task.profile?.username || ""}
                  onChange={handleProfileChange}
                >
                  <option value="">Select Profile</option>
                  {billingProfiles.map((profile, index) => (
                    <option key={index} value={profile.username}>
                      {profile.username}
                    </option>
                  ))}
                </select>
              </div>
              {/* Display Site (immutable) */}
              <div className="mb-3">
                <label className="form-label">Site</label>
                <p className="form-control-plaintext">{groupSite}</p>
              </div>
            </form>
          </div>
          <div className="modal-footer">
            <button 
              type="button" 
              className="btn btn-secondary" 
              onClick={handleClose}
            >
              Close
            </button>
            <button 
              type="button" 
              className="btn btn-primary" 
              onClick={onSave}
            >
              Save Task
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductTaskModal;
