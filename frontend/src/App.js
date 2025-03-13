import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './App.css';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Layout from './components/Layout';
import Profiles from './pages/Profiles'
import Tasks from './pages/Tasks';
import Dashboard from './pages/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");

  return (
    <Router>
      <div className="d-flex flex-column" style={{ minHeight: "100vh" }}>
        <Navbar />
        <div className="d-flex flex-grow-1">
          <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
          <div className="flex-grow-1 d-flex flex-column">
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/tasks" element={<Tasks />} />
                <Route path="/profiles" element={<Profiles />}/>
              </Routes>
            </Layout>
          </div>
        </div>
      </div>
      <ToastContainer />
    </Router>
  );
}

export default App;