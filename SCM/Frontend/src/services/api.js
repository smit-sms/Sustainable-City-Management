// Define all the urls here
const BASE_URL = 'http://localhost:8000'
const MET_WEATHER_URL = 'https://prodapi.metweb.ie/observations/dublin/today'
const DUBLIN_BIKE_API_URL = `https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=${process.env.REACT_APP_DUBLIN_BIKE_API_KEY}`

export { BASE_URL, MET_WEATHER_URL, DUBLIN_BIKE_API_URL };