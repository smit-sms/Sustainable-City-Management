import { useEffect, useState } from "react";
import { BASE_URL } from "../services/api";
import { TSADashboard } from "tsa-dashboard";
import { useLocation } from 'react-router-dom';

const TimeSeriesAnalysis = () => {
    let data = {'data':[], 'time':[]};

    const location = useLocation();
    let search_params = location.search.replace("?", "")
    search_params = search_params.split("_")
    const [dispData, setDispData] = useState(data)
    const [title, setTitle] = useState('')
    
    if (search_params.length < 2) {
        search_params = ["air", "DCC-AQ2"]
    }

    const fetchData = async () => {
        const datetimeNow = new Date();
        const datetimeYesterday = new Date(datetimeNow);
        datetimeYesterday.setDate(datetimeNow.getDate() - 1);
        const url = `${BASE_URL}/sensors/${search_params[0] == "air" ? "pm2.5" : "laeq"}/`;
        // const monitor = id; // "DCC-AQ2";
        const monitor = search_params[1];
        const body = {sensor_serial_number: monitor};
        fetch(url, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(body)
        }).then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        }).then(data => {
            const data_fetched = data.data; // Use the response data as needed
            let data_processed = {'data':[], 'time':[]};
            data_fetched.forEach(d => {
                data_processed.time.push(d.datetime)
                data_processed.data.push(d.pm2_5)
            });
            setTitle(monitor);
            setDispData(data_processed);
        }).catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
    }
    
    useEffect(() => {
        fetchData();
    }, [])

    return (
        <div className="App">
            {
                dispData.data.length > 0 ? 
                <TSADashboard 
                    title={`${search_params[0] == "air" ? "Air" : "Noise"} Sensor: ${title}`}
                    data={dispData} 
                    frequency={"5min"}
                    period={8}
                    lags={10}
                    backend_url_root={BASE_URL}
                /> : <>Time Series Dashboard</>
            }
        </div>
    );
}

export default TimeSeriesAnalysis;
