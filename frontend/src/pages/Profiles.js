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
    type: "broker", // Only broker type now
    broker: "",
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

  const createOrEditProfile = () => {
    // Validate required fields
    if (!newProfile.broker || !newProfile.username) {
      toast.error("Please fill in all the required fields for a broker profile.");
      return;
    }
    
    // Only check password for brokers other than Fennel
    if (newProfile.broker !== "fennel" && !newProfile.password) {
      toast.error("Please enter a password for this broker.");
      return;
    }

    // If it's Fennel, ensure we have an empty password rather than undefined
    if (newProfile.broker === "fennel") {
      newProfile.password = "";
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
      type: "broker",
      broker: "",
      username: "",
      password: "",
    });
    setEditingIndex(null);
  };

  return (
    <div className="container p-3">
      <h3>Broker Profiles</h3>
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
            <span>
              Broker ({profile.broker}): {profile.username}
            </span>
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
                  {/* Broker Selection */}
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
                      <option value="fennel">Fennel</option>
                      <option value="firstrade">Firstrade</option>
                      <option value="schwab">Schwab</option>
                      <option value="wells">Wells Fargo</option>
                      <option value="robinhood">Robinhood</option>
                    </select>
                  </div>

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

                  {/* Password - hide for Fennel */}
                  {newProfile.broker !== "fennel" && (
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
