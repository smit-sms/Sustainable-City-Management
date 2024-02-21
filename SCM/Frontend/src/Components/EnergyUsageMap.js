import React from 'react';
import { useState } from 'react'
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

function EnergyUsageMap() {
  const [totalEnergyUse, setTotalEnergyUse] = useState(0);
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
        Energy_Use: ${Energy_Use}(kWh)
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
      <div class="total-energy-use">Total energy use {totalEnergyUse}(kWh)</div>
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
      {powerPlants.features.map((feature, index) => (
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
  );
}

export default EnergyUsageMap;
