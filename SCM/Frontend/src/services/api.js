// Define all the urls here
const BASE_URL = process.env.REACT_APP_BACKEND_URL;
const MET_WEATHER_URL = 'https://prodapi.metweb.ie/observations/dublin/today';
const DUBLIN_BIKE_API_URL = `https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=${process.env.REACT_APP_DUBLIN_BIKE_API_KEY}`;
const DUBLIN_WASTE_FACILITIES = 'https://gis.epa.ie/geoserver/EPA/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=EPA:LEMA_Facilities_Waste&maxFeatures=50&outputFormat=application%2Fjson&srsName=EPSG:4326';

export { BASE_URL, MET_WEATHER_URL, DUBLIN_BIKE_API_URL, DUBLIN_WASTE_FACILITIES };
