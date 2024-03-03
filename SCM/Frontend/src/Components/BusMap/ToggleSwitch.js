// ToggleSwitch.jsx

import React from 'react';
import './ToggleSwitch.css'; // This will contain the CSS for the toggle switch

const ToggleSwitch = ({ isOn, handleToggle }) => {
  return (
    <div className="toggle-container">
      <span className="toggle-label-text">Edit Mode</span>
      <div className="toggle-switch">
        <input
          id="edit-mode-toggle"
          type="checkbox"
          className="toggle-checkbox"
          checked={isOn}
          onChange={handleToggle}
        />
        <label className="toggle-label" htmlFor="edit-mode-toggle">
          <span className="toggle-inner" />
          <span className="toggle-switch" />
        </label>
      </div>
    </div>
  );
};

export default ToggleSwitch;
