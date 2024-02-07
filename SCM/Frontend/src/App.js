import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LoginPage from './Components/LoginPage';
import RegisterPage from './Components/RegisterPage';
import HomePage from './Components/HomePage';
import TimeSeriesDashboardPage from './Components/TimeSeriesDashboardPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LoginPage />} />
        {/* <Route path="/register" element={<RegisterPage />} /> */}
        <Route path="/home" element={<HomePage />} />
        <Route path="/time-series-dashboard" element={<TimeSeriesDashboardPage />} />
      </Routes>
    </Router>
  );
}

export default App;
