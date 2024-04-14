import {TSADashboard } from '../components/TSADashboard';
// import { TSADashboard } from "tsa-dashboard";

const title = "Bike Usage (Station 32)";
const dummyData = [
    {
        "id": 3785,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 9,
        "usage_percent": 1.0,
        "last_update": "2024-03-26T13:29:20Z",
        "status": "open"
    },
    {
        "id": 3899,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 10,
        "usage_percent": 0.9,
        "last_update": "2024-03-26T13:43:33Z",
        "status": "open"
    },
    {
        "id": 4080,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 10,
        "usage_percent": 0.33,
        "last_update": "2024-03-26T14:03:43Z",
        "status": "open"
    },
    {
        "id": 4177,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 10,
        "usage_percent": 0.33,
        "last_update": "2024-03-26T14:13:49Z",
        "status": "open"
    },
    {
        "id": 4310,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 9,
        "usage_percent": 0.3,
        "last_update": "2024-03-26T14:23:56Z",
        "status": "open"
    },
    {
        "id": 4382,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 10,
        "usage_percent": 0.33,
        "last_update": "2024-03-26T14:25:39Z",
        "status": "open"
    },
    {
        "id": 4445,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 11,
        "usage_percent": 0.37,
        "last_update": "2024-03-26T14:34:02Z",
        "status": "open"
    },
    {
        "id": 4587,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 10,
        "usage_percent": 0.33,
        "last_update": "2024-03-26T14:44:09Z",
        "status": "open"
    },
    {
        "id": 4723,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 13,
        "usage_percent": 0.43,
        "last_update": "2024-03-26T14:54:17Z",
        "status": "open"
    },
    {
        "id": 4658,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 12,
        "usage_percent": 0.4,
        "last_update": "2024-03-26T14:49:09Z",
        "status": "open"
    },
    {
        "id": 4808,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 9,
        "usage_percent": 0.3,
        "last_update": "2024-03-26T15:04:27Z",
        "status": "open"
    },
    {
        "id": 4919,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 9,
        "usage_percent": 0.3,
        "last_update": "2024-03-26T15:07:43Z",
        "status": "open"
    },
    {
        "id": 4989,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 8,
        "usage_percent": 0.27,
        "last_update": "2024-03-26T15:13:51Z",
        "status": "open"
    },
    {
        "id": 5067,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 8,
        "usage_percent": 0.27,
        "last_update": "2024-03-26T15:14:35Z",
        "status": "open"
    },
    {
        "id": 5149,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 8,
        "usage_percent": 0.27,
        "last_update": "2024-03-26T15:24:40Z",
        "status": "open"
    },
    {
        "id": 5263,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 8,
        "usage_percent": 0.27,
        "last_update": "2024-03-26T15:43:36Z",
        "status": "open"
    },
    {
        "id": 5372,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 9,
        "usage_percent": 0.3,
        "last_update": "2024-03-26T15:47:08Z",
        "status": "open"
    },
    {
        "id": 5519,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 11,
        "usage_percent": 0.37,
        "last_update": "2024-03-26T15:55:00Z",
        "status": "open"
    },
    {
        "id": 5448,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 11,
        "usage_percent": 0.37,
        "last_update": "2024-03-26T15:53:37Z",
        "status": "open"
    },
    {
        "id": 5609,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 13,
        "usage_percent": 0.43,
        "last_update": "2024-03-26T16:08:51Z",
        "status": "open"
    },
    {
        "id": 5709,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 16,
        "usage_percent": 0.53,
        "last_update": "2024-03-26T16:14:20Z",
        "status": "open"
    },
    {
        "id": 5779,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 16,
        "usage_percent": 0.53,
        "last_update": "2024-03-26T16:16:26Z",
        "status": "open"
    },
    {
        "id": 5861,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 16,
        "usage_percent": 0.53,
        "last_update": "2024-03-26T16:23:44Z",
        "status": "open"
    },
    {
        "id": 5940,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 16,
        "usage_percent": 0.53,
        "last_update": "2024-03-26T16:25:36Z",
        "status": "open"
    },
    {
        "id": 6023,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 17,
        "usage_percent": 0.57,
        "last_update": "2024-03-26T16:34:00Z",
        "status": "open"
    },
    {
        "id": 6098,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 16,
        "usage_percent": 0.53,
        "last_update": "2024-03-26T16:39:25Z",
        "status": "open"
    },
    {
        "id": 6185,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 15,
        "usage_percent": 0.5,
        "last_update": "2024-03-26T16:43:48Z",
        "status": "open"
    },
    {
        "id": 6267,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 17,
        "usage_percent": 0.57,
        "last_update": "2024-03-26T16:46:40Z",
        "status": "open"
    },
    {
        "id": 6357,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 18,
        "usage_percent": 0.6,
        "last_update": "2024-03-26T16:51:25Z",
        "status": "open"
    },
    {
        "id": 6441,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 18,
        "usage_percent": 0.6,
        "last_update": "2024-03-26T16:55:40Z",
        "status": "open"
    },
    {
        "id": 6534,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 21,
        "usage_percent": 0.7,
        "last_update": "2024-03-26T17:04:04Z",
        "status": "open"
    },
    {
        "id": 6618,
        "station_id": 32,
        "bike_stands": 30,
        "available_bikes": 21,
        "usage_percent": 0.7,
        "last_update": "2024-03-26T17:06:56Z",
        "status": "open"
    }
]

let data = {'data':[], 'time':[]};
dummyData.forEach(d => {
    data.data.push(d.usage_percent)
    let time = d.last_update
    time = time.replace("T", " ")
    time = time.replace("Z", "")
    data.time.push(time)
});

export default {
    title: 'Example/TSADashboard',
    component: TSADashboard,
    parameters: {
        layout: 'centered',
    },
};

export const Primary = {
    args: {
        title: title,
        data: data,
        frequency: "10min",
        period: 8,
        lags: 10,
        backend_url_root: 'http://127.0.0.1:8001',
    }
};