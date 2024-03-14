import React, { useEffect, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
// import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { FaBars, FaBus, FaVolumeUp, FaWind, FaTrash } from "react-icons/fa";

// import 'leaflet.markercluster/dist/MarkerCluster.css';
// import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import "leaflet.markercluster";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { BASE_URL } from "../services/api";

import bikeImage from "../assets/bin_icon.png";
const icon = L.icon({
	iconSize: [22, 22],
	iconAnchor: [11, 11],
	popupAnchor: [0, -11],
	iconUrl: bikeImage,
});

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
				spiderfyOnMaxZoom: true,
				disableClusteringAtZoom: 18,
				animateAddingMarkers: true,
			});
			binData.features.forEach((bin) => {
				const marker = L.marker(
					[bin.geometry.coordinates[1], bin.geometry.coordinates[0]],
					{ icon: icon }
				);
				marker.bindPopup(
					`<b>${bin.properties.Electoral_Area}</b><br>Bin Type: ${bin.properties.Bin_Type}`
				);
				markers.addLayer(marker);
			});

			map.addLayer(markers);
		}
		if (!map) {
			const leafletMap = L.map("map").setView([53.349805, -6.26031], 13);
			L.tileLayer(
				"https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png",
				{
					attribution: "© OpenStreetMap contributors",
				}
			).addTo(leafletMap);

			setMap(leafletMap);
		}
	}, [map, binData]);

	return (
		<div>
			<div className="p-4">
				<h1 className="text-3xl font-bold text-center mb-2">BINS</h1>
				<hr className="border-t-2 border-gray-200 mb-2" />
			</div>
			<div
				id="map"
				className="relative w-full overflow-hidden"
				style={{ height: "calc(100vh - 90px)" }}
			></div>

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
