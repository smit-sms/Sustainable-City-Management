import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './Components/LoginPage';
import RegisterPage from './Components/RegisterPage';
import HomePage from './Components/HomePage';
import BusMap from './components/BusMap/BusMap';
import BusSelector from './components/BusSelector/BusSelector';
import './App.css';

function App() {
  const [selectedBus, setSelectedBus] = useState({
    busName: null,
    routeData: null,
  });

  const handleBusSelect = (busName, selectedRoute) => {
    // Assuming BusSelector now calls this with both busName and route data
    setSelectedBus({
      busName: busName,
      routeData: { data: selectedRoute },
    });
  };
  return (<div>
    <div className="App">
      <BusSelector onBusSelect={handleBusSelect} />
      {/* Pass both busName and selectedBusRoute as props */}
      <BusMap selectedBusRoute={selectedBus.routeData} selectedBus={selectedBus.busName} />
    </div>

    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/home" element={<HomePage />} />
      </Routes>
    </Router>
    </div>
    
  ); 
}

export default App;
