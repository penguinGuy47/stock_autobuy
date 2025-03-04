// Function to save data
export const saveData = (key, data) => {
  try {
    const serializedData = JSON.stringify(data);
    localStorage.setItem(key, serializedData);
  } catch (error) {
    console.error('Error saving data to localStorage:', error);
  }
};

// Function to get data
export const getData = (key) => {
  try {
    const serializedData = localStorage.getItem(key);
    if (serializedData === null) {
      return null;
    }
    return JSON.parse(serializedData);
  } catch (error) {
    console.error('Error retrieving data from localStorage:', error);
    return null;
  }
};

// Function to remove data
export const removeData = (key) => {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing data from localStorage:', error);
  }
};

// Function to record transaction history
export const recordTransaction = (transaction) => {
  const history = getData('transactionHistory') || [];
  history.unshift(transaction);
  saveData('transactionHistory', history);
};
