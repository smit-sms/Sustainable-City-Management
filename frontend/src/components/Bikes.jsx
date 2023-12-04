import React, { useEffect, useState } from 'react'
import { API_BIKES } from '../webpages/api'

const Bikes = () => {
    const [bikes, setBikes] = useState([]);
    const [showBikes, setShowBikes] = useState(false);

    const fetchData = () => {
        fetch(API_BIKES)
            .then(res => res.json())
            .then((data) => {
                const bikes = data.map((item) => (
                    <p key={item.number}>{JSON.stringify(item)}</p>
                ));
                console.log('BIKES = ', bikes);
                setBikes(bikes);
            }
        );
    }

    const handleClick = () => {
        fetchData();
        setShowBikes((prevVal) => {
            return !prevVal
        });
    }

    return (
        <div>
            <button onClick={handleClick}>
                Toggle Bike Data
            </button>
            <div>{showBikes && bikes}</div>
        </div>
    )
}

export default Bikes