import React, { useState, useEffect }  from 'react';
import { Link } from 'react-router-dom';
import { API_URL } from './api';

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
        return (
            <div>
                <h1>
                    Sustainable City Management - ThinSlice
                </h1>
                <div>Error: {error.message}</div>
            </div>
        );
    } else if (!isLoaded) {
        return <div>Loading...</div>;
    } else {
        return (
            <div>
                <h1>
                    Sustainable City Management - ThinSlice
                </h1>
                <ul>
                    {thinslices.map((thinslice, i) => (
                        <div className={"row"} key={i} id={i}>
                            <li>
                                <Link to={`thinslice/${thinslice.id}`}>{thinslice.firstname}</Link>
                            </li>
                        </div>
                    ))}
                </ul>
            </div>
        );
    }
}

export default Home;
