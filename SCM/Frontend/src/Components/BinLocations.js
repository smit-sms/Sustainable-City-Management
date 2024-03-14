import React, { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
// import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";

// import 'leaflet.markercluster/dist/MarkerCluster.css';
// import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import "leaflet.markercluster";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { BASE_URL } from "../services/api";

const BinLocations = () => {
	const [map, setMap] = useState(null);
	const [binData, setBinData] = useState({});

	useEffect(() => {
		fetch(`${BASE_URL}/city_services/bin-locations/`)
			.then((response) => {
				if (response.status === 200) return response.json();
				else throw new Error("Fetching dublin bikes prediction data failed!");
			})
			.then((data) => {
                console.log("fetched data", data);
				setBinData(data.data);
			})
			.catch((error) => {
				toast.dark(error.toString());
				console.log(error);
			});
	}, []);

	useEffect(() => {
        console.log("binData", binData);
		if (map && Object.keys(binData).length !== 0) {
			const markers = L.markerClusterGroup({
				iconCreateFunction: function (cluster) {
					return L.divIcon({
						html:
							'<div style="background-color: grey; color: white; border-radius: 50%; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center;">' +
							cluster.getChildCount() +
							"</div>",
						className: "custom-cluster-icon",
					});
				},
				showCoverageOnHover: false,
				maxClusterRadius: 50,
				spiderfyOnMaxZoom: false,
				disableClusteringAtZoom: 18,
				animateAddingMarkers: true,
			});
			binData.features.forEach((bin) => {
				const marker = L.marker([
					bin.geometry.coordinates[1],
					bin.geometry.coordinates[0],
				]);
				marker.bindPopup(`<b>${bin.properties.Electoral_Area}</b><br>Bin Type: ${bin.properties.Bin_Type}`);
				markers.addLayer(marker);
			});

			map.addLayer(markers);
		} 
        if(!map) {
			const leafletMap = L.map("map").setView([53.349805, -6.26031], 13);

			L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
				attribution: "© OpenStreetMap contributors",
			}).addTo(leafletMap);

			setMap(leafletMap);
		}
	}, [map, binData]);

	return (
		<div>
			<div id="map" style={{ height: "600px" }}></div>

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
};

export default BinLocations;
