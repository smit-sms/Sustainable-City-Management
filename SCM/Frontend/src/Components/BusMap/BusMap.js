import ToggleSwitch from './ToggleSwitch';
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './BusMap.css'; // Assuming this is in the same directory as your component

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

function AddMarkerOnClick({ onAdd, enabled, customMarkers }) {
  useMapEvents({
    click(e) {
      if (enabled && customMarkers.length < 2) { // Limit to 2 markers
        const { lat, lng } = e.latlng;
        onAdd({ lat, lng });
      }
    },
  });
  return null;
}

const BusMap = ({ selectedBusRoute, selectedBus }) => {
  const [customMarkers, setCustomMarkers] = useState([]);
  const [mapKey, setMapKey] = useState(0); // Initial key
  const [isEditModeEnabled, setIsEditModeEnabled] = useState(false);
  const [selectedStartingPoint, setSelectedStartingPoint] = useState(null);
  const [selectedEndPoint, setSelectedEndPoint] = useState(null);
  const [updatedRoute, setRouteData] = useState(null); // This will hold the route data


  console.log(selectedBus)

  useEffect(() => {
    if (customMarkers.length === 2) {
      // Prompt user to select a starting point once two markers are added
      alert('Please select a starting point from the existing bus stops.');

    }
  }, [customMarkers]);
  useEffect(() => {
    setMapKey(prevKey => prevKey + 1); // Change this line to trigger on specific updates
  }, [selectedBus, updatedRoute]); // Dependencies array, change this based on your needs


  if (!selectedBusRoute || !selectedBusRoute.data) {
    return <div>Loading...</div>;
  }
  function AddMarkerOnClick({ onAdd, enabled, customMarkers }) {
    useMapEvents({
      click(e) {
        if (enabled && customMarkers.length < 2) {
          const { lat, lng } = e.latlng;
          onAdd({ lat, lng });
        }
      },
    });
    return null;
  }

  const resetMap = () => {
    setCustomMarkers([]);
    setRouteData(null); // Now this call to setUpdatedRoute will work
    setIsEditModeEnabled(false);
    // Reset any other relevant state here
  };
  const sendDataToBackend = async () => {
    // Construct payload
    const payload = {
      bus_name: selectedBus, // Assuming this is how you pass the selected bus name
      coordinates: [
        [selectedStartingPoint.lng, selectedStartingPoint.lat, selectedStartingPoint.name], // Starting point
        ...customMarkers.map(marker => [marker.lng, marker.lat, "stop1"]), // Custom markers (additional stops)
        [selectedEndPoint.lng, selectedEndPoint.lat, selectedStartingPoint.name] // Ending point
      ]
    };
    console.log(payload)
    console.log(selectedStartingPoint["Stop Name"])
    try {
      // Send POST request to the backend
      const response = await fetch('https://bb45-134-226-214-245.ngrok-free.app/city_services/bus-routes/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

    //   // Handle response data
      const updatedRouteResponse = await response.json();
      console.log('Updated route:', updatedRouteResponse.data);
      setRouteData(updatedRouteResponse);
      // Update your state or map based on the response
    } catch (error) {
      console.error('Failed to send data to backend:', error);
    }

    //   // Handle response data
    //   const geoJsonData = await response.json();
    //   console.log('Updated route:', geoJsonData.data);
    //   setRouteData(geoJsonData);
    //   // Update your state or map based on the response
    // } catch (error) {
    //   console.error('Failed to send data to backend:', error);
    // }
  };


  const mapStyle = { height: "500px", width: "100%" };
  const geoJsonData = selectedBusRoute.data;
  const lineStyle = (feature) => {
    return feature.properties.style || { color: "blue", weight: 5, opacity: 0.65 };
  }
  // const lineStyle = ;
  const bounds = L.geoJSON(geoJsonData).getBounds();

  const handleStopClick = (coordinates) => {
    if (isEditModeEnabled) {
      const coordinatesStr = JSON.stringify(coordinates); // Convert coordinates to a string for comparison
      const selectedStartingPointStr = JSON.stringify(selectedStartingPoint);
  
      if (!selectedStartingPoint) {
        setSelectedStartingPoint(coordinates);
        alert('Starting point selected. Now select an ending point.');
      } else if (!selectedEndPoint && coordinatesStr !== selectedStartingPointStr) {
        setSelectedEndPoint(coordinates);
        alert('Ending point selected.');
      }

    }
    console.log(selectedStartingPoint);
    console.log(selectedEndPoint);
  };
  
  const busStopMarkers = geoJsonData.features.filter(feature => feature.geometry.type === "Point").map((feature, index) => (
    <Marker
      key={index}
      position={[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]}
      eventHandlers={{
        click: () => handleStopClick({lat: feature.geometry.coordinates[1], lng: feature.geometry.coordinates[0]}),
      }}
    >
      <Popup>
        {feature.properties['Stop Name']}<br /> {/* Display the actual stop name */}
        Position: {feature.geometry.coordinates[1]}, {feature.geometry.coordinates[0]}
      </Popup>
    </Marker>
  ));
  

  const toggleEditMode = () => {
    setIsEditModeEnabled(!isEditModeEnabled);
    // Reset selections when toggling edit mode
    if (!isEditModeEnabled) {
      setCustomMarkers([]);
      setSelectedStartingPoint(null);
      setSelectedEndPoint(null);
    }
   
  };

  return (
    <>
    <div className="map-top-right-controls">
        <ToggleSwitch isOn={isEditModeEnabled} handleToggle={toggleEditMode} />
        {isEditModeEnabled && (
          <div className="update-route-button-container">
            <button onClick={sendDataToBackend} className="update-route-button">Update Route</button>
          </div>
        )}
        {isEditModeEnabled && (
          <button onClick={resetMap} className="reset-map-button">Reset Map</button>
        )}

      </div>
      {/* <button onClick={toggleEditMode} className="toggle-edit-mode-button">
        {isEditModeEnabled ? 'Disable Edit Mode' : 'Enable Edit Mode'}
      </button>
      <button onClick={sendDataToBackend} className="send-route-data">Send Route Data</button> */}
       <div className={`route-info-box ${!isEditModeEnabled ? 'hidden' : ''}`}>
        <div className="route-info-title">Route Information</div>
        <div className="route-info">
        <p>Starting point: {selectedStartingPoint ? `${selectedStartingPoint.name} (${selectedStartingPoint.lat}, ${selectedStartingPoint.lng})` : 'Not selected'}</p>
            <p>Ending point: {selectedEndPoint ? `${selectedEndPoint.name} (${selectedEndPoint.lat}, ${selectedEndPoint.lng})` : 'Not selected'}</p>
            {customMarkers.map((marker, index) => (
              <p key={index}>Stop {index + 1}: {marker.name ? `${marker.name} ` : ''}({marker.lat}, {marker.lng})</p>
            ))}
        </div>
      </div>

      {/* {isEditModeEnabled && customMarkers.length >= 2 && !selectedStartingPoint && (
        <div>Please select a starting point from the existing bus stops.</div>
      )}
       */}

<MapContainer key={mapKey} center={[53.345123, -6.26526]} zoom={13} style={mapStyle} bounds={bounds}>
<TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
{/* <GeoJSON data={updatedRoute || geoJsonData} style={lineStyle} /> */}
{updatedRoute ? (
    // If updatedRoute is not null, render the updated route
    <MapContainer key={mapKey} center={[53.345123, -6.26526]} zoom={13} style={mapStyle} bounds={bounds}>
    
    <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <GeoJSON data={updatedRoute.data} style={lineStyle} />
      {updatedRoute.data.features.filter(feature => feature.geometry.type === "Point").map((feature, index) => (

      <Marker
    key={index}
    position={[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]}
    eventHandlers={{
      click: () => handleStopClick({
        lat: feature.geometry.coordinates[1],
        lng: feature.geometry.coordinates[0],
        name: feature.properties['Stop Name'] // Assuming the name is stored here
      }),
    }}
  >
    <Popup>
      {feature.properties['Stop Name']}<br /> {/* Display the actual stop name */}
      Position: {feature.geometry.coordinates[1]}, {feature.geometry.coordinates[0]}
    </Popup>
  </Marker>
      ))}
    </MapContainer>
  
    
  ) : (
    // Otherwise, render the initial route data
    <GeoJSON data={geoJsonData} style={{ color: "blue", weight: 5, opacity: 0.65 }} />
  )}
 {/* <GeoJSON data={ updatedRoute || geoJsonData} style={lineStyle} />  */}
{geoJsonData.features.filter(feature => feature.geometry.type === "Point").map((feature, index) => (
  <Marker
    key={index}
    position={[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]}
    eventHandlers={{
      click: () => handleStopClick({
        lat: feature.geometry.coordinates[1],
        lng: feature.geometry.coordinates[0],
        name: feature.properties['Stop Name'] // Assuming the name is stored here
      }),
    }}
  >
    <Popup>
      {feature.properties['Stop Name']}<br /> {/* Display the actual stop name */}
      Position: {feature.geometry.coordinates[1]}, {feature.geometry.coordinates[0]}
    </Popup>
  </Marker>
))}
{customMarkers.map((marker, index) => (
  <Marker key={index} position={[marker.lat, marker.lng]}>
    <Popup>Custom Marker<br />Position: {marker.lat}, {marker.lng}</Popup>
  </Marker>
))}
{isEditModeEnabled && (
  <AddMarkerOnClick onAdd={(marker) => setCustomMarkers([...customMarkers, marker])} enabled={isEditModeEnabled} customMarkers={customMarkers} />
)}
</MapContainer>


    </>
  );
};

export default BusMap;