import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Sidebar from './components/Sidebar';
import Profiles from './pages/Profiles'
import Tasks from './pages/Tasks';
import Dashboard from './pages/Dashboard';
import Products from './pages/Products';

function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");

  return (
    <Router>
      <Navbar />
      <div className="d-flex mt-2" style={{ height: "100vh" }}>
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
        <div className="flex-grow-1 d-flex flex-column">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/tasks" element={<Tasks />} />
            <Route path="/products" element={<Products />} />
            <Route path="/profiles" element={<Profiles />}/>
          </Routes>
        </div>
      </div>
      <Footer />
      <ToastContainer />
    </Router>
  );
}

export default App;