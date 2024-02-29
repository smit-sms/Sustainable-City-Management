import React from 'react';
import { useState, useEffect } from 'react';
import '../assets/styles/EnergyUsageMap.css'
import { MapContainer,Marker, Popup, TileLayer, GeoJSON } from 'react-leaflet';
import "leaflet/dist/leaflet.css";
import countries from "../assets/area.json";
import { Icon } from 'leaflet';
import customIconImage from '../assets/pin.png';
import powerPlants from '../assets/powerPlants.json'


function Style(countries) {
  return {
    fillColor: getColor(countries.properties.Estimated_Annual_Cost),
    fillOpacity: 0.6
  };
}

function getColor(d) {
  return d > 300000 ? '#800026' :
         d > 250000 ? '#BD0026' :
         d > 200000 ? '#E31A1C' :
         d > 150000 ? '#FC4E2A' :
         d > 50 ? '#FD8D3C' :
         d > 20 ? '#FEB24C' :
         d > 10 ? '#FED976' :
         '#FFEDA0';
}


// Function to update the Active Production of a power plant based on wind speed
function updateActiveProduction(powerPlants, plantName, windSpeed) {
  // Determine the increase factor based on wind speed
  let increaseFactor;
  if (windSpeed > 20) {
    increaseFactor = 1.2; // Increase production by 20% for wind speeds over 20
  } else if (windSpeed > 10) {
    increaseFactor = 1.1; // Increase production by 10% for wind speeds over 10
  } else {
    increaseFactor = 1.05; // Increase production by 5% for wind speeds 10 or below
  }

  // Update the Active Production of the specified power plant
  const updatedPowerPlants = powerPlants?.features.map((feature) => {
    if (feature.properties.Name === plantName) {
      const currentProduction = parseFloat(feature.properties['Active Production']);
      const updatedProduction = currentProduction * increaseFactor;
      return {
        ...feature,
        properties: {
          ...feature.properties,
          'Active Production': updatedProduction.toFixed(2) // Keep two decimal places
        }
      };
    }
    return feature;
  });
  return updatedPowerPlants; // Return the updated power plants data
}


function EnergyUsageMap() {
  const [totalEnergyUse, setTotalEnergyUse] = useState(0);
  const [totalPowerPlantEnergy, setPowerPlantEnergy] = useState(0);
  const [previousPowerOutputs] = useState(powerPlants);
  const [totalSurplus,setSurplus]=useState(0);
  const [powerPlantsData, setPowerPlantsData] = useState(powerPlants);


  // State to keep track of the slider values corresponding to power plants power production
  const [sliderValues, setSliderValues] = useState(
    powerPlants.features.reduce((acc, feature) => {
      acc[feature.properties.Name] = feature.properties['Active Production'];
      return acc;
    }, {})
  );

  // Function to calculate the current surplus
  const calculateSurplus = () => {
    const totalModifiedProduction = Object.values(sliderValues).reduce((total, current) => total + current, 0);
    const CurrentEnergyProduction = totalPowerPlantEnergy;
    // console.log(CurrentEnergyProduction - totalModifiedProduction)
    return CurrentEnergyProduction - totalModifiedProduction;
  };

  const handleSliderChange = (event, plantName) => {
  const newProductionValue = parseFloat(event.target.value);
  let newSliderValues = { ...sliderValues, [plantName]: newProductionValue };
  const totalCapacity = powerPlantsData.features.reduce((total, feature) => total + feature.properties['Total Capacity (MW)'], 0);
  
  // Calculate what the new total energy use would be with the updated slider values
  const updatedTotalEnergyUse = Object.values(newSliderValues).reduce((total, current) => total + current, 0);

  // Calculate the surplus with the updated values
  const updatedSurplus = totalCapacity - updatedTotalEnergyUse;
  
  if (updatedSurplus >= 0) {
    // If the surplus is positive, update the slider values and total energy use
    setSliderValues(newSliderValues);
    setSurplus(updatedTotalEnergyUse);
    setPowerPlantEnergy(updatedTotalEnergyUse); // Assuming this should also be updated

    // Update the main state with the new values
    const updatedFeatures = powerPlantsData.features.map(feature => {
      const updatedProduction = newSliderValues[feature.properties.Name];
      return {
        ...feature,
        properties: {
          ...feature.properties,
          'Active Production': updatedProduction
        }
      };
    });
  
    setPowerPlantsData({ ...powerPlantsData, features: updatedFeatures });
  } else {
    // If the surplus is negative, prevent the slider from moving
    alert('Unable to adjust production as it would result in a negative energy surplus.');
  }
};

  
  const customIcon = new Icon({
    iconUrl: customIconImage,
    iconSize: [20, 20]
  })

  const [weatherData, setWeatherData] = useState(null);
  // Function to fetch weather data
  const fetchWeatherData = async () => {
    try {
      const response = await fetch('https://prodapi.metweb.ie/observations/dublin/today');
      const data = await response.json();
      setWeatherData(data);

      //based on the weather changes estimate the changes in power output
      const latestWindSpeed = data[data.length - 1].windSpeed;
      const updatedPowerPlants = updateActiveProduction(powerPlants, 'Wind Farm', latestWindSpeed);
      setPowerPlantsData({ ...powerPlantsData, features: updatedPowerPlants });
      // updatePowerPlantsData(powerPlantsData);

    } catch (error) {
      console.error("Failed to fetch weather data", error);
    }
  };

   // Effect hook to fetch weather data at component mount and every hour
   useEffect(() => {
    fetchWeatherData(); // Fetch immediately on mount
    const intervalId = setInterval(fetchWeatherData, 3600000); // Refresh every hour (3600000 ms)

    return () => clearInterval(intervalId); // Cleanup interval on component unmount
  }, []);

  function onEachCountry(totalEnergyUse, setTotalEnergyUse) {
    return function(countries, layer) {
      const name = countries.properties.Local_Electorial_Area_name;
      const Energy_Use = countries.properties['Estimated_Annual_EnergyUse(kWh)'];
      const Cost_Of_Energy = countries.properties.Estimated_Annual_Cost;
      layer.bindPopup(`<div class="pop" >
        Name: ${name}
        <br/>
        Energy_Use: ${Energy_Use}(kWh)s
        <br/>
        Cost_Of_Energy: ${Cost_Of_Energy}
        </div>`);

      layer.on({
        mouseover: function(e) {
          this.openPopup();
        },
        click: function(event) {
          if (event.target.options.fillColor === "yellow") {
            totalEnergyUse = totalEnergyUse - Energy_Use;
            setTotalEnergyUse(totalEnergyUse);
            event.target.setStyle({
              fillColor: getColor(countries.properties.Estimated_Annual_Cost),
            });
            layer.bringToFront();
          } else {
            totalEnergyUse = totalEnergyUse + Energy_Use;
            setTotalEnergyUse(totalEnergyUse);
            event.target.setStyle({
              fillColor: "yellow"
            });
          }
        }
      });
    };
  }

  return (
    <div className="map-and-list-container">
      <div className='map-container'>
        {/* Displaying weather data */}
      {weatherData && weatherData.length > 0 && (
          <div className="weatherData">
            <h3>Latest weather statistics:</h3>
            <p> <b>Weather Description:</b> {weatherData[weatherData.length - 1].weatherDescription}  <b>Wind Speed:</b> {weatherData[weatherData.length - 1].windSpeed} <b>Rainfall:</b>  {weatherData[weatherData.length - 1].rainfall}</p>
          </div>
        )}
      <MapContainer center={[53.35442, -6.24896]} zoom={12}>
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        <GeoJSON
          style={Style}
          data={countries.features}
          onEachFeature={onEachCountry(totalEnergyUse, setTotalEnergyUse)}
        />
      {powerPlantsData.features.map((feature, index) => (
        <Marker
          key={index}
          position={[feature.geometry.coordinates[1], feature.geometry.coordinates[0]]}
          icon={customIcon}
        >
          <Popup>
              <div>
              {feature.properties.Name}
              <br/>
              Total Capacity (MW): {feature.properties['Total Capacity (MW)']}
              <br/>
              Active Production: {feature.properties['Active Production']}
              </div>
          </Popup>
        </Marker>
      ))}
      </MapContainer>
      </div>
      <div className="power-plants-statistics">
        <div className="total-energy-use">Total energy usage in selected regions: {totalEnergyUse} kWh</div>
          <div>{powerPlantsData.features.map((feature, index) => {
                const currentOutput = parseFloat(feature.properties['Active Production']);
                const previousFeature = previousPowerOutputs.features.find(prevFeature => prevFeature.properties.Name === feature.properties.Name);
                const previousOutput = previousFeature ? parseFloat(previousFeature.properties['Active Production']) : 0;

                const change = currentOutput - previousOutput;
                

                return (
                  <div key={index}>
                    <h4>{feature.properties.Name}</h4>
                    <input
                      type="range"
                      min="0"
                      max={feature.properties['Total Capacity (MW)']}
                      value={sliderValues[feature.properties.Name]}
                      onChange={(event) => handleSliderChange(event, feature.properties.Name)}
                    />
                    <div>
                      Current running capacity: {((currentOutput / feature.properties['Total Capacity (MW)']) * 100).toFixed(2)} %  
                      <br/> 
                      Surplus: {change >= 0 ? `+${change.toFixed(2)}` : change.toFixed(2)} MWh
                    </div>
                  </div>
                );
              })}
            </div>
      </div>
    </div>  
  );
}

export default EnergyUsageMap;
