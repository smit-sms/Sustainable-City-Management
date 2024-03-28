import React from 'react';
import { useState,useEffect,useMemo, useRef } from 'react'
import '../assets/styles/style_leaflet.css'
import { MapContainer,Marker, Popup, TileLayer, GeoJSON } from 'react-leaflet';
import "leaflet/dist/leaflet.css";
import { Icon , L} from 'leaflet';
import customIconImage1 from '../assets/noise1.png';
import customIconImage2 from '../assets/noise2.png';
import customIconImage3 from '../assets/noise3.png';
import customIconImage4 from '../assets/noise4.png';
import customIconImage5 from '../assets/noise5.png';
import customIconImage6 from '../assets/noise6.png';
import customIconImage7 from '../assets/noise7.png';
import customIconImage8 from '../assets/noise8.png';

function NoisePollutionMap(){
    const [sensors,Setsensors]=useState([]);

  
    const customIcon1= new Icon({
        iconUrl: customIconImage1,
        iconSize: [20, 20]
      })

      const customIcon2 = new Icon({
        iconUrl: customIconImage2,
        iconSize: [20, 20]
      })
      const customIcon3 = new Icon({
        iconUrl: customIconImage3,
        iconSize: [20, 20]
      })
      const customIcon4 = new Icon({
        iconUrl: customIconImage4,
        iconSize: [20, 20]
      })
      const customIcon5 = new Icon({
        iconUrl: customIconImage5,
        iconSize: [20, 20]
      })
      const customIcon6 = new Icon({
        iconUrl: customIconImage6,
        iconSize: [20, 20]
      })
      const customIcon7 = new Icon({
        iconUrl: customIconImage7,
        iconSize: [20, 20]
      })
      const customIcon8 = new Icon({
        iconUrl: customIconImage8,
        iconSize: [20, 20]
      })

    const getsensors = () =>{
    fetch('http://127.0.0.1:8000/sensors/air-noise').then((response) => response.json()).then((json) =>{ 
      Setsensors(json.data);
    }
      );}
    
      useEffect(()=>{
        getsensors();
        //const intervalId = setInterval(getsensors, 10000);
        //return () => clearInterval(intervalId);
    },
    []);

    function filtersensors(sensor){
    let new_sensor=[];
    for (let i =0;i<sensor.length;i++){
        if (sensor[i].sensor_type=="noise"){
            new_sensor.push(sensor[i]);
        }
        
    }
    return new_sensor;
    }

    let sensors_show=filtersensors(sensors);
    
    function getColor(d) {
      return d > 70 ? customIcon8 :
             d > 65 ? customIcon7 :
             d > 60 ? customIcon6 :
             d > 55 ? customIcon5 :
             d > 50 ? customIcon4 :
             d > 45 ? customIcon3 :
             d > 40 ? customIcon2 :
             customIcon1;
    };

      const RenderIcons = () => {
       
      
        const eventHandlers = useMemo(
          () => ({
            mouseover() {
 
              this.openPopup();
            },
            mouseout() {
         
              this.closePopup();
             
            }
          })
        ); 

        return (
          
          sensors_show.map((feature, index) => (
            <Marker
              key={index}
              position={[(feature.latitude),(feature.longitude)]}
              icon={getColor(feature.value)}
              eventHandlers={eventHandlers}
            >
              <Popup>
                  <div>
                   Station ID
                  <br/>
                  {feature.serial_number}
                  <br/>
                  Noise 
                  <br/>
                  {feature.value} LAeq
                  </div>
              </Popup>
            </Marker>
          ))
        );
      };


return(



   
    <div>
       
      <MapContainer center={[53.35442, -6.24896]} zoom={12} >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
    <RenderIcons />
    </MapContainer>
  </div>
);
}


export default NoisePollutionMap;
