import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
// import BikeAvailabilityPicker from './TimePicker';
import "leaflet/dist/leaflet.css";
import moment from "moment";
import bikeImage from "../assets/bike.png";

// Move map center and zoom level outside of the component
const MAP_CENTER = [53.3498, -6.2603];
const ZOOM_LEVEL = 13;
const icon = L.icon({
	iconSize: [26, 26],
	iconAnchor: [13, 13],
	popupAnchor: [0, -13],
	iconUrl: bikeImage,
});

const BikeMap = ({ currSetTime, toast }) => {
	// console.log("GOT TIME", currSetTime.getTime());
	const [bikeStands, setBikeStands] = useState([]);
	const [availabilityPrediction, setAvailabilityPrediction] = useState([]);
	const [predictions, setPredictions] = useState([]);
	const [isRealOrPred, setIsRealOrPred] = useState("real");

	function get_data_from_dublinbikes() {
		fetch(
			"https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=8a8241e24f9e3ee686043dc6714379821333d62e"
		)
			.then((response) => {
				if (response.status == 200) return response.json();
				else throw new Error("Error in fetching live data");
			})
			.then((data) => {
				// Filter logic based on selected time
				const filteredData = data.filter((entry) => {
					entry["STATION ID"] = entry["number"];
					entry["BIKE STANDS"] = entry["bike_stands"];
					entry["LATITUDE"] = entry["position"]["lat"];
					entry["LONGITUDE"] = entry["position"]["lng"];
					return true;
				});
				setAvailabilityPrediction(filteredData);
				console.log("initial values set", filteredData);
				// toast.dark("Showing Dublin Bikes live data.");
			})
			.catch((error) => {
				// get current time
				// get predictions from backend for this current time
				// display as predictions and not as real data
				console.log(error);
				toast.error(error);
			});
	}

	useEffect(() => {
		get_data_from_dublinbikes();

		fetch("http://127.0.0.1:8000/city_services/dublin-bikes-predictions/")
			.then((response) => {
				if (response.status == 200) return response.json();
				else throw new Error("Fetching dublin bikes prediction data failed!");
			})
			.then((data) => {
				// Filter logic based on selected time
				setPredictions(data.data.prediction);
				setBikeStands(data.data.positions);
				console.log("predictions set");
			})
			.catch((error) => {
				toast.dark(error.toString());
				console.log(error);
			});
	}, []);

	useEffect(() => {
		if (predictions.length != 0 && predictions != undefined) {
			const filteredData = predictions.filter(
				(entry) => entry.TIME == currSetTime.getTime()
			);
			setAvailabilityPrediction(filteredData);
			setIsRealOrPred("pred");
		}
	}, [currSetTime]);

	return (
		<MapContainer
			center={MAP_CENTER}
			zoom={ZOOM_LEVEL}
			style={{ height: "100vh", width: "100%" }}
		>
			<TileLayer
				attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
				url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
			/>

			{availabilityPrediction.map((stand) => {
				let entry = bikeStands.filter(
					(entry) => entry["station_id"] == stand["STATION ID"]
				)[0];
				if (entry != undefined)
					try {
						return (
							<Marker
								key={stand["STATION ID"]}
								position={[entry["latitude"] ?? "", entry["longitude"] ?? ""]}
								// position={[53.3409, -6.2625]}
								icon={icon}
							>
								<Popup>
									<div>
										<h3>
											{entry["name"]} ({stand["STATION ID"]})
										</h3>
										<p>Bike Stands: {stand["BIKE STANDS"]}</p>
										<p>
											{isRealOrPred == "real"
												? "Current Available Bikes"
												: "Available Bikes Prediction"}
											: {stand.available_bikes}
										</p>
										<p>
											Time: {moment(stand.TIME).format("MMMM Do, YYYY, h:mm a")}
										</p>
									</div>
								</Popup>
							</Marker>
						);
					} catch (error) {
						console.log("error", error);
						console.log(stand["STATION ID"]);
					}
			})}
		</MapContainer>
	);
};

export default BikeMap;
