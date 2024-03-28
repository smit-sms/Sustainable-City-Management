import React, { useState, useEffect } from 'react';

const BusSelector = ({ onBusSelect }) => {
  const [buses, setBuses] = useState([]);
  const [error, setError] = useState(""); // Error state to handle errors

  // Function to fetch all buses
  const fetchBuses = async () => {
    try {
      const response = await fetch('https://8dae-134-226-214-245.ngrok-free.app/city_services/bus-routes/', {
        headers: {
          "ngrok-skip-browser-warning": "true"
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
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

  // Function to fetch details for the selected bus
  const fetchBusDetails = async (busName) => {
    try {
      const response = await fetch(`https://8dae-134-226-214-245.ngrok-free.app/city_services/bus-routes/?bus_name=${busName}`, {
        headers: {
          "ngrok-skip-browser-warning": "true"
        }
      });
      if (!response.ok) {
        throw new Error(`Network response was not ok: ${response.status}`);
      }
      const data = await response.json();
      onBusSelect(data.data); // Pass the details up
    } catch (error) {
      console.error('Error fetching bus details:', error);
      setError("Failed to load bus details.");
    }
  };

  // Handle bus selection change
  const handleChange = async (event) => {
    const selectedRouteId = event.target.value;
    const selectedBus = buses.find(bus => bus.route_id === selectedRouteId);
    if (selectedBus) {
      await fetchBusDetails(selectedBus.name); // Fetch details for the selected bus
    }
  };

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <div>
      <select onChange={handleChange} defaultValue="" className="bus-selector">
        <option value="" disabled>Select a bus</option>
        {buses.map(bus => (
          <option key={bus.route_id} value={bus.route_id}>{bus.name}</option>
        ))}
      </select>
    </div>
  );
};

export default BusSelector;




// Bus Map Using Geojson-------------------------------------------------
// import React, { useEffect, useRef } from 'react';
// import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMap } from 'react-leaflet';
// import L from 'leaflet';
// import 'leaflet/dist/leaflet.css';
// import axios from 'axios';


// // Fix for default marker icons
// delete L.Icon.Default.prototype._getIconUrl;
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
//   iconUrl: require('leaflet/dist/images/marker-icon.png'),
//   shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
// });

// // Helper component to fit map bounds
// const FitBounds = ({ bounds }) => {
//   const map = useMap();
//   useEffect(() => {
//     map.fitBounds(bounds);
//   }, [bounds, map]);

//   return null;
// };

// const BusMap = ({ selectedBusRoute }) => {
//   if (!selectedBusRoute || !selectedBusRoute.data) {
//     return <div>Loading...</div>;
//   }

//   const mapStyle = {
//     height: "400px",
//     width: "100%"
//   };

//   const geoJsonData = selectedBusRoute.data;
//   const lineStyle = {
//     color: "blue",
//     weight: 5,
//     opacity: 0.65 
//   };

//   // Create bounds from the GeoJSON data to fit the map view
//   const bounds = L.geoJSON(geoJsonData).getBounds();

//   // Process GeoJSON Points to create markers and popups
//   const markers = geoJsonData.features.map((feature, index) => {
//     if (feature.geometry.type === "Point") {
//       const [longitude, latitude] = feature.geometry.coordinates;
//       const stopName = feature.properties["Stop Name"];
      
//       return (
//         <Marker key={index} position={[latitude, longitude]}>
//           <Popup>
//             {stopName}<br />
//             Position: {latitude}, {longitude}
//           </Popup>
//         </Marker>
//       );
//     }
//     return null;
//   }).filter(marker => marker !== null); // Filter out any null values

//   return (
//     <MapContainer center={[53.345123, -6.26526]} zoom={13} style={mapStyle} whenCreated={mapInstance => {
//       setTimeout(() => mapInstance.invalidateSize(), 0);
//     }}>
//       <TileLayer
//         url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
//       />
//       <GeoJSON data={geoJsonData} style={lineStyle} />
//       {markers}
//       <FitBounds bounds={bounds} />
//     </MapContainer>
//   );
// };

// // export default BusMap;
