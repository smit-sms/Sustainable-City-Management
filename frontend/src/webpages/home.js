import React, { useState, useEffect }  from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [thinslices, setThinSlices] = useState([]);
    useEffect(() => {
        fetch("http://127.0.0.1:8000/thinslice/")
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
            <ul>
                {thinslices.map((thinslice, i) => (
                    <div className={"row"} key={i} id={i}>
                        <li>
                            <Link to={`thinslice/${thinslice.id}`}>{thinslice.firstname}</Link>
                        </li>
                    </div>
                ))}
            </ul>
        );
    }
}

export default Home;
