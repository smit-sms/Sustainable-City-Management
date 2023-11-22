import React from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes
} from "react-router-dom";
import Home from './home';
import ThinSlice from './thinslice';

const Webpages = () => {
    return(
        <Router>
            <Routes>
                <Route exact path="/" element={<Home/>} />
                <Route path = "/thinslice/:id" element = {<ThinSlice/>} />
            </Routes>
        </Router>
    );
};

export default Webpages;
