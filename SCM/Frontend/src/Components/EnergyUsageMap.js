import React from 'react';
import { Component, useState } from 'react'
import '../assets/styles/EnergyUsageMap.css'
import { MapContainer, Marker, Popup, TileLayer, useMap, GeoJSON, layer  } from 'react-leaflet';
import "leaflet/dist/leaflet.css";
import countries from "../assets/area.json";


function Style(countries) {
    return {
      fillColor: getColor(countries.properties.Estimated_Annual_Cost),
      fillOpacity: 0.6
    }  
  };

function getColor(d) {
    return d > 300000 ? '#800026' :
           d > 250000  ? '#BD0026' :
           d > 200000  ? '#E31A1C' :
           d > 150000  ? '#FC4E2A' :
           d > 50   ? '#FD8D3C' :
           d > 20   ? '#FEB24C' :
           d > 10   ? '#FED976' :
                      '#FFEDA0';
 }


function onEachCountry(countries, layer) {
    const name = countries.properties.Local_Electorial_Area_name;
    const Energy_Use = countries.properties['Estimated_Annual_EnergyUse(kWh)'];
    const Cost_Of_Energy = countries.properties.Estimated_Annual_Cost;
    layer.bindPopup(`<div class="pop" >
    Name:  ${name}
    <br/>
    Energy_Use:${Energy_Use}(kWh)
    <br/>
    Cost_Of_Energy:${Cost_Of_Energy}
    </div>
    `)
    ;
  }

  function EnergyUsageMap() {
    return (
      <div>
        <MapContainer  center={[ 53.34442,-6.25896]} zoom={13}>
           <TileLayer
         attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
         url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
         />
          <GeoJSON 
              style ={Style}
              data={countries.features}
              onEachFeature={onEachCountry}
          />
        </MapContainer >
      </div>
    )
  }

export default EnergyUsageMap;
