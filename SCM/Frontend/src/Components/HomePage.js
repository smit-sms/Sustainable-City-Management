import React from 'react';
import dummyData from '../DummyData/air';
import TimeSeriesDashboard from './TimeSeriesDashboard';

function HomePage() {

  return (
    <div>
      <h1>Home Page</h1>
      
      {/* Time Series Dashboard */}
      <div>
        <TimeSeriesDashboard 
            data={dummyData} 
            seasonalityPeriod={12} 
            movingAvgWindowSize={24}
        />
      </div>
    </div>
  );
}

export default HomePage;
