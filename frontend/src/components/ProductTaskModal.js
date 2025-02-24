import React, { useState, useEffect } from "react";
import { getData } from "../utils/localStorage";
import { toast } from "react-toastify";

const ProductTaskModal = ({ show, handleClose, handleSave, initialData, groupSite }) => {
  const defaultTask = {
    name: "",
    billing: "",
    profile: ""
  };

  const [task, setTask] = useState(initialData || defaultTask);
  const [billingProfiles, setBillingProfiles] = useState([]);

  // Assume billing profiles are stored in localStorage under "billingProfiles"
  useEffect(() => {
    setBillingProfiles(getData("billingProfiles") || []);
  }, []);

  const handleChange = (e) => {
    setTask({ ...task, [e.target.name]: e.target.value });
  };

  const onSave = () => {
    if (!task.name || !task.billing || !task.profile) {
      toast.error("Please fill in all required fields.");
      return;
    }
    // Optionally, set the site from the group automatically:
    handleSave({ ...task, site: groupSite });
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
                <input type="text" className="form-control" name="name" value={task.name} onChange={handleChange} />
              </div>
              {/* Billing Information */}
              <div className="mb-3">
                <label className="form-label">Billing Information</label>
                <input type="text" className="form-control" name="billing" value={task.billing} onChange={handleChange} placeholder="Billing info..." />
              </div>
              {/* Profile Selector (for billing profile) */}
              <div className="mb-3">
                <label className="form-label">Select Billing Profile</label>
                <select className="form-select" name="profile" value={task.profile} onChange={handleChange}>
                  <option value="">Select Profile</option>
                  {billingProfiles.map((profile, index) => (
                    <option key={index} value={profile.username}>
                      {profile.username}
                    </option>
                  ))}
                </select>
              </div>
              {/* Site is already provided by the group */}
              <div className="mb-3">
                <label className="form-label">Site</label>
                <input type="text" className="form-control" value={groupSite} readOnly />
              </div>
            </form>
          </div>
          <div className="modal-footer">
            <button type="button" className="btn btn-secondary" onClick={handleClose}>Close</button>
            <button type="button" className="btn btn-primary" onClick={onSave}>Save Task</button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductTaskModal;
