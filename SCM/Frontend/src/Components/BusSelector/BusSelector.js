import React, { useEffect, useState } from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../../assets/styles/BusSelector.css'
import { BASE_URL } from '../../services/api';

const BusSelector = (props) => {
  const [buses, setBuses] = useState([]);

  const fetchBuses = async () => {
    try {
      const response = await fetch(`${BASE_URL}/city_services/bus-routes/`,{
        headers: {
          // "ngrok-skip-browser-warning": "true"
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Received non-JSON response from server");
      }
      const data = await response.json();

      // Sorting the buses
      const sortedBuses = data.data.sort((a, b) => {
        const nameA = a.bus_name.toUpperCase();
        const nameB = b.bus_name.toUpperCase();
        if (nameA < nameB) {
          return -1;
        }
        if (nameA > nameB) {
          return 1;
        }
        return 0;
      });

      setBuses(sortedBuses);
    } catch (error) {
      toast.error('Some Error occurred. Please refresh and try again.');
      console.log(error);
    }
  };

  useEffect(() => {
    fetchBuses();
  }, []);

  const handleChange = async (event) => {
    const selectedRouteId = event.target.value;
    const selectedBus = buses.find(bus => bus.route_id === selectedRouteId);

    if (selectedBus) {
      await fetchBusDetails(selectedBus.bus_name);
    }
    
  };

  const fetchBusDetails = async (busName) => {
    try {
      const response = await fetch(`${BASE_URL}/city_services/bus-routes/?bus_name=${busName}`, {
        headers: {
          // "ngrok-skip-browser-warning": "true"
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      const data = await response.json();
      props.onBusSelect(busName,data.data); 
    } catch (error) {
      toast.error('Some error occurred while fetching bus details. Please try again.');
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-center mb-2">DUBLIN BUS</h1>
      <hr className="border-t-2 border-gray-200 mb-2" />
      <select onChange={handleChange} defaultValue="" className="bus-selector">
        <option value="" disabled>Select a Bus </option>
        {buses.map(bus => (
          <option key={bus.route_id} value={bus.route_id}>{bus.bus_name}</option>
          ))}
      </select>
      <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored" pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
};

export default BusSelector;
