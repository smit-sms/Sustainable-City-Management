import React, { useEffect, useState, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.markercluster";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { BASE_URL, DUBLIN_WASTE_FACILITIES } from "../services/api";
import binIconPng from "../assets/bin_icon.png";
import currLocIconPng from "../assets/current-location-icon.png";

const binIcon = L.icon({
	iconSize: [22, 22],
	iconAnchor: [11, 11],
	popupAnchor: [0, -11],
	iconUrl: binIconPng,
});

const currLocIcon = L.icon({
	iconSize: [22, 22],
	iconAnchor: [11, 11],
	popupAnchor: [0, -11],
	iconUrl: currLocIconPng,
});

export default function BinLocations() {
	const [map, setMap] = useState(null);
	const [mapLayersControl, setMapLayersControl] = useState(null);
	const [binData, setBinData] = useState(null);
	const [wasteFacilities, setWasteFacilities] = useState(null);
	const [currentLocation, setCurrentLocation] = useState(null);

	var binDataMapLayer = useRef(L.layerGroup());
	var wasteFacilitiesMapLayer = useRef(L.layerGroup());
	var currentLocationMapLayer = useRef(L.layerGroup());

	function initializeMap() {
		if (!map) {
			const leafletMap = L.map("map", {
				center: [53.349805, -6.26031],
				zoom: 13,
			});
			L.tileLayer(
				"https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png",
				{ attribution: "leaflet" }
			).addTo(leafletMap);

			setMapLayersControl(L.control.layers(null).addTo(leafletMap));

			setMap(leafletMap);
		}
	}

	// Fetch the data
	useEffect(() => {
		// Fetch bin locations and store in variable `binData`
		fetch(`${BASE_URL}/city_services/bin-locations/`)
			.then((response) => {
				if (response.status === 200) return response.json();
				else throw new Error("Fetching bin location data failed!");
			})
			.then((data) => {
				setBinData(data.data);
			})
			.catch((error) => {
				toast.dark(error.toString());
				console.log(error);
			});

		// Fetch waste facilities locations and store in variable `wasteFacilities`
		fetch(DUBLIN_WASTE_FACILITIES)
			.then((response) => {
				if (response.status === 200) return response.json();
				else throw new Error("Fetching waste facilities data failed!");
			})
			.then((data) => {
				setWasteFacilities(data);
			})
			.catch((error) => {
				toast.dark(error.toString());
				console.log(error);
			});
	}, []);

	useEffect(() => {
		initializeMap();

		if (!navigator.geolocation) {
			toast.error("Current location unavailable!");
		} else {
			navigator.geolocation.getCurrentPosition(
				(position) => {
					setCurrentLocation([
						position.coords.latitude,
						position.coords.longitude,
					]);
					if (map && !map.hasLayer(currentLocationMapLayer.current)) {
						L.marker([position.coords.latitude, position.coords.longitude], {
							icon: currLocIcon,
						}).addTo(currentLocationMapLayer.current);
						map.addLayer(currentLocationMapLayer.current);
						mapLayersControl.addOverlay(
							currentLocationMapLayer.current,
							"Current Location"
						);
					}
				},
				() => {
					toast.error("Unable to retrieve your location");
				}
			);
		}

		if (map && binData && !map.hasLayer(binDataMapLayer.current)) {
			binDataMapLayer.current = L.markerClusterGroup({
				iconCreateFunction: function (cluster) {
					return L.divIcon({
						html:
							`<div style="background-color: grey; color: white; 
							border-radius: 50%; width: 30px; height: 30px; display: 
							flex; justify-content: center; align-items: center;">` +
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
					{ icon: binIcon }
				).addTo(binDataMapLayer.current);
				marker.bindPopup(
					`<b>${bin.properties.Electoral_Area}</b><br>Bin Type: ${bin.properties.Bin_Type}`
				);
			});
			map.addLayer(binDataMapLayer.current);
			mapLayersControl.addOverlay(binDataMapLayer.current, "Bins");
		}

		if (
			map &&
			wasteFacilities &&
			!map.hasLayer(wasteFacilitiesMapLayer.current)
		) {
			wasteFacilities.features.forEach(function (wasteFacility) {
				// Keeping facilities in Dublin only
				if (
					wasteFacility.geometry.coordinates[0][1] > 53.45 ||
					wasteFacility.geometry.coordinates[0][1] < 53.19 ||
					wasteFacility.geometry.coordinates[0][0] < -6.45122489
				)
					return;

				// console.log(wasteFacility.properties);
				// console.log(wasteFacility.properties.Category);
				var marker = L.marker([
					wasteFacility.geometry.coordinates[0][1],
					wasteFacility.geometry.coordinates[0][0],
				]).addTo(wasteFacilitiesMapLayer.current);
				marker.bindPopup(
					`<h1><b>${wasteFacility.properties.Name}</b></h1>
					<br/><b>Address:</b> ${wasteFacility.properties.Address}
					<br/><b>Licence Number:</b> ${wasteFacility.properties.ActiveLicenceNumber}
					<br/><b>Location:</b> ${wasteFacility.geometry.coordinates[0][1]},
						${wasteFacility.geometry.coordinates[0][0]}
					`
				);
			});
			map.addLayer(wasteFacilitiesMapLayer.current);
			mapLayersControl.addOverlay(
				wasteFacilitiesMapLayer.current,
				"Waste Facilities"
			);
		}
	}, [map, binData, wasteFacilities]);

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
}
