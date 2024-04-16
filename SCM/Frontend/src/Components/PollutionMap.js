import React, { useRef } from "react";
import { useState, useEffect, useMemo } from "react";
// import "../assets/styles/style_leaflet.css";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { customReactIcon } from "../utils/customReactIcons";
import { FaMicrophone, FaWind } from "react-icons/fa";
import { BASE_URL } from "../services/api";
import { ToastContainer } from "react-toastify";
import L from "leaflet";
import CustomFetch from "../utils/customFetch";
import { useNavigate } from "react-router-dom";

function PollutionMap() {
	const [sensors, setSensors] = useState([]);
	const [predictions, setPredictions] = useState([]);
	const [showPredictions, setShowPredictions] = useState(false);
	const navigate = useNavigate();

	const getsensors = () => {
		CustomFetch(`${BASE_URL}/sensors/air-noise`, {
				method: 'GET'
			}, navigate)
			.then((response) => {
			const data = response.json();
			setSensors(data.data);
			getPredictions();
		});
	};

	const getPredictions = () => {
		let predictions_temp = [];
		CustomFetch(`${BASE_URL}/sensors/air-predictions`, {
				method: 'GET'
			}, navigate)
			.then((response) => {
			if (response.status === 200 || response.status === 201) {
				const data = response.json().then((data_new) => {
					console.log(data_new);
					if (data_new) {
						predictions_temp.push(...data_new.data);
					}
				});
			}
		});
		CustomFetch(`${BASE_URL}/sensors/noise-predictions`, {
				method: 'GET'
			}, navigate)
			.then((response) => {
			if (response.status === 200 || response.status === 201) {
				const data = response.json().then((data_new) => {
					console.log(data_new);
					if (data_new) {
						predictions_temp.push(...data_new.data);
						setPredictions(predictions_temp);
					}
				});
			}
		});
	};

	useEffect(() => {
		getsensors();
		// getPredictions();
	}, []);

	const RenderIcons = () => {
		const eventHandlers = useMemo(() => ({
			mouseover() {
				this.openPopup();
			},
			mouseout() {
				this.closePopup();
			},
		}));

		var sensors_to_show = showPredictions ? predictions : sensors;
		return sensors_to_show.map((feature, index) => (
			<Marker
				key={index}
				position={[feature.latitude, feature.longitude]}
				// icon={getIcon(feature.sensor_type, feature.status)}
				icon={
					feature.sensor_type === "air"
						? customReactIcon(FaWind, feature.status)
						: customReactIcon(FaMicrophone, feature.status)
				}
				eventHandlers={eventHandlers}
			>
				<Popup>
					<div>
						Station ID
						<br />
						{feature.serial_number}
						<br />
						{feature.sensor_type}
						<br />
						{feature.value} {feature.unit}
						<br />
						{feature.status}
						<br />
						{feature.datetime}
					</div>
				</Popup>
			</Marker>
		));
	};

	return (
		<div>
			<div className="p-4">
				<h1 className="text-3xl font-bold text-center mb-2">POLLUTION</h1>
				<hr className="border-t-2 border-gray-200 mb-2" />
			</div>
			<div
				className="relative w-full overflow-hidden"
				style={{ height: "calc(100vh - 95px)" }}
			>
				<div>
					<MapContainer
						center={[53.35442, -6.24896]}
						zoom={12}
						className="h-full z-0"
						style={{ height: "calc(100vh - 95px)" }}
					>
						<TileLayer
							attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
							url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png"
						/>
						<RenderIcons />
					</MapContainer>
				</div>

				<div
					className="absolute top-1 right-1 z-10 p-2 rounded-lg bg-gray-100 justify-end"
					style={{ maxWidth: "100%", overflow: "visible" }}
				>
					<div className="font-bold justify-end">
						Show 1 hr future predictions:&emsp;&emsp;&emsp;
					</div>

					<button
						onClick={() =>
							showPredictions
								? setShowPredictions(false)
								: setShowPredictions(true)
						}
						className="bg-red-500 text-white py-2 px-2 text-sm rounded-md cursor-pointer hover:bg-red-700"
					>
						{" "}
						{showPredictions ? "Hide predictions" : "Show predictions"}
					</button>
				</div>
			</div>
			<ToastContainer
				position="top-right"
				autoClose={5000}
				hideProgressBar={false}
				newestOnTop={false}
				closeOnClick
				rtl={false}
				theme="colored"
				pauseOnFocusLoss
				draggable
				pauseOnHover
			/>
		</div>
	);
}

export default PollutionMap;
