import React, { useState } from 'react';

import BusMap from './BusMap/BusMap';
import BusSelector from './BusSelector/BusSelector';

function BusPage() {
  const [selectedBus, setSelectedBus] = useState({
    busName: null,
    routeData: null,
  });

  const handleBusSelect = (busName, selectedRoute) => {
    // BusSelector calls this with both busName and route data
    setSelectedBus({
      busName: busName,
      routeData: { data: selectedRoute },
    });
  };
  return (
    <div>
        <div className="App">
            <BusSelector onBusSelect={handleBusSelect} />
            <BusMap selectedBusRoute={selectedBus.routeData} selectedBus={selectedBus.busName} />
        </div>
    </div>
  ); 
}

export default BusPage;
