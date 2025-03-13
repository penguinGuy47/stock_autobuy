import React from 'react';
import TransactionHistory from '../components/TransactionHistory';
import ReverseSplits from '../components/ReverseSplits';

const Dashboard = () => {
  return (
    <div className="container-fluid mt-4" style={{ paddingBottom: '60px' }}>
      <h1 className="text-center mb-4">Dashboard</h1>
      <div className="row">
        <div className="col-md-6">
          <TransactionHistory />
        </div>
        <div className="col-md-6">
          <ReverseSplits />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
