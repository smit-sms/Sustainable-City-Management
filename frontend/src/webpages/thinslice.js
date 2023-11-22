import React, { useState, useEffect }  from 'react';
import { useParams } from 'react-router-dom';

const ThinSlice = () => {
    const params = useParams();
    var id = params.id;
    const [error, setError] = useState(null);
    const [isLoaded, setIsLoaded] = useState(false);
    const [thinsliceobj, setThinSlice] = useState([]);

    useEffect(() => {
        fetch("http://127.0.0.1:8000/thinslice/" + id)
            .then(res => res.json())
            .then(
                (data) => {
                    setIsLoaded(true);
                    setThinSlice(data);
                },
                (error) => {
                    setIsLoaded(true);
                    setError(error);
                }
            )
    }, [id])
    if (error) {
        return <div>Error: {error.message}</div>;
    }
    if (!isLoaded) {
        return <div>Loading...</div>;
    }
    if (thinsliceobj) {
        return (
            <div>
                <h1>{thinsliceobj.id}</h1>
                <div>
                    Firstname: {thinsliceobj.firstname}
                </div>
                <div>
                    Lastname: {thinsliceobj.lastname}
                </div>
          </div>
        );
    }
}

export default ThinSlice;
