import L from 'leaflet';
import ReactDOMServer from 'react-dom/server';
import { IconContext } from 'react-icons';
import { FaWind } from 'react-icons/fa'; // Import the wind icon

export const customReactIcon = (IconComponent, color, fontsize='22px') => {
  const iconHtml = ReactDOMServer.renderToString(
    <IconContext.Provider value={{ className: "react-leaflet-icon", color:color, style: {fontSize: fontsize}}}>
      <IconComponent />
    </IconContext.Provider>
  );

  return L.divIcon({
    className: 'custom-icon',
    html: iconHtml
  });
};


// Not working properly: attention needed
export const createReactIcon = (IconComponent, iconColor = 'red', pinColor = '#2A81CB', size = '30px') => {
  // Render the icon to a string
  const iconHtml = ReactDOMServer.renderToString(
    <IconComponent color={iconColor} size='10' />
  );

  // Create an SVG string for the marker with the icon inside
  const svgHtml = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 24 24">
      <path fill="${pinColor}" d="M12 2C8.13 2 5 5.13 5 9c0 5 7 13 7 13s7-8 7-13c0-3.87-3.13-7-7-7z"/>
      ${iconHtml}
    </svg>
  `;

  // Create a Leaflet divIcon with the SVG string
  return L.divIcon({
    className: 'custom-leaflet-icon',
    html: svgHtml,
    iconSize: L.point(30, 30), // Adjust size as needed
    iconAnchor: L.point(40, 40) // Adjust the anchor as needed
  });
};
