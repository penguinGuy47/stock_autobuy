import React from 'react';
import TransactionHistory from '../components/TransactionHistory';

const Dashboard = () => {
  return (
    <div className="text-center mt-5">
      <h1>Dashboard</h1>
      <TransactionHistory />
    </div>
  );
};

export default Dashboard;
