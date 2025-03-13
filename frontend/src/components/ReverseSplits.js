import React, { useState, useEffect, useCallback } from 'react';
import api from '../services/api';
import { saveData, getData } from '../utils/localStorage';

const REVERSE_SPLITS_KEY = 'reverseSplitsData';
const LAST_FETCH_KEY = 'reverseSplitsLastFetch';

const ReverseSplits = () => {
  const [splits, setSplits] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);
  const [connectionStatus, setConnectionStatus] = useState({ status: 'unknown', message: 'Not checked yet' });
  const [cacheEmpty, setCacheEmpty] = useState(false);

  // Fetch data only when needed (new data or missing from localStorage)
  const fetchSplitsFromAPI = async (forceUpdate = false) => {
    try {
      setLoading(true);
      setConnectionStatus({ status: '', message: 'Fetching data from server...' });

      // Get existing symbols from localStorage
      const existingSymbols = forceUpdate ? [] : (getData(REVERSE_SPLITS_KEY) || []).map(item => item.symbol);
      
      console.log('Starting API fetch:', { 
        forceUpdate, 
        existingSymbolsCount: existingSymbols.length,
        existingSymbols: existingSymbols.join(',')
      });

      const endpoint = forceUpdate 
        ? '/api/splits/reverse-splits' 
        : `/api/splits/reverse-splits?existing=${existingSymbols.join(',')}`;
      
      console.log('Requesting endpoint:', endpoint);
      
      const response = await api.get(endpoint);
      
      console.log('API Response received:', { 
        status: response.status,
        statusText: response.statusText,
        dataReceived: !!response.data,
        responseSize: JSON.stringify(response.data).length,
        responseData: response.data
      });

      if (response.data && response.data.success) {
        console.log('Response success, data length:', response.data.data.length);
        
        // Check if the backend cache is empty
        if (response.data.cache_empty === true) {
          console.log('Backend cache is empty - not displaying any data');
          setCacheEmpty(true);
          setSplits([]);  // Clear any existing data
          
          setConnectionStatus({
            status: 'warning',
            message: 'No data available - backend cache is empty'
          });
          
          return; // Exit early
        } else {
          setCacheEmpty(false);
        }
        
        if (response.data.data.length > 0) {
          const newData = response.data.data;
          console.log('New data received:', { count: newData.length, firstItem: newData[0] });
          
          // Filter out any splits that are more than 7 days past their effective date
          const today = new Date();
          const filteredData = newData.filter(item => {
            if (!item.split_date) return true; // Keep items without a split date
            
            const splitDate = new Date(item.split_date);
            const timeDiff = today - splitDate;
            const daysPast = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
            
            return daysPast <= 7; // Keep only if 7 or fewer days have passed
          });
          
          if (filteredData.length === 0 && newData.length > 0) {
            console.log('All splits are more than 7 days past their effective date');
            setCacheEmpty(true);
            setSplits([]);
            
            setConnectionStatus({
              status: 'info',
              message: 'All available splits are more than 7 days past their effective date'
            });
            
            return; // Exit early
          }
          
          // If we're not forcing an update, merge with existing data
          if (!forceUpdate) {
            const existingData = getData(REVERSE_SPLITS_KEY) || [];
            console.log('Merging with existing data:', { existingCount: existingData.length });
            
            // Create a merged dataset, removing duplicates based on symbol
            const mergedData = [...existingData];
            
            filteredData.forEach(newItem => {
              const existingIndex = mergedData.findIndex(item => item.symbol === newItem.symbol);
              if (existingIndex >= 0) {
                console.log('Updating existing item:', newItem.symbol);
                mergedData[existingIndex] = newItem;
              } else {
                console.log('Adding new item:', newItem.symbol);
                mergedData.push(newItem);
              }
            });
            
            // Sort by effective date, most recent first
            mergedData.sort((a, b) => new Date(b.split_date) - new Date(a.split_date));
            
            // Save to localStorage and update state
            console.log('Saving merged data to localStorage:', { count: mergedData.length });
            saveData(REVERSE_SPLITS_KEY, mergedData);
            setSplits(mergedData);
          } else {
            // Just use the new filtered data
            console.log('Force update - saving filtered data directly:', { count: filteredData.length });
            saveData(REVERSE_SPLITS_KEY, filteredData);
            setSplits(filteredData);
          }
          
          // Update last fetch timestamp
          const currentTime = Date.now();
          saveData(LAST_FETCH_KEY, currentTime);
          setLastUpdated(new Date(currentTime).toLocaleString());
          
          // Add a status update
          setConnectionStatus({
            status: 'success',
            message: `Data successfully loaded with ${filteredData.length} items`
          });
        } else {
          // No new data, just use what we have in localStorage if it's not past 7 days
          console.log('No new data received, using cached data');
          
          const cachedData = getData(REVERSE_SPLITS_KEY) || [];
          
          // Filter cached data for 7-day expiry
          const today = new Date();
          const filteredCachedData = cachedData.filter(item => {
            if (!item.split_date) return true;
            
            const splitDate = new Date(item.split_date);
            const timeDiff = today - splitDate;
            const daysPast = Math.floor(timeDiff / (1000 * 60 * 60 * 24));
            
            return daysPast <= 7;
          });
          
          if (filteredCachedData.length === 0 && cachedData.length > 0) {
            console.log('All cached splits are more than 7 days past their effective date');
            setCacheEmpty(true);
            setSplits([]);
            
            setConnectionStatus({
              status: 'info',
              message: 'All available splits are more than 7 days past their effective date'
            });
          } else {
            setSplits(filteredCachedData);
            setLastUpdated(new Date(getData(LAST_FETCH_KEY)).toLocaleString());
          }
        }
      } else {
        console.error('API returned error or invalid format:', response.data);
        setError('Failed to fetch reverse splits data');
        setErrorMessage(response.data?.message || 'Unknown error occurred');
        setConnectionStatus({
          status: 'warning',
          message: `API returned error: ${response.data?.message || 'Unknown error'}`
        });
      }
    } catch (error) {
      console.error('Error fetching reverse splits:', error);
      console.error('Full error details:', { 
        message: error.message,
        stack: error.stack,
        response: error.response ? {
          status: error.response.status,
          statusText: error.response.statusText,
          data: error.response.data
        } : 'No response object'
      });
      setError('Error connecting to server');
      setErrorMessage(`Failed to fetch data: ${error.message}`);
      setConnectionStatus({
        status: 'error',
        message: `Error: ${error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const loadSplitsData = async () => {
      setLoading(true);
      
      try {
        // Get data from localStorage first
        const cachedData = getData(REVERSE_SPLITS_KEY);
        const lastFetch = getData(LAST_FETCH_KEY);
        
        console.log('Initial load - checking localStorage:', { 
          hasCachedData: !!cachedData, 
          cachedItemCount: cachedData ? cachedData.length : 0,
          lastFetch: lastFetch ? new Date(lastFetch).toLocaleString() : 'never'
        });
        
        if (cachedData && cachedData.length > 0) {
          // Use cached data immediately
          setSplits(cachedData);
          setLastUpdated(new Date(lastFetch).toLocaleString());
          
          // Only fetch fresh data if cache is old (e.g., older than 6 hours)
          const sixHoursInMs = 6 * 60 * 60 * 1000;
          if (!lastFetch || (Date.now() - lastFetch) > sixHoursInMs) {
            // Use existing symbols to avoid full re-scrape
            await fetchSplitsFromAPI(false);
          } else {
            console.log('Using cached data - last fetch was recent');
          }
        } else {
          // No cached data, need to fetch everything
          await fetchSplitsFromAPI(true);
        }
      } catch (error) {
        console.error('Error loading reverse splits:', error);
        
        // If we have cached data, continue showing it despite the error
        const cachedData = getData(REVERSE_SPLITS_KEY);
        if (cachedData && cachedData.length > 0) {
          setError('Using cached data - could not refresh from server');
          setSplits(cachedData);
          setLastUpdated(new Date(getData(LAST_FETCH_KEY)).toLocaleString());
        } else {
          setError('Error loading data');
        }
      } finally {
        setLoading(false);
      }
    };

    // Load initial data
    loadSplitsData();
    // No dependencies needed as this should only run once on mount
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Format date function to make dates more readable
  const formatDate = (dateString) => {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  // Calculate days remaining until split date
  const getDaysRemaining = (splitDate) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time part to compare just dates
    const splitDateObj = new Date(splitDate);
    splitDateObj.setHours(0, 0, 0, 0);
    
    const timeDiff = splitDateObj - today;
    const daysRemaining = Math.ceil(timeDiff / (1000 * 60 * 60 * 24));
    
    return daysRemaining;
  };

  // Wrap this in useCallback to use as a dependency in useEffect
  const processApiData = useCallback((data) => {
    return data.map(item => ({
      symbol: item.symbol || "NA",
      ratio: item.ratio || "NA",
      news_release_date: item.news_release_date || "NA",
      split_date: item.split_date || "NA", 
      days_between: item.days_between || "NA",
      current_price: item.current_price || "NA",
      expected_price: item.expected_price || "NA"
    }));
  }, []);

  // For smaller screens, you could add a card-based view
  const MobileView = ({ splits }) => (
    <div className="d-md-none">
      {splits.map((split, index) => (
        <div key={index} className="card mb-3">
          <div className="card-header bg-dark text-white">
            <strong>{split.symbol}</strong> - Ratio 1:{split.ratio}
          </div>
          <div className="card-body">
            <div className="row mb-2">
              <div className="col-6 text-muted">Announced:</div>
              <div className="col-6">{split.news_release_date === "NA" ? "NA" : formatDate(split.news_release_date)}</div>
            </div>
            <div className="row mb-2">
              <div className="col-6 text-muted">Effective:</div>
              <div className="col-6">{split.split_date === "NA" ? "NA" : formatDate(split.split_date)}</div>
            </div>
            <div className="row mb-2">
              <div className="col-6 text-muted">Current Price:</div>
              <div className="col-6">{split.current_price === "NA" ? "NA" : `$${parseFloat(split.current_price).toFixed(2)}`}</div>
            </div>
            <div className="row mb-2">
              <div className="col-6 text-muted">Expected Price:</div>
              <div className="col-6">{split.expected_price === "NA" ? "NA" : `$${parseFloat(split.expected_price).toFixed(2)}`}</div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );

  const downloadCsv = () => {
    const headers = ['Symbol', 'Ratio', 'Announced Date', 'Effective Date', 'Current Price', 'Expected Price', 'Status'];
    
    const csvRows = [
      headers.join(','),
      ...splits.map(split => {
        const daysRemaining = getDaysRemaining(split.split_date);
        const status = daysRemaining > 0 ? 'Upcoming' : 'Completed';
        
        return [
          split.symbol,
          `1:${split.ratio}`,
          split.news_release_date === "NA" ? "NA" : formatDate(split.news_release_date),
          split.split_date === "NA" ? "NA" : formatDate(split.split_date),
          split.current_price === "NA" ? "NA" : `$${parseFloat(split.current_price).toFixed(2)}`,
          split.expected_price === "NA" ? "NA" : `$${parseFloat(split.expected_price).toFixed(2)}`,
          status
        ].join(',');
      })
    ].join('\n');
    
    const blob = new Blob([csvRows], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.setAttribute('hidden', '');
    a.setAttribute('href', url);
    a.setAttribute('download', 'reverse_splits.csv');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Connection status indicator component
  const ConnectionStatus = () => {
    const getStatusColor = () => {
      switch (connectionStatus.status) {
        case 'connected':
        case 'success':
          return 'green';
        case 'testing':
          return 'blue';
        case 'warning':
          return 'orange';
        case 'error':
          return 'red';
        default:
          return 'gray';
      }
    };

    return (
      <div style={{ 
        padding: '10px', 
        margin: '10px 0', 
        borderRadius: '4px',
        backgroundColor: `${getStatusColor()}15`, // 15% opacity
        border: `1px solid ${getStatusColor()}`,
        color: getStatusColor()
      }}>
        <div><strong>Backend Status:</strong> {connectionStatus.status}</div>
        <div>{connectionStatus.message}</div>
      </div>
    );
  };

  if (loading && splits.length === 0) {
    return (
      <div className="d-flex justify-content-center my-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mt-4">
      <div className="card">
        <div className="card-header d-flex justify-content-between align-items-center bg-dark text-white">
          <h2 className="mb-0">Reverse Stock Splits</h2>
          {lastUpdated && <small>Last updated: {lastUpdated}</small>}
        </div>

        {/* Connection status indicator */}
        {connectionStatus.message && (
          <div className={`alert ${
            connectionStatus.status === 'success' ? 'alert-success' : 
            connectionStatus.status === 'error' ? 'alert-danger' : 
            connectionStatus.status === 'warning' ? 'alert-warning' : 'alert-info'
          }`}>
            {connectionStatus.status === 'error' ? 'Backend Status: error' : ''} 
            {connectionStatus.message}
          </div>
        )}

        {error && (
          <div className="alert alert-danger">
            {error}
            {errorMessage && <div className="mt-2 small">{errorMessage}</div>}
          </div>
        )}

        {loading ? (
          <div className="card-body text-center">
            <div className="spinner-border" role="status">
              <span className="visually-hidden">Loading...</span>
            </div>
            <div className="mt-2">Loading data...</div>
          </div>
        ) : cacheEmpty ? (
          <div className="card-body text-center">
            <p>No data available. The backend cache is empty or all splits are more than 7 days past their effective date.</p>
          </div>
        ) : splits.length > 0 ? (
          <>
            {/* Table view for larger screens */}
            <div className="table-responsive d-none d-md-block">
              <table className="table table-striped table-hover">
                <thead className="table-dark">
                  <tr>
                    <th>Symbol</th>
                    <th>Ratio</th>
                    <th>Announced Date</th>
                    <th>Effective Date</th>
                    <th>Current Price</th>
                    <th>Expected Price</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {splits.map((split, index) => (
                    <tr key={index}>
                      <td><strong>{split.symbol}</strong></td>
                      <td>{split.ratio}</td>
                      <td>{split.news_release_date === "NA" ? "NA" : formatDate(split.news_release_date)}</td>
                      <td>{split.split_date === "NA" ? "NA" : formatDate(split.split_date)}</td>
                      <td>{split.current_price === "NA" ? "NA" : `$${parseFloat(split.current_price).toFixed(2)}`}</td>
                      <td>{split.expected_price === "NA" ? "NA" : `$${parseFloat(split.expected_price).toFixed(2)}`}</td>
                      <td>
                        {split.split_date && getDaysRemaining(split.split_date) < 0 ? 
                          <span className="badge bg-success">Completed</span> : 
                          <span className="badge bg-warning text-dark">Pending</span>}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            
            {/* Mobile view for smaller screens */}
            <MobileView splits={splits} />
          </>
        ) : (
          <div className="card-body text-center">
            <p>No reverse splits data available.</p>
          </div>
        )}
        
        {/* Card footer with refresh and download buttons - always visible */}
        <div className="card-footer bg-light d-flex justify-content-between align-items-center">
          <div>
            <button 
              className="btn btn-sm btn-outline-primary me-2" 
              onClick={() => fetchSplitsFromAPI(true)}
              disabled={loading}
            >
              {loading ? 
                <span>
                  <span className="spinner-border spinner-border-sm me-1" role="status"></span>
                  Refreshing...
                </span> : 'Refresh Data'}
            </button>
          </div>
          <div className="d-flex align-items-center">
            {splits.length > 0 && (
              <>
                <span className="text-muted small me-3">
                  {splits.length} reverse splits found
                </span>
                <button 
                  className="btn btn-sm btn-outline-secondary" 
                  onClick={downloadCsv}
                >
                  Download CSV
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ReverseSplits;
