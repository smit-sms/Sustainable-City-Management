import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, Outlet, useLocation } from 'react-router-dom';
import LoginPage from './Components/LoginPage';
import RegisterPage from './Components/RegisterPage';
// import HomePage from './Components/HomePage';
import BusPage from './Components/BusPage';
import EnergyUsageMap from './Components/EnergyUsageMap'

function Sidebar() {
  const location = useLocation();
  const isActive = (pathname) => location.pathname === pathname;

  return (
    <div className="bg-gray-800 text-white w-64 py-7 px-2 absolute inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition duration-200 ease-in-out flex flex-col justify-between">
      <nav className="flex flex-col">
        <Link to="/bus"
          className={`block py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${isActive('/bus') ? 'bg-gray-700' : ''}`}>
          Bus
        </Link>
        <hr className="border-gray-700" />
        <Link to="/bike" 
          className={`block py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${isActive('/bike') ? 'bg-gray-700' : ''}`}>
          Dublin Bikes
        </Link>
        <hr className="border-gray-700" />
        <Link to="/bin" 
        className={`block py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${isActive('/bin') ? 'bg-gray-700' : ''}`}>
          Bin Trucks
        </Link>
        <hr className="border-gray-700" />
        <Link to="/energy" 
        className={`block py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${isActive('/bin') ? 'bg-gray-700' : ''}`}>
          Renewable Energy
        </Link>
      </nav>

      <div className="mt-auto">
        <button
          // onClick={handleLogout}
          className="w-full py-2 px-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-md transition duration-200 mt-4">
          Logout
        </button>
      </div>
    </div>
  );
}

function LayoutWithSidebar() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 min-h-screen">
        <Outlet />
      </div>
    </div>
  );
}

function App() {
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          <Route element={<LayoutWithSidebar />}>
            <Route path="/bus" element={<BusPage />} />
            <Route path="/energy" element={<EnergyUsageMap />} />
          </Route>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
