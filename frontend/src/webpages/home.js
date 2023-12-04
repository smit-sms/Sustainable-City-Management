import React, { useState, useEffect }  from 'react';
import { Link } from 'react-router-dom';
import { API_URL } from './api';
import Bikes from '../components/Bikes';

const Home = () => {
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [thinslices, setThinSlices] = useState([]);
    useEffect(() => {
        fetch(API_URL)
            .then(res => res.json())
            .then(
                (data) => {
                    console.log(data);
                    setIsLoaded(true);
                    setThinSlices(data);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
      }, [])
    if (error) {
        return <div>Error: {error.message}</div>;
    } else if (!isLoaded) {
        return <div>Loading...</div>;
    } else {
        return (
            <>
                {/* List of items from PgSQL DB. */}
                <ul>
                    {thinslices.map((thinslice, i) => (
                        <div className={"row"} key={i} id={i}>
                            <li>
                                <Link to={`thinslice/${thinslice.id}`}>{thinslice.firstname}</Link>
                            </li>
                        </div>
                    ))}
                </ul>
                {/* Data from DubLinked API. */}
                <div>
                    <h1>Bike Data</h1>
                    <Bikes />
                </div>
            </>  
        );
    }
}

export default Home;
