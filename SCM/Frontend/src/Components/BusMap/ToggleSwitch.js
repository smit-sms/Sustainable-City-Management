import React from 'react';

const ToggleSwitch = ({ isOn, handleToggle }) => {
  return (
    <div className="flex items-center justify-end">
      <span className="text-sm text-gray-700 mr-2 font-bold">Edit Mode</span>
      <div className="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
        <input
          type="checkbox"
          name="toggle"
          id="edit-mode-toggle"
          checked={isOn}
          onChange={handleToggle}
          className={`${isOn ? 'right-0 border-green-400' : 'border-gray-300'} toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer`}
        />
        <label
          htmlFor="edit-mode-toggle"
          className={`toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 cursor-pointer ${isOn ? 'bg-green-400' : 'bg-gray-300'}`}
        ></label>
      </div>
    </div>
  );
};

export default ToggleSwitch;
