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
function updateActiveProduction(powerPlants, weatherData) {
  const windSpeed = weatherData.windSpeed;
  const weatherDescription = weatherData.weatherDescription;
  const rainfall = weatherData.rainfall;
  
  
    // Assuming the 'Type' property is available in your powerPlants.features data
    return powerPlants.features.map((feature) => {
      let newProduction = feature.properties['Active Production'];
  
      // Adjust production for wind farms based on wind speed
      if (feature.properties.Name === 'Wind Farm') {
        let increaseFactor = 1;
        if (windSpeed > 20) {
          increaseFactor = 1.2;
        } else if (windSpeed > 10) {
          increaseFactor = 1.1;
        } else {
          increaseFactor = 1.05;
        }
        newProduction *= increaseFactor;
      }
  
      // Adjust production for solar plants based on clear skies
      if (feature.properties.Name === 'Solar Plant' && weatherDescription.includes('Sun / Clear sky')) {
        newProduction *= 1.1; // An Estimated increase factor for clear skies (Dummy for project)
      }
  
      // Adjust production for hydroelectric plants based on rainfall
      if (feature.properties.Name === 'Hydroelectric power plant' && rainfall > 5) { 
        newProduction *= 1.1; //An Estimated increase factor for heavy rainfall (Dummy for project)
      }
  
      // Make sure not to exceed the total capacity
      newProduction = Math.min(newProduction, feature.properties['Total Capacity (MW)']);
  
      return {
        ...feature,
        properties: {
          ...feature.properties,
          'Active Production': newProduction.toFixed(2)
        }
      }; // Return the updated power plants data
});
}


function EnergyUsageMap() {
  const [totalEnergyUse, setTotalEnergyUse] = useState(0);
  const [powerPlantsData, setPowerPlantsData] = useState(powerPlants);
  const [weatherData, setWeatherData] = useState(null);
  
  // Function to fetch weather data
  const fetchWeatherData = async () => {
    try {
      const response = await fetch('https://prodapi.metweb.ie/observations/dublin/today');
      const data = await response.json();
      setWeatherData(data);

      //based on the weather changes estimate the changes in power output
      const latestWeatherData = data[data.length - 1];
      const updatedPowerPlants = updateActiveProduction(powerPlants, latestWeatherData);
      setPowerPlantsData({ ...powerPlantsData, features: updatedPowerPlants });
      
    } catch (error) {
      console.error("Failed to fetch weather data", error);
    }
    
  };

   // Effect hook to fetch weather data at component mount and every hour
  useEffect(() => {
    fetchWeatherData(); // Fetch immediately on mount
    const intervalId = setInterval(fetchWeatherData, 3600000); // Refresh every hour (3600000 ms)

    return () => clearInterval(intervalId); 
  }, []);

  useEffect(() => {
    // This will run whenever powerPlantsData changes, including after fetchWeatherData and updates the slider values
    setSliderValues(
      powerPlantsData.features.reduce((acc, feature) => {
        acc[feature.properties.Name] = feature.properties['Active Production'];
        return acc;
      }, {})
    );
  }, [powerPlantsData]); // The effect depends on powerPlantsData
  
  
  // State to keep track of the slider values corresponding to power plants power production
  const [sliderValues, setSliderValues] = useState(
    powerPlantsData.features.reduce((acc, feature) => {
      acc[feature.properties.Name] = feature.properties['Active Production'];
      return acc;
    }, {})
  );

  const handleSliderChange = (event, plantName) => {
    const newProductionValue = parseFloat(event.target.value);
    let newSliderValues = { ...sliderValues, [plantName]: newProductionValue };
  
    // Calculate the total required energy, ensuring that each value is a number.
    const totalEnergyReq = powerPlants.features.reduce((total, feature) => {
      const production = parseFloat(feature.properties['Active Production']);
      return total + (isNaN(production) ? 0 : production);
    }, 0);
  
    // Calculate the new total energy use from the slider values.
    const newTotalEnergyUse = Object.values(newSliderValues).reduce((total, current) => {
      const currentValue = parseFloat(current);
      return total + (isNaN(currentValue) ? 0 : currentValue);
    }, 0);
  
    const newSurplus = newTotalEnergyUse - totalEnergyReq;

    if (newSurplus >= 0) {
      setSliderValues(newSliderValues);
      const updatedFeatures = powerPlantsData.features.map(feature => {
        if (feature.properties.Name === plantName) {
          return {
            ...feature,
            properties: {
              ...feature.properties,
              'Active Production': newProductionValue
            }
          };
        }
        return feature;
      });

      setPowerPlantsData({ ...powerPlantsData, features: updatedFeatures });
    } else {
      // If the surplus is negative, prevent the slider from moving and alert the user
      alert('Unable to adjust production as it would result in a negative energy surplus.');
    }
  };
  
  const customIcon = new Icon({
    iconUrl: customIconImage,
    iconSize: [20, 20]
  })

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
     <div>
          {/* Displaying weather data */}
           {weatherData && weatherData.length > 0 && (
            <div >
              <h3 className='weatherData'>Latest weather statistics:</h3>
              <p> <b>Weather Description:</b> {weatherData[weatherData.length - 1].weatherDescription}  <b>Wind Speed:</b> {weatherData[weatherData.length - 1].windSpeed} <b>Rainfall:</b>  {weatherData[weatherData.length - 1].rainfall}</p>
            </div>
          )}
        <div className="total-energy-use">Total energy usage in selected regions: {totalEnergyUse} kWh</div>
          <div className="map-and-list-container">
            <div className='map-container'>
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
                <div>{powerPlantsData.features.map((feature, index) => {
                      const currentOutput = parseFloat(feature.properties['Active Production']);
                      const previousFeature = powerPlants.features.find(prevFeature => prevFeature.properties.Name === feature.properties.Name);
                      const previousOutput = previousFeature ? parseFloat(previousFeature.properties['Active Production']) : 0;                
                      const change = currentOutput - previousOutput;
                      return (
                        <div key={index}>
                          <h4><b>{feature.properties.Name}</b></h4>
                          <input
                            type="range"
                            min="0"
                            max={feature.properties['Total Capacity (MW)']}
                            value={feature.properties['Active Production']}
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
     </div>  
  );
}

export default EnergyUsageMap;
