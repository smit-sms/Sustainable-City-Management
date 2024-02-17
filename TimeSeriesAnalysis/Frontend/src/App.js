import { useEffect, useState } from "react";
import TSDashboard from "./components/TSDashboard";

const App = () => {

    const [data, setData] = useState({data:[], time:[]});

    const fetchData = () => {
        fetch('http://127.0.0.1:8000/sensors/pm2.5/?sensor_serial_number=DCC-AQ2')
        .then(response => response.json())
        .then(response => {
            let dataFetched = {data: [], time: []}
            response['data'].forEach(dt => {
                dataFetched.data.push(dt.pm2_5);
                dataFetched.time.push(dt.datetime);
            })
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
                <TSDashboard 
                    title={"Air Pollution (PM2.5) (Sensor = DCC-AQ2)"}
                    data={data} 
                    frequency={"15min"}
                    period={20}
                    lags={24} 
                /> : <></>
            }
        </div>
    );
}

export default App;
