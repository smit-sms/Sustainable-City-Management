
// import React, { useEffect, useState } from 'react';
// import './BusSelector.css';

// const BusSelector = (props) => { // Include props here if you need to use them
//   const [buses, setBuses] = useState([]);
//   const [selectedBusDetails, setSelectedBusDetails] = useState(null); // Define state for selected bus details
//   const [error, setError] = useState(""); // Added an error state

//   const fetchBuses = async () => {
//     try {
//       const response = await fetch('https://1941-134-226-214-245.ngrok-free.app/city_services/bus-routes/',{
//         headers: {
//           "ngrok-skip-browser-warning": "true"
//         }
//       });
//       if (!response.ok) {
//         throw new Error(`Network response was not ok: ${response.status}`);
//       }
//       const contentType = response.headers.get("content-type");
//       if (!contentType || !contentType.includes("application/json")) {
//         throw new Error("Received non-JSON response from server");
//       }
//       const data = await response.json();
//       setBuses(data.data);
//     } catch (error) {
//       console.error('Error fetching buses:', error);
//       setError("Failed to load buses.");
//     }
//   };

//   useEffect(() => {
//     fetchBuses();
//   }, []);

//   const handleChange = async (event) => {
//     const selectedRouteId = event.target.value;
//     const selectedBus = buses.find(bus => bus.route_id === selectedRouteId);
//     console.log(selectedBus);
//     if (selectedBus) {
//       await fetchBusDetails(selectedBus.bus_name); // Fetch details for the selected bus
//     }
    
//   };

//   const fetchBusDetails = async (busName) => {
//     try {
//       const response = await fetch(`https://1941-134-226-214-245.ngrok-free.app/city_services/bus-routes/?bus_name=${busName}`, { // Ensure template literals are used correctly
//         headers: {
//           "ngrok-skip-browser-warning": "true"
//         }
//       });
//       if (!response.ok) {
//         throw new Error(`Network response was not ok: ${response.status}`);
//       }
//       const data = await response.json();
//       console.log(data.data)
//       setSelectedBusDetails(data.data); // Now this line will work because we've defined the state above
//       props.onBusSelect(busName,data.data); 
//     } catch (error) {
//       console.error('Error fetching bus details:', error);
//       setError("Failed to load bus details.");
//     }
//   };
//   console.log(selectedBusDetails)
//   if (error) {
//     return <div>Error: {error}</div>;
//   }

//   return (
//     <select onChange={handleChange} defaultValue="" className="bus-selector">
//       <option value="" disabled>Select a bus</option>
//       {buses.map(bus => (
//         <option key={bus.route_id} value={bus.route_id}>{bus.bus_name}</option>
        
//       ))}
//     </select>
//   );
// };

// export default BusSelector;
import React, { useEffect, useState } from 'react';
import './BusSelector.css';

const BusSelector = (props) => { // Include props here if you need to use them
  const [buses, setBuses] = useState([]);
  const [selectedBusDetails, setSelectedBusDetails] = useState(null); // Define state for selected bus details
  const [error, setError] = useState(""); // Added an error state

  const fetchBuses = async () => {
    try {
      const response = await fetch('https://bb45-134-226-214-245.ngrok-free.app/city_services/bus-routes/',{
        headers: {
          "ngrok-skip-browser-warning": "true"
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
      setBuses(data.data);
    } catch (error) {
      console.error('Error fetching buses:', error);
      setError("Failed to load buses.");
    }
  };

  useEffect(() => {
    fetchBuses();
  }, []);

  const handleChange = async (event) => {
    const selectedRouteId = event.target.value;
    const selectedBus = buses.find(bus => bus.route_id === selectedRouteId);
    console.log(selectedBus);
    if (selectedBus) {
      await fetchBusDetails(selectedBus.bus_name); // Fetch details for the selected bus
    }
    
  };

  const fetchBusDetails = async (busName) => {
    try {
      const response = await fetch(`https://bb45-134-226-214-245.ngrok-free.app/city_services/bus-routes/?bus_name=${busName}`, { // Ensure template literals are used correctly
        headers: {
          "ngrok-skip-browser-warning": "true"
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      const data = await response.json();
      console.log(data.data)
      setSelectedBusDetails(data.data); // Now this line will work because we've defined the state above
      props.onBusSelect(busName,data.data); 
    } catch (error) {
      console.error('Error fetching bus details:', error);
      setError("Failed to load bus details.");
    }
  };
  console.log(selectedBusDetails)
  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <select onChange={handleChange} defaultValue="" className="bus-selector">
      <option value="" disabled>Select a bus</option>
      {buses.map(bus => (
        <option key={bus.route_id} value={bus.route_id}>{bus.bus_name}</option>
        
      ))}
    </select>
  );
};

export default BusSelector;