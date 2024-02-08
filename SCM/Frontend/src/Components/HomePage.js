import React from 'react';
import Button from './Button';
import dummyData from '../DummyData/air';
import { Link } from 'react-router-dom';
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
