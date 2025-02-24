import React from 'react';
import { useNavigate } from 'react-router-dom';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const navigate = useNavigate();

  const handleTabClick = (tab) => {
    setActiveTab(tab);
    if (tab === "Dashboard") {
      navigate("/");
    } else if (tab === "Tasks") {
      navigate("/tasks");
    } else if (tab === "Profiles") {
      navigate("/profiles");
    } else if (tab === "Products") {
      navigate("/products");
    }
  };

  return (
    <div className="col-2 bg-dark text-white p-3">
      <ul className="nav flex-column">
        <li
          className={`nav-item ${activeTab === "Dashboard" ? "active" : ""}`}
          onClick={() => handleTabClick("Dashboard")}
          style={{ cursor: "pointer" }}
        >
          Dashboard
        </li>
        <li
          className={`nav-item ${activeTab === "Tasks" ? "active" : ""}`}
          onClick={() => handleTabClick("Tasks")}
          style={{ cursor: "pointer" }}
        >
          Tasks
        </li>
        <li
          className={`nav-item ${activeTab === "Products" ? "active" : ""}`}
          onClick={() => handleTabClick("Products")}
          style={{ cursor: "pointer" }}
        >
          Products
        </li>
        <li
          className={`nav-item ${activeTab === "Profiles" ? "active" : ""}`}
          onClick={() => handleTabClick("Profiles")}
          style={{ cursor: "pointer"}}
        >
          Profiles
        </li>
      </ul>
    </div>
  );
};

export default Sidebar;
