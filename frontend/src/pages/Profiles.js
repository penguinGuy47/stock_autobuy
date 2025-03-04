import React, { useState, useEffect } from "react";
import { toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { saveData, getData } from "../utils/localStorage";
import "./Profiles.css";

const Profiles = () => {
  const formKey = "profiles";
  const [profiles, setProfiles] = useState(() => getData(formKey) || []);
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null); // Track which profile is being edited
  const [newProfile, setNewProfile] = useState({
    type: "", // "broker" or "retail"
    broker: "",   // used when type is broker
    retailer: "", // used when type is retail
    username: "",
    password: "",
  });

  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    saveData(formKey, profiles); // Ensure profiles are saved correctly
  }, [profiles]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setNewProfile({ ...newProfile, [name]: value });
  };

  const handleTypeChange = (e) => {
    const value = e.target.value; // "broker" or "retail"
    setNewProfile({ ...newProfile, type: value, broker: "", retailer: "" });
  };

  const createOrEditProfile = () => {
    // Validate required fields based on profile type
    if (!newProfile.type) {
      toast.error("Please select a profile type.");
      return;
    }
    if (newProfile.type === "broker") {
      if (!newProfile.broker || !newProfile.username || !newProfile.password) {
        toast.error("Please fill in all the fields for a broker profile.");
        return;
      }
    } else if (newProfile.type === "retail") {
      if (!newProfile.retailer || !newProfile.username || !newProfile.password) {
        toast.error("Please fill in all the fields for a retail profile.");
        return;
      }
    }

    if (editingIndex !== null) {
      // Editing an existing profile
      const updatedProfiles = [...profiles];
      updatedProfiles[editingIndex] = newProfile;
      setProfiles(updatedProfiles);
      toast.success("Profile updated successfully!");
    } else {
      // Creating a new profile
      setProfiles([...profiles, newProfile]);
      toast.success("Profile created successfully!");
    }
    resetForm();
    setShowModal(false);
  };

  const editProfile = (index) => {
    setEditingIndex(index);
    setNewProfile(profiles[index]);
    setShowModal(true);
    setShowPassword(false);
  };

  const deleteProfile = (index) => {
    const updatedProfiles = profiles.filter((_, i) => i !== index);
    setProfiles(updatedProfiles);
    toast.info("Profile deleted");
  };

  const resetForm = () => {
    setNewProfile({
      type: "",
      broker: "",
      retailer: "",
      username: "",
      password: "",
    });
    setEditingIndex(null);
  };

  return (
    <div className="container p-3">
      <h3>Profiles</h3>
      <button
        className="btn btn-success mb-3"
        onClick={() => {
          resetForm();
          setShowModal(true);
        }}
      >
        + Create Profile
      </button>
      <ul className="list-group">
        {profiles.map((profile, index) => (
          <li
            className="list-group-item d-flex justify-content-between align-items-center"
            key={index}
          >
            {profile.type === "broker" ? (
              <span>
                Broker ({profile.broker}): {profile.username}
              </span>
            ) : (
              <span>
                Retail ({profile.retailer}): {profile.username}
              </span>
            )}
            <div>
              <button
                className="btn btn-secondary btn-sm me-2"
                onClick={() => editProfile(index)}
              >
                Edit
              </button>
              <button
                className="btn btn-danger btn-sm"
                onClick={() => deleteProfile(index)}
              >
                Delete
              </button>
            </div>
          </li>
        ))}
      </ul>

      {/* Modal for Creating/Editing a Profile */}
      {showModal && (
        <div className="modal show d-block" role="dialog">
          <div className="modal-dialog">
            <div className="modal-content">
              <div className="modal-header">
                <h5 className="modal-title">
                  {editingIndex !== null ? "Edit Profile" : "Create Profile"}
                </h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setShowModal(false)}
                ></button>
              </div>
              <div className="modal-body">
                <form>
                  {/* Profile Type */}
                  <div className="mb-3 form-label">
                    <label className="mb-2">Profile Type</label>
                    <div>
                      <input
                        type="radio"
                        id="brokerType"
                        name="type"
                        value="broker"
                        checked={newProfile.type === "broker"}
                        onChange={handleTypeChange}
                      />
                      <label htmlFor="brokerType" className="ms-2 me-3">
                        Broker
                      </label>
                      <input
                        type="radio"
                        id="retailType"
                        name="type"
                        value="retail"
                        checked={newProfile.type === "retail"}
                        onChange={handleTypeChange}
                      />
                      <label htmlFor="retailType" className="ms-2">
                        Retail
                      </label>
                    </div>
                  </div>

                  {/* Conditional Field: Broker or Retailer */}
                  {newProfile.type === "broker" && (
                    <div className="mb-3">
                      <label htmlFor="brokerSelect" className="form-label">
                        Select Broker
                      </label>
                      <select
                        id="brokerSelect"
                        className="form-select"
                        name="broker"
                        value={newProfile.broker}
                        onChange={handleInputChange}
                      >
                        <option value="">Select Broker</option>
                        <option value="chase">Chase</option>
                        <option value="fidelity">Fidelity</option>
                        <option value="schwab">Schwab</option>
                        <option value="firstrade">Firstrade</option>
                        <option value="wells">Wells Fargo</option>
                        <option value="robinhood">Robinhood</option>
                      </select>
                    </div>
                  )}
                  {newProfile.type === "retail" && (
                    <div className="mb-3">
                      <label htmlFor="retailerSelect" className="form-label">
                        Select Retailer
                      </label>
                      <select
                        id="retailerSelect"
                        className="form-select"
                        name="retailer"
                        value={newProfile.retailer}
                        onChange={handleInputChange}
                      >
                        <option value="">Select Retailer</option>
                        <option value="bestbuy">BestBuy</option>
                        <option value="walmart">Walmart</option>
                        <option value="supreme">Supreme</option>
                      </select>
                    </div>
                  )}

                  {/* Username */}
                  <div className="mb-3">
                    <label htmlFor="usernameInput" className="form-label">
                      Username
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="usernameInput"
                      name="username"
                      value={newProfile.username}
                      onChange={handleInputChange}
                    />
                  </div>

                  {/* Password */}
                  <div className="mb-3">
                    <label htmlFor="passwordInput" className="form-label">
                      Password
                    </label>
                    <input
                      type="password"
                      className="form-control"
                      id="passwordInput"
                      name="password"
                      value={newProfile.password}
                      onChange={handleInputChange}
                    />
                  </div>
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
                  onClick={createOrEditProfile}
                >
                  {editingIndex !== null ? "Save Changes" : "Save Profile"}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profiles;
