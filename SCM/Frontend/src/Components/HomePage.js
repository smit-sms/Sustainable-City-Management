import React from 'react';
import Button from './Button';
import dummyData from '../DummyData/air';
import { Link } from 'react-router-dom';

function HomePage() {

  return (
    <div>
      <h1>Home Page</h1>
      
      {/* Time Series Dashboard */}
      <Button>
        <Link to='/time-series-dashboard' state={{ data: dummyData }}>
            Time Series Dashboard
        </Link>
      </Button>
    </div>
  );
}

export default HomePage;
