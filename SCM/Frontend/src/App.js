import React, { useState, useEffect } from "react";
import {
	BrowserRouter as Router,
	Routes,
	Route,
	Link,
	Outlet,
	useLocation,
	useNavigate
} from "react-router-dom";
import Cookies from 'js-cookie';
import LoginPage from "./Components/LoginPage";
import RegisterPage from "./Components/RegisterPage";
import BikeMap from "./Components/BikeMap";
import BusPage from "./Components/BusPage";
import EnergyUsageMap from "./Components/EnergyUsageMap";
import PollutionMap from "./Components/PollutionMap";
import TimeSeriesAnalysis from "./Components/TimeSeriesAnalysis";
import BinLocations from "./Components/BinLocations";
import { FaBars, FaBus, FaReact, FaTrash, FaSmog } from "react-icons/fa";
import {
	MdDirectionsBike,
	MdEnergySavingsLeaf,
	MdLogout,
} from "react-icons/md";

function Sidebar({ isOpen, toggleSidebar }) {
	const location = useLocation();
	const isActive = (pathname) => location.pathname === pathname;
	const navigate = useNavigate();
	const handleLogout = () => {
		Cookies.remove('access_token');
		Cookies.remove('refresh_token');
		navigate('/');
	};

	return (
		<div
			className={`bg-gray-800 text-white w-64 py-7 px-2 absolute inset-y-0 left-0 transform ${
				isOpen ? "translate-x-0" : "-translate-x-full"
			} md:relative md:translate-x-0 transition duration-300 ease-in-out flex flex-col justify-between z-20`}
		>
			<div className="mb-5">
				<img
					src="/logo.png"
					alt="Dashboard Logo"
					className="h-16 w-16 mx-auto"
				/>
				<h1 className="text-center text-4xl mt-2 mb-4">EcoCity</h1>
			</div>
			<nav className="flex flex-col">
				<Link
					to="/bus"
					className={`flex items-center py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${
						isActive("/bus") ? "bg-gray-700" : ""
					}`}
				>
					<FaBus className="mr-2" />
					Bus
				</Link>
				<hr className="border-gray-700" />
				<Link
					to="/bike"
					className={`flex items-center py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${
						isActive("/bike") ? "bg-gray-700" : ""
					}`}
				>
					<MdDirectionsBike className="mr-2" />
					Dublin Bikes
				</Link>
				<hr className="border-gray-700" />
				<Link
					to="/bins"
					className={`flex items-center py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${
						isActive("/bins") ? "bg-gray-700" : ""
					}`}
				>
					<FaTrash className="mr-2" />
					Bins
				</Link>
				<hr className="border-gray-700" />
				<Link
					to="/pollution"
					className={`flex items-center py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${
						isActive("/pollution") ? "bg-gray-700" : ""
					}`}
				>
					<FaSmog className="mr-2" />
					Pollution
				</Link>
				<hr className="border-gray-700" />
				<Link
					to="/energy"
					className={`flex items-center py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${
						isActive("/energy") ? "bg-gray-700" : ""
					}`}
				>
					<MdEnergySavingsLeaf className="mr-2" />
					Renewable Energy
				</Link>
				<hr className="border-gray-700" />
				<Link
					to="/time-series-analysis"
					className={`flex items-center py-2.5 mt-2 mb-2 px-4 rounded transition duration-200 hover:bg-gray-700 ${
						isActive("/time-series-analysis") ? "bg-gray-700" : ""
					}`}
				>
					<FaReact className="mr-2" />
					Time Series Analysis
				</Link>
			</nav>

			<div className="mt-auto">
				<button
					onClick={handleLogout}
					className="flex justify-center items-center w-full py-2 px-4 border border-green-600 hover:bg-green-600 text-white font-semibold rounded-md transition duration-200 mt-4 space-x-2"
				>
					<MdLogout className="inline-block" size={20} />
					<span>Logout</span>
				</button>
			</div>
		</div>
	);
}

function LayoutWithSidebar() {
	const [isOpen, setIsOpen] = useState(false);
	const navigate = useNavigate();

	const toggleSidebar = () => {
		setIsOpen(!isOpen);
	};

	useEffect(() => {
		if(!Cookies.get('access_token')){
		  navigate('/');
		}
	},[navigate]);

	return (
		<div className="flex">
			<button
				onClick={toggleSidebar}
				className={`text-dark md:hidden z-30 fixed top-0 left-0 p-4 ${
					isOpen ? "text-white" : "text-dark"
				}`}
			>
				<FaBars />
			</button>
			<Sidebar isOpen={isOpen} toggleSidebar={toggleSidebar} />
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
						<Route path="/bike" element={<BikeMap />} />
						<Route path="/bins" element={<BinLocations />} />
						<Route path="/pollution" element={<PollutionMap />} />
						<Route path="/time-series-analysis" element={<TimeSeriesAnalysis />} />
						<Route path="*" element={<LoginPage />} />
					</Route>
				</Routes>
			</Router>
		</div>
	);
}

export default App;
