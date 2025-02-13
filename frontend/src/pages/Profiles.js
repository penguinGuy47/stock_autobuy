import React, {useState, useEffect} from "react";
import {toast} from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css'
import { saveData, getData } from "../utils/localStorage";
import './Profiles.css';

const Profiles = () => {
    const formKey = "profiles";
    const [profiles, setProfiles] = useState(() => getData(formKey) || []);
    const [showModal, setShowModal] = useState(false);
    const [editingIndex, setEditingIndex] = useState(null); // Track the profile being edited
    const [newProfile, setNewProfile] = useState({
        broker: "",
        username: "",
        password: "",
    });

    useEffect(() => {
        saveData("profiles", profiles); // Ensure profiles are saved correctly
    }, [profiles]);
    

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNewProfile({ ...newProfile, [name]: value });
    };

    const createOrEditProfile = () => {
        if (newProfile.broker && newProfile.username && newProfile.password) {
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
        } else {
            toast.error("Please fill in all the fields");
        }
    };

    const editProfile = (index) => {
        setEditingIndex(index);
        setNewProfile(profiles[index]);
        setShowModal(true);
    };

    const deleteProfile = (index) => {
        const updatedProfiles = profiles.filter((_, i) => i !== index);
        setProfiles(updatedProfiles);
        toast.info("Profile deleted");
    };

    const resetForm = () => {
        setNewProfile({ broker: "", username: "", password: "" });
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
                        {profile.broker}: {profile.username}
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
                                    <div className="mb-3">
                                        <label htmlFor="brokerSelect" className="form-label">Broker</label>
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
                                        </select>
                                    </div>
                                    <div className="mb-3">
                                        <label htmlFor="usernameInput" className="form-label">Username</label>
                                        <input
                                            type="text"
                                            className="form-control"
                                            id="usernameInput"
                                            name="username"
                                            value={newProfile.username}
                                            onChange={handleInputChange}
                                        />
                                    </div>
                                    <div className="mb-3">
                                        <label htmlFor="passwordInput" className="form-label">Password</label>
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
