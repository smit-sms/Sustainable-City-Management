import ToggleSwitch from './ToggleSwitch';
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, GeoJSON, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../../assets/styles/BusMap.css'
import { BASE_URL } from '../../services/api';

// Fix for default marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const BusMap = ({ selectedBusRoute, selectedBus }) => {
  const [customMarkers, setCustomMarkers] = useState([]);
  const [mapKey, setMapKey] = useState(0);
  const [isEditModeEnabled, setIsEditModeEnabled] = useState(false);
  const [selectedStartingPoint, setSelectedStartingPoint] = useState(null);
  const [selectedEndPoint, setSelectedEndPoint] = useState(null);
  const [updatedRoute, setRouteData] = useState(null);

  useEffect(() => {
    if (customMarkers.length === 2) {
      toast.info('Please select a starting point from the existing bus stops.');
    }
  }, [customMarkers]);
  useEffect(() => {
    setMapKey(prevKey => prevKey + 1);
  }, [selectedBus, updatedRoute]);

  if (!selectedBusRoute || !selectedBusRoute.data) {
    // Default empty map rendering
    return (
      <div>
        <MapContainer center={[53.345123, -6.26526]} zoom={13} className="h-full z-0" 
        style={{ height: 'calc(100vh - 155px)' }}>
          <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png" />
        </MapContainer>
      </div>
    );
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
    setRouteData(null);
    setIsEditModeEnabled(false);
  };
  const sendDataToBackend = async () => {
    console.log(customMarkers);
    const payload = {
      bus_name: selectedBus,
      coordinates: [
        [selectedStartingPoint.lng, selectedStartingPoint.lat, selectedStartingPoint.name], // Starting point
        ...customMarkers.map((marker, index) => [marker.lng, marker.lat, `Custom Stop ${index + 1}`]), // Custom markers (additional stops)
        [selectedEndPoint.lng, selectedEndPoint.lat, selectedStartingPoint.name] // Ending point
      ]
    };
    console.log(payload);
    try {
      // Send POST request to the backend
      const response = await fetch(`${BASE_URL}/city_services/bus-routes/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const updatedRouteResponse = await response.json();
      setRouteData(updatedRouteResponse);
    } catch (error) {
      toast.error('Failed to send data to backend:', error);
    }
  };

  const geoJsonData = selectedBusRoute.data;
  const lineStyle = (feature) => {
    return feature.properties.style || { color: "blue", weight: 5, opacity: 0.65 };
  }
  const bounds = L.geoJSON(geoJsonData).getBounds();

  const handleStopClick = (coordinates) => {
    if (isEditModeEnabled) {
      const coordinatesStr = JSON.stringify(coordinates); // Convert coordinates to a string for comparison
      const selectedStartingPointStr = JSON.stringify(selectedStartingPoint);
  
      if (!selectedStartingPoint) {
        setSelectedStartingPoint(coordinates);
        toast.info('Starting point selected. Now select an ending point.');
      } else if (!selectedEndPoint && coordinatesStr !== selectedStartingPointStr) {
        setSelectedEndPoint(coordinates);
        toast.info('Ending point selected.');
      }

    }
  };
  
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
  <div className="relative w-full overflow-hidden" style={{ height: 'calc(100vh - 155px)' }}>
    <MapContainer
      key={mapKey}
      center={[53.345123, -6.26526]}
      zoom={13}
      className="h-full z-0"
    >
      {updatedRoute ? (
        // If updatedRoute is not null, render the updated route
        <>
          <div className="relative w-full overflow-hidden" style={{ height: 'calc(100vh - 155px)' }}>
            <MapContainer key={mapKey} center={[53.345123, -6.26526]} zoom={13} className="h-full z-0" bounds={bounds}>
            <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png" />
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
                }}>
                <Popup>
                  {feature.properties['Stop Name']}<br />
                  Position: {feature.geometry.coordinates[1]}, {feature.geometry.coordinates[0]}
                </Popup>
              </Marker>
            ))}
            </MapContainer>
          </div></>
      ) : (
        <>
        {/* Otherwise, render the initial route data */}
        <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png" />
        <GeoJSON data={geoJsonData} style={{ color: "blue", weight: 5, opacity: 0.65 }} />
        {geoJsonData.features.filter(feature => feature.geometry.type === "Point").map((feature, index) => (
          <Marker
            key={index}
            position={[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]}
            eventHandlers={{
              click: () => handleStopClick({
                lat: feature.geometry.coordinates[1],
                lng: feature.geometry.coordinates[0],
                name: feature.properties['Stop Name']
              }),
            }}
          >
            <Popup>
              {feature.properties['Stop Name']}<br />
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
        )}</>
      )}
    </MapContainer>

    <div className="absolute top-1 right-1 z-10 p-5 rounded-lg bg-gray-100 text-dark shadow-lg justify-items-center">
      <ToggleSwitch isOn={isEditModeEnabled} handleToggle={toggleEditMode}/>
      {isEditModeEnabled && (
          <><div className="font-bold text-md mt-2">Route Information:</div>
          <p className="text-sm">
            Starting point: {selectedStartingPoint ? `${selectedStartingPoint.name} (${selectedStartingPoint.lat.toFixed(3)}, ${selectedStartingPoint.lng.toFixed(3)})` : 'Not selected'}
          </p>
          <p className="text-sm">
            Ending point: {selectedEndPoint ? `${selectedEndPoint.name} (${selectedEndPoint.lat.toFixed(3)}, ${selectedEndPoint.lng.toFixed(3)})` : 'Not selected'}
          </p>
          {customMarkers.map((marker, index) => (
            <p className="text-sm" key={index}>Custom Stop {index + 1}: ({marker.lat.toFixed(3)}, {marker.lng.toFixed(3)})</p>
          ))}
          <div className="mt-2 grid grid-cols-2 gap-1">
            <button onClick={sendDataToBackend} className="bg-blue-500 text-white py-2 px-2 text-sm rounded-md cursor-pointer hover:bg-blue-700">
              Update Route
            </button>
            <button onClick={resetMap} className="bg-red-500 text-white py-2 px-2 text-sm rounded-md cursor-pointer hover:bg-red-700">
              Reset Map
            </button>
          </div>
          </>
      )}
    </div>
    <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored" pauseOnFocusLoss draggable pauseOnHover />
  </div>
);
};

export default BusMap;
