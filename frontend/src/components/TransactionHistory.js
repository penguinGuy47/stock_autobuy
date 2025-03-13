import React, { useState, useEffect } from 'react';
import { getData } from '../utils/localStorage';

const TransactionHistory = () => {
    const [transactions, setTransactions] = useState([]);
    const [sortConfig, setSortConfig] = useState({ key: 'date', direction: 'descending' });

    useEffect(() => {
        const storedTransactions = getData('transactionHistory') || [];
        setTransactions(storedTransactions);
    }, []);

    const handleSort = (key) => {
        let direction = 'ascending';
        if (sortConfig.key === key && sortConfig.direction === 'ascending') {
            direction = 'descending';
        }
        setSortConfig({ key, direction });
    }

    const renderTransactions = () => {
        if (transactions.length === 0) {
            return <div className="no-transactions">No transactions yet</div>;
        }

        return (
           <table className="table table-dark table-striped">
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Ticker(s)</th>
                    <th>Action</th>
                    <th>Quantity</th>
                    <th>Broker</th>
                    <th>Username</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {transactions.map((tx, index) => (
                    <tr key={index}>
                        <td>{tx.date}</td>
                        <td>{Array.isArray(tx.tickers) ? tx.tickers.join(', ') : tx.tickers}</td>
                        <td>{tx.action}</td>
                        <td>{tx.quantity}</td>
                        <td>{tx.broker}</td>
                        <td>{tx.username || '-'}</td>
                        <td>{tx.status}</td>
                    </tr>
                ))}
            </tbody>
           </table>
        );
    };

    return (
        <div>
            <h3>Transaction History</h3>
            {renderTransactions()}
        </div>
    );
};

export default TransactionHistory;
