import React from 'react';
import dummyData from '../DummyData/air';
import TimeSeriesDashboard from './TimeSeriesDashboard';

function HomePage() {

  return (
    <div>
      <h1>Home Page</h1>
      
      {/* Time Series Dashboard */}
      <div>
        <TimeSeriesDashboard data={dummyData} />
      </div>
    </div>
  );
}

export default HomePage;
