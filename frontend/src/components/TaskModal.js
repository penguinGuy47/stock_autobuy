import React, { useState, useEffect } from "react";
import { getData } from "../utils/localStorage";

const TaskModal = ({ show, handleClose, handleSave }) => {
    const [taskDetails, setTaskDetails] = useState({
        name: "",
        tickers: [""],
        broker: "",
        profile: "",
        quantity: "",
        action: "",
    });

    useEffect(() => {
        const allProfiles = getData("profiles") || [];
        const brokerProfiles = allProfiles.filter(
            (profile) => profile.broker === taskDetails.broker
        );
        setFilteredProfiles(brokerProfiles);
    }, [taskDetails.broker]);

    const handleBrokerChange = (e) => {
        setTaskDetails({ ...taskDetails, broker: e.target.value, profile: "" });
    };

    const filteredProfiles = profiles.filter(profile => profile.broker === taskForm.broker);
    
    const handleProfileChange = (e) => {
        const selectedProfile = profiles.find(profile => profile.username === e.target.value);
    
        if (selectedProfile) {
            setTaskForm({
                ...taskForm,
                username: selectedProfile.username,
                password: selectedProfile.password,
            });
        }
    };
    
  

    const handleSubmit = () => {
        const selectedProfile = filteredProfiles.find(
            (profile) => profile.username === taskDetails.profile
        );

        if (!selectedProfile) {
            alert("Please select a valid profile.");
            return;
        }

        const payload = {
            ...taskDetails,
            username: selectedProfile.username,
            password: selectedProfile.password,
        };

        console.log("Payload to Backend:", payload); // Debugging log
        handleSave(payload);
    };

    return (
        <div className={`modal ${show ? "d-block" : "d-none"}`} role="dialog">
            <div className="modal-dialog">
                <div className="modal-content">
                    <div className="modal-header">
                        <h5 className="modal-title">Create Task</h5>
                        <button
                            type="button"
                            className="btn-close"
                            onClick={handleClose}
                        ></button>
                    </div>
                    <div className="modal-body">
                        <form>
                            <div className="mb-3">
                                <label className="form-label">Task Name</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    value={taskDetails.name}
                                    onChange={(e) =>
                                        setTaskDetails({ ...taskDetails, name: e.target.value })
                                    }
                                />
                            </div>
                            <div className="mb-3">
                                <label className="form-label">Tickers</label>
                                {taskDetails.tickers.map((ticker, index) => (
                                    <div key={index} className="d-flex align-items-center mb-2">
                                        <input
                                            type="text"
                                            className="form-control me-2"
                                            value={ticker}
                                            onChange={(e) =>
                                                setTaskDetails({
                                                    ...taskDetails,
                                                    tickers: taskDetails.tickers.map((t, i) =>
                                                        i === index ? e.target.value.toUpperCase() : t
                                                    ),
                                                })
                                            }
                                        />
                                        {taskDetails.tickers.length > 1 && (
                                            <button
                                                type="button"
                                                className="btn btn-danger btn-sm"
                                                onClick={() =>
                                                    setTaskDetails({
                                                        ...taskDetails,
                                                        tickers: taskDetails.tickers.filter(
                                                            (_, i) => i !== index
                                                        ),
                                                    })
                                                }
                                            >
                                                &ndash;
                                            </button>
                                        )}
                                        {index === taskDetails.tickers.length - 1 && (
                                            <button
                                                type="button"
                                                className="btn btn-success btn-sm"
                                                onClick={() =>
                                                    setTaskDetails({
                                                        ...taskDetails,
                                                        tickers: [...taskDetails.tickers, ""],
                                                    })
                                                }
                                            >
                                                +
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                            <div className="mb-3">
                                <label className="form-label">Broker</label>
                                <select
                                    className="form-select"
                                    value={taskDetails.broker}
                                    onChange={handleBrokerChange}
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
                                <label className="form-label">Profile</label>
                                <select
                                    className="form-select"
                                    value={taskDetails.profile}
                                    onChange={handleProfileChange}
                                    disabled={!taskDetails.broker}
                                >
                                    <option value="">Select Profile</option>
                                    {filteredProfiles.map((profile, index) => (
                                        <option key={index} value={profile.username}>
                                            {profile.username}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div className="mb-3">
                                <label className="form-label">Quantity</label>
                                <input
                                    type="number"
                                    className="form-control"
                                    value={taskDetails.quantity}
                                    onChange={(e) =>
                                        setTaskDetails({ ...taskDetails, quantity: e.target.value })
                                    }
                                />
                            </div>
                            <div className="mb-3">
                                <label className="form-label">Action</label>
                                <select
                                    className="form-select"
                                    value={taskDetails.action}
                                    onChange={(e) =>
                                        setTaskDetails({ ...taskDetails, action: e.target.value })
                                    }
                                >
                                    <option value="">Select Action</option>
                                    <option value="Buy">Buy</option>
                                    <option value="Sell">Sell</option>
                                </select>
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
                            onClick={handleSubmit}
                        >
                            Save Task
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default TaskModal;
