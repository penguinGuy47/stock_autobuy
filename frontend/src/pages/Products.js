// Products.js
import React, { useState, useEffect } from "react";
import { toast } from 'react-toastify';
import api from '../services/api';
import { saveData, getData, removeData } from '../utils/localStorage';
import ProductTaskModal from '../components/ProductTaskModal';
import "./Tasks.css"; // reuse styling if desired

const Products = () => {
  const formKey = `productsForm`;

  // Instead of a simple string, groups are now objects with groupName and site
  const [productGroups, setProductGroups] = useState(() => getData(`${formKey}_productGroups`) || []);
  const [products, setProducts] = useState(() => getData(`${formKey}_products`) || {});
  const [selectedGroup, setSelectedGroup] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingIndex, setEditingIndex] = useState(null);

  // New state for group creation modal
  const [showGroupModal, setShowGroupModal] = useState(false);
  const [newGroupName, setNewGroupName] = useState("");
  const [newGroupSite, setNewGroupSite] = useState("");

  // Save to localStorage when groups or tasks change
  useEffect(() => {
    saveData(`${formKey}_productGroups`, productGroups);
    saveData(`${formKey}_products`, products);
  }, [productGroups, products]);

  // Opens the modal for creating a new product group
  const openGroupModal = () => {
    setNewGroupName("");
    setNewGroupSite("");
    setShowGroupModal(true);
  };

  // Handles creation of a new product group using inputs from the modal
  const handleCreateGroup = () => {
    const trimmedName = newGroupName.trim();
    const trimmedSite = newGroupSite.trim();
    if (!trimmedName || !trimmedSite) {
      toast.error("Both group name and site are required.");
      return;
    }
    if (productGroups.some(group => group.groupName === trimmedName)) {
      toast.error("Group already exists.");
      return;
    }
    const newGroup = { groupName: trimmedName, site: trimmedSite };
    setProductGroups([...productGroups, newGroup]);
    setProducts({ ...products, [trimmedName]: [] });
    toast.success("Product group created.");
    setShowGroupModal(false);
  };

  const handleStartProductTask = async (index) => {
    const task = products[selectedGroup.groupName][index];
    if (!task.name || !task.billing || !task.profile) {
      toast.error('Please fill in all required fields.');
      return;
    }
    // Set task status to "Starting"
    const updatedTasks = [...products[selectedGroup.groupName]];
    updatedTasks[index].status = 'Starting';
    setProducts({ ...products, [selectedGroup.groupName]: updatedTasks });

    try {
      // Call your new backend endpoint (for example, /automate_product)
      const payload = {
        taskName: task.name,
        billing: task.billing,
        site: selectedGroup.site,
        profile: task.profile,
      };
      const response = await api.post('/automate_product', payload);
      if (response.data.status === 'success') {
        updatedTasks[index].status = 'Success';
        toast.success('Product automation successful.');
      } else {
        updatedTasks[index].status = 'Failed';
        toast.error(`Automation failed: ${response.data.message || 'Unknown error.'}`);
      }
    } catch (error) {
      updatedTasks[index].status = 'Error';
      toast.error(`Task failed: ${error.response?.data?.error || 'Unknown error.'}`);
    } finally {
      setProducts({ ...products, [selectedGroup.groupName]: updatedTasks });
    }
  };

  const handleProductDelete = (index) => {
    if (!selectedGroup) return;
    const updatedTasks = products[selectedGroup.groupName].filter((_, i) => i !== index);
    setProducts({ ...products, [selectedGroup.groupName]: updatedTasks });
  };

  return (
    <div className="container-fluid d-flex" style={{ height: "100vh" }}>
      {/* Left Column: Product Groups */}
      <div className="col-3 bg-secondary text-white p-3 overflow-auto" style={{ height: "100%" }}>
        <h5>Product Groups</h5>
        <button className="btn btn-success mb-2" onClick={openGroupModal}>
          + Create Group
        </button>
        <ul className="list-group">
          {productGroups.map((group, index) => (
            <li
              key={index}
              className={`list-group-item ${selectedGroup && selectedGroup.groupName === group.groupName ? "active" : ""}`}
              style={{ cursor: "pointer", display: "flex", justifyContent: "space-between" }}
              onClick={() => setSelectedGroup(group)}
            >
              {group.groupName} ({group.site})
            </li>
          ))}
        </ul>
      </div>

      {/* Right Column: Product Tasks */}
      <div className="col-9 bg-dark text-white p-3 overflow-auto" style={{ height: "100%" }}>
        {selectedGroup ? (
          <>
            <h5>Tasks in {selectedGroup.groupName}</h5>
            <button className="btn btn-primary mb-3" onClick={() => { setEditingIndex(null); setShowModal(true); }}>
              + Create Product Task
            </button>
            {products[selectedGroup.groupName] && products[selectedGroup.groupName].length > 0 ? (
              products[selectedGroup.groupName].map((task, index) => (
                <div key={index} className="row align-items-center mb-2 bg-secondary text-white p-2 rounded">
                  <div className="col-3">{task.name}</div>
                  <div className="col-3">{task.billing}</div>
                  <div className="col-2">{selectedGroup.site}</div>
                  <div className="col-2">{task.profile}</div>
                  <div className="col-2">{task.status}</div>
                  <div className="col-2">
                    <button className="btn btn-primary btn-sm" onClick={() => handleStartProductTask(index)}>Start</button>
                    <button className="btn btn-danger btn-sm" onClick={() => handleProductDelete(index)}>Delete</button>
                  </div>
                </div>
              ))
            ) : (
              <div>No product tasks available</div>
            )}
          </>
        ) : (
          <div className="text-center mt-5">Select a product group</div>
        )}
      </div>

      {/* Product Task Modal */}
      {showModal && selectedGroup && (
        <ProductTaskModal
          show={showModal}
          handleClose={() => setShowModal(false)}
          handleSave={(task) => {
            if (editingIndex !== null) {
              const updatedTasks = [...products[selectedGroup.groupName]];
              updatedTasks[editingIndex] = { ...task, status: 'Updated' };
              setProducts({ ...products, [selectedGroup.groupName]: updatedTasks });
            } else {
              setProducts({
                ...products,
                [selectedGroup.groupName]: [...(products[selectedGroup.groupName] || []), { ...task, status: 'Created' }],
              });
            }
            setShowModal(false);
          }}
          initialData={editingIndex !== null ? products[selectedGroup.groupName][editingIndex] : null}
          groupSite={selectedGroup.site}
        />
      )}

      {/* Product Group Creation Modal */}
        {showGroupModal && (
        <div className="modal show d-block" role="dialog">
            <div className="modal-dialog">
            <div className="modal-content">
                <div className="modal-header">
                <h5 className="modal-title text-dark">Create Product Group</h5>
                <button
                    type="button"
                    className="btn-close"
                    onClick={() => {
                    setShowGroupModal(false);
                    setNewGroupName("");
                    setNewGroupSite("");
                    }}
                ></button>
                </div>
                <div className="modal-body text-dark">
                <div className="mb-3">
                    <label className="form-label">Group Name</label>
                    <input
                    type="text"
                    className="form-control"
                    value={newGroupName}
                    onChange={(e) => setNewGroupName(e.target.value)}
                    />
                </div>
                <div className="mb-3">
                    <label className="form-label">Site</label>
                    <select
                    className="form-select"
                    value={newGroupSite}
                    onChange={(e) => setNewGroupSite(e.target.value)}
                    >
                    <option value="">Select Site</option>
                    <option value="https://www.bestbuy.com">BestBuy</option>
                    <option value="https://www.walmart.com">Walmart</option>
                    <option value="https://www.supremenewyork.com">Supreme</option>
                    </select>
                </div>
                </div>
                <div className="modal-footer">
                <button
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => {
                    setShowGroupModal(false);
                    setNewGroupName("");
                    setNewGroupSite("");
                    }}
                >
                    Close
                </button>
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={handleCreateGroup}
                >
                    Save Group
                </button>
                </div>
            </div>
            </div>
        </div>
        )}
    </div>
  );
};

export default Products;
