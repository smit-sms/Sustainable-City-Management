import React, { useState, useEffect } from "react";
import DatePicker from "react-datepicker";
import "react-datepicker/dist/react-datepicker.css";
import moment from "moment";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import bikeImage from "../assets/bike.png";
import { BASE_URL, DUBLIN_BIKE_API_URL } from "../services/api";

// Setup for the bike icon in Leaflet
const icon = L.icon({
  iconSize: [26, 26],
  iconAnchor: [13, 13],
  popupAnchor: [0, -13],
  iconUrl: bikeImage,
});

// Constants for the map center and zoom level
const MAP_CENTER = [53.3498, -6.2603];
const ZOOM_LEVEL = 14;

const BikeMap = () => {
  const [startDate, setStartDate] = useState(new Date());
  const currSetTime = startDate.getTime();
  const today = new Date();
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const [minTime, setMinTime] = useState(new Date());
  const [maxTime, setMaxTime] = useState(
    new Date(
      tomorrow.getFullYear(),
      tomorrow.getMonth(),
      tomorrow.getDate(),
      23,
      59
    )
  );

  const [bikeStands, setBikeStands] = useState([]);
  const [availabilityPrediction, setAvailabilityPrediction] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [isRealOrPred, setIsRealOrPred] = useState("real");

  function get_data_from_dublinbikes(pred_data) {
    fetch(`${BASE_URL}/city_services/dublin-bikes/`)
    .then((response) => {
        if (response.status === 200) return response.json();
        else throw new Error("Error in fetching live data");
      })
      .then((data) => {
        // Filter logic based on selected time
        const filteredData = data.data.filter((entry) => {
          entry["STATION ID"] = entry["station_id"];
          entry["BIKE STANDS"] = entry["bike_stands"];
          entry["LATITUDE"] = entry["latitude"];
          entry["LONGITUDE"] = entry["longitude"];
          return true;
        });
        setAvailabilityPrediction(filteredData);
      })
      .catch((error) => {
        toast.error(
          "Failed to fetch live data. Showing next available prediction."
        );

        if (pred_data.length != 0 && pred_data != undefined) {
          // Get the start time of the next hour
          const now = new Date();
          const nextHour = new Date(now);
          nextHour.setMinutes(0);
          nextHour.setSeconds(0);
          nextHour.setMilliseconds(0);
          nextHour.setHours(now.getHours() + 1);

          const filteredData = pred_data.filter(
            (entry) => entry.TIME == nextHour.getTime()
          );
          setAvailabilityPrediction(filteredData);
          setIsRealOrPred("pred");
        }
        toast.error(error);
      });
  }

  useEffect(() => {
    setMaxTime(
      new Date(
        tomorrow.getFullYear(),
        tomorrow.getMonth(),
        tomorrow.getDate(),
        23,
        59
      )
    );
  }, []);

  useEffect(() => {
    if (
      startDate.getDate() === today.getDate() &&
      startDate.getMonth() === today.getMonth() &&
      startDate.getFullYear() === today.getFullYear()
    ) {
      setMinTime(new Date());
      setMaxTime(
        new Date(
          tomorrow.getFullYear(),
          tomorrow.getMonth(),
          tomorrow.getDate(),
          23,
          59
        )
      );
    } else {
      setMinTime(
        new Date(
          tomorrow.getFullYear(),
          tomorrow.getMonth(),
          tomorrow.getDate(),
          0,
          0
        )
      );
      setMaxTime(
        new Date(
          tomorrow.getFullYear(),
          tomorrow.getMonth(),
          tomorrow.getDate(),
          today.getHours(),
          59
        )
      );
    }
  }, [startDate]);

  useEffect(() => {
    fetch(`${BASE_URL}/city_services/dublin-bikes-predictions/`)
      .then((response) => {
        if (response.status === 200) return response.json();
        else throw new Error("Fetching dublin bikes prediction data failed!");
      })
      .then((data) => {
        // Filter logic based on selected time
        let data_pred = data.data.prediction;
        setPredictions(data_pred);
        setBikeStands(data.data.positions);
        get_data_from_dublinbikes(data_pred);
      })
      .catch((error) => {
        toast.dark(error.toString());
        console.log(error);
      });
  }, []);

  useEffect(() => {
    if (predictions.length != 0 && predictions != undefined) {
      const filteredData = predictions.filter(
        (entry) => entry.TIME == currSetTime
      );
      setAvailabilityPrediction(filteredData);
      toast.success("Showing predicted data");
      setIsRealOrPred("pred");
    }
  }, [currSetTime]);

  return (
    <div>
      <div className="p-4">
        <h1 className="text-3xl font-bold text-center mb-2">DUBLIN BIKES</h1>
        <hr className="border-t-2 border-gray-200 mb-2" />
      </div>
      <div
        className="relative w-full overflow-hidden"
        style={{ height: "calc(100vh - 95px)" }}
      >
        <MapContainer
          center={MAP_CENTER}
          zoom={ZOOM_LEVEL}
          className="h-full z-0"
          style={{ height: "calc(100vh - 95px)" }}
        >
          <TileLayer url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}.png" />
          {availabilityPrediction.map((stand) => {
            let entry = bikeStands.filter(
              (entry) => entry["station_id"] == stand["STATION ID"]
            )[0];
            if (entry != undefined)
              try {
                return (
                  <Marker
                    key={stand["STATION ID"]}
                    position={[
                      entry["latitude"] ?? "",
                      entry["longitude"] ?? "",
                    ]}
                    icon={icon}
                  >
                    <Popup>
                      <div>
                        <b>
                          {entry["name"]} ({stand["STATION ID"]})
                        </b>
                        <p>Total Bike Stands: {stand["BIKE STANDS"]}</p>
                        <p>
                          {isRealOrPred == "real"
                            ? "Current Available Bikes"
                            : "Available Bikes Prediction"}
                          : {stand.available_bikes}
                        </p>
                        <p>
                          Time:{" "}
                          {moment(stand.TIME).format("MMMM Do, YYYY, h:mm a")}
                        </p>
                      </div>
                    </Popup>
                  </Marker>
                );
              } catch (error) {
                toast.error("Some error occured, please try again.");
              }
          })}
        </MapContainer>
        <div
          className="absolute top-1 right-1 z-10 p-2 rounded-lg bg-gray-100 justify-end"
          style={{ maxWidth: "100%", overflow: "visible" }}
        >
          <div className="font-bold justify-end">
            Select time to view predictions:&emsp;&emsp;&emsp;
          </div>
          <DatePicker
            selected={startDate}
            onChange={(date) => setStartDate(date)}
            showTimeSelect
            dateFormat="MMMM d, yyyy h:mm aa"
            minDate={today}
            maxDate={tomorrow}
            minTime={minTime}
            maxTime={maxTime}
            timeIntervals={60}
            className="form-input block w-full px-3 py-1.5 text-base font-bold text-green-700 bg-green bg-clip-padding border border-green-500 rounded transition ease-in-out m-0 focus:text-green-700 focus:border-green-600 focus:outline-none justify-end"
          />
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
};

export default BikeMap;
