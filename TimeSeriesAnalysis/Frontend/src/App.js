import { useEffect, useState } from "react";
import TSADashboard from "./components/TSADashboard";

// // Air Data
// const dataName = "pm2_5"
// const sensorType = "pm2.5"
// const sensorNumber = "DCC-AQ2"
// const title = `Air Pollution (${sensorType}) (Sensor = ${sensorNumber})`

// Noise Data
const dataName = "laeq"
const sensorType = "laeq"
const sensorNumber = "10.1.1.1"
const title = `Noise Pollution (${sensorType}) (Sensor = ${sensorNumber})`

const App = () => {

    const [data, setData] = useState({data:[], time:[]});

    const fetchData = () => {
        fetch(`http://127.0.0.1:8000/sensors/${sensorType}/?sensor_serial_number=${sensorNumber}&time_start=2024-02-01 00:00:00&time_end=2024-02-02 00:00:00`)
        .then(response => response.json())
        .then(response => {
            let dataFetched = {data: [], time: []}
            response['data'].forEach(dt => {
                dataFetched.data.push(dt[dataName]);
                dataFetched.time.push(dt.datetime);
            })
            // Adding outliers.
            // dataFetched.data[10] = 50 
            dataFetched.data[5] = -10;
            setData(dataFetched);
        });
    }

    useEffect(() => {
        fetchData();
    }, [])

    return (
        <div className="App">
            {
                data.data.length > 0 ? 
                <TSADashboard 
                    title={title}
                    data={data} 
                    frequency={"15min"}
                    period={8}
                    lags={10}
                    backend_url_root='http://127.0.0.1:8001'
                /> : <></>
            }
        </div>
    );
}

export default App;
