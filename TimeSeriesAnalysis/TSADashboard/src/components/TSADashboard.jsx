import * as d3 from "d3";
import TextBox from './TextBox.jsx';
import RadioButton from './RadioButton.jsx';
import React, { useEffect, useState } from 'react';
import { FaInfoCircle } from "react-icons/fa";
import { Tooltip } from 'react-tooltip'

let controls = {
    freq: 'None',
    period: 0,
    lags: 1,
    bins: 10,
    outliers: false,
    decomposition_type: 'additive'
}

let feedback = "";

let dataProcessed = {
    base:[], time_base: [], trend:[], 
    seasonal:[], time_decomposed:[], 
    residual:[], stationary: [], time_stationary: [],
    acf:[], pacf:[], corr_ci:[], corr_lags:[] 
}

let outliers = [];

const isNumeric = (str) => {
    /** Returns true if the string is a number and false otherwise. */
    return !isNaN(str);
}

const roundToNPlaces = (num, n) => {
    /** Rounds a given number num to n decimal places. */
    return Math.round((num + Number.EPSILON) * (10**n)) / (10**n)
}

export const TSADashboard = ({ 
    data, frequency, period, lags, title, backend_url_root
}) => {
    const [selectedLineType, setSelectedLineType] = useState('base');
    const [statusMessage, setStatusMessage] = useState("");
    const [stateDataProcessed, setStateDataProcessed] = useState({
        base:[], time_base: [], trend:[], 
        seasonal:[], time_decomposed:[], 
        residual:[], stationary: [], time_stationary: [],
        acf:[], pacf:[], corr_ci:[], corr_lags:[],
        num_diff: 0,
    });
    const [numSum, setNumSum] = useState({
        'mean': 0, 'median': 0, 'iqr': 0,
        'q1': 0, 'q3': 0, 'num_outliers':0, 
        'max': 0, 'min': 0
    })

    const handleTextBoxChange = (id) => {
        feedback = "";
        const textBox = d3.select(`#${id}`).select('input');
        const textBoxType = id.split('-')[2];
        const val = textBox.property("value");
        if (sanityCheckControls(textBoxType, val)) {
            if (textBoxType == 'freq') controls[textBoxType] = val;
            if (textBoxType == 'period' || textBoxType == 'lags' || textBoxType == 'bins') controls[textBoxType] = parseInt(val);  
            textBox.attr('style', 'border: 2px solid green');
        } else {
            if (textBoxType == 'freq') controls.freq = frequency;
            if (textBoxType == 'period') controls.period = period;
            if (textBoxType == 'lags') controls.lags = lags;
            if (textBoxType == 'bins') controls.bins = Math.max(1, Math.floor(dataProcessed.time_decomposed.length/2));
            textBox.attr('style', 'border: 2px solid red');
        }
    }
    
    const handleChkBoxChange = (e) => {
        controls.outliers = !controls.outliers;
        handleApply();
    }

    const handleApply = (e) => {
        feedback = "";
        ['freq', 'period', 'lags', 'bins'].forEach(tb => {
            d3.select(`#text-box-${tb}`).select('input').property("value", "").attr('style', 'border:none');
        });
        // Update data.
        updateDataProcessed();
    }

    const sanityCheckControls = (textBoxType, val) => {
        if (textBoxType == 'freq') {
            return typeof val == String && 
                val.length > 0 && val.slice(0, 1) != 0
        }

        if (textBoxType == 'period' || textBoxType == 'lags') {
            return isNumeric(val) && Number.isInteger(Number(val)) &&
            val > 0 && val <= Math.floor(stateDataProcessed.time_decomposed.length/2);
        }

        if (textBoxType == 'bins') {
            return isNumeric(val) && Number.isInteger(Number(val)) &&
            val <= stateDataProcessed.time_decomposed.length && val > 0
        }
        return false
    }

    const handleLineTypeSelection = (e) => {
        const value = e.currentTarget.value;
        setSelectedLineType(prevVal => value);
    }

    const updateDataProcessed = async () => {
        dataProcessed = {
            base:[], time_base: [], trend:[], 
            seasonal:[], time_decomposed:[], 
            residual:[], stationary: [], time_stationary: [],
            acf:[], pacf:[], corr_ci:[], corr_lags:[], num_diff:0
        }

        // Base data.
        let d;
        let t;
        console.log(`controls.outliers = ${controls.outliers}`)
        if (controls.outliers) { // Include outliers.
            dataProcessed.base = [];
            dataProcessed.time_base = [];
            for (let i=0; i<data.data.length; i++) {
                d = data.data[i];
                t = data.time[i];
                dataProcessed.base.push(parseFloat(d));
                dataProcessed.time_base.push(t);
            }
        } else { // Exclude outliers.
            dataProcessed.base = [];
            dataProcessed.time_base = [];
            for (let i=0; i<data.data.length; i++) {
                d = data.data[i];
                t = data.time[i];
                if (!outliers.includes(d)) {
                    dataProcessed.base.push(parseFloat(d));
                    dataProcessed.time_base.push(t);
                }   
            }
        }

        // Sort data and time based on time.
        let data_time = dataProcessed.time_base.map((time, index) => ({
            time: time,
            value: dataProcessed.base[index]
        }));

        data_time.sort((a, b) => new Date(a.time) - new Date(b.time));
        dataProcessed.base = data_time.map(item => item.value);
        dataProcessed.time_base = data_time.map(item => item.time);

        // Decompose data into trend, seasonal and residual components.
        let decomposed = await fetch(`${backend_url_root}/tsa/decompose/`, {
            method: 'POST',
            body: JSON.stringify({"data": {
                data: dataProcessed.base,
                time: dataProcessed.time_base
            }, "freq": controls.freq, "period": controls.period, "model_type": controls.decomposition_type}),
            headers: {'Content-Type':'application/json'}
        })
        decomposed = await decomposed.json();
        if (decomposed.message.includes('Failure')) {
            feedback += " Decomposition: " + decomposed.message;
        }
        decomposed = decomposed.data;
        dataProcessed.time_decomposed = decomposed.time;
        dataProcessed.trend = decomposed.trend;
        dataProcessed.seasonal = decomposed.seasonal;
        dataProcessed.residual = decomposed.residual;

        // Check stationarity and do decomposition (multiple times
        // if required) to make data stationary.
        let dataStationary = {
            data: dataProcessed.base,
            time: dataProcessed.time_base
        };
        let stationarity;
        let diff;
        while (true) {
            // Check data stationarity.
            stationarity = await fetch(`${backend_url_root}/tsa/stationarity/`, {
                method: 'POST',
                body: JSON.stringify({"data": dataStationary.data}),
                headers: {'Content-Type':'application/json'}
            });
            stationarity = await stationarity.json();
            if (stationarity.message.includes('Failure')) {
                feedback += " Stationarity Check: " + stationarity.message;
                break; // If there was a failure, exit loop.
            }
            if (stationarity.data.is_stationary == 1) break; // If stationary, exit loop.
            else {  // If not stationary, make stationary by differencing.
                diff = await fetch(`${backend_url_root}/tsa/first_difference/`, {
                    method: 'POST',
                    body: JSON.stringify({"data": dataStationary, "freq": controls.freq}),
                    headers: {'Content-Type':'application/json'}
                });
                diff = await diff.json();
                if (diff.message.includes('Failure')) {
                    feedback += " Differencing: " +diff.message;
                    break;
                }
                dataStationary = diff.data;
                dataProcessed.num_diff += 1;
            }
        }
        dataProcessed.stationary = dataStationary.data;
        dataProcessed.time_stationary = dataStationary.time;

        // Get Autocorrelation and Partial Autocorrelation information.
        let correlations = await fetch(`${backend_url_root}/tsa/correlation/`, {
            method: 'POST',
            body: JSON.stringify({"data": {
                data: dataProcessed.base,
                time: dataProcessed.time_base
            }, "freq": controls.freq, "lags": controls.lags}),
            headers: {'Content-Type':'application/json'}
        })
        correlations = await correlations.json();
        if (correlations.message.includes('Failure')) {
            feedback += " ACF & PACF: " + correlations.message;
        }
        correlations = correlations.data;
        dataProcessed.acf = correlations.autocorrelation;
        dataProcessed.pacf = correlations.partial_autocorrelation;
        dataProcessed.corr_lags = correlations.lag;
        dataProcessed.corr_ci = correlations.confidence_interval;
        
        // Reset system feedback to user.
        if (feedback.length > 0) {
            setStatusMessage(feedback);
            setTimeout(() => setStatusMessage(prevVal => ""), 8000);
        }

        // Trigger plot updates.
        setStateDataProcessed(prevVal => dataProcessed);
    }

    const plotLineData = () => {
        // Get appropriate x axis and y axis data.
        let x;
        let y;
        if (selectedLineType == 'base') {
            y = dataProcessed.base;
            x = dataProcessed.time_base;
        } else if (selectedLineType == 'trend') {
            y = dataProcessed.trend;
            x = dataProcessed.time_decomposed;
        } else if (selectedLineType == 'seasonal') {
            y = dataProcessed.seasonal;
            x = dataProcessed.time_decomposed;
        } else if (selectedLineType == 'residual') {
            y = dataProcessed.residual;
            x = dataProcessed.time_decomposed;
        } else { // selectedLineType == 'stationary'
            y = dataProcessed.stationary;
            x = dataProcessed.time_stationary;
        }
        x = x.map(d => d3.isoParse(d));

        // Define plot elements.
        const svg = d3.select('#svg-line');
        let dataToPlot = [];
        for (let i = 0; i < x.length; i++) dataToPlot.push({'x': x[i], 'y': y[i]});
        const widthSvg = Number(svg.style('width').replace('px', ''));
        const heightSvg = Number(svg.style('height').replace('px', ''));
        const margins = {left: 65, top: 20, right: 20, bottom: 70};
        const widthPlot = widthSvg - margins.left - margins.right;
        const heightPlot = heightSvg - margins.top - margins.bottom;
        const gPlot = svg.selectAll('.group-plot')
                        .data(['g'])
                        .join('g')
                        .attr('class', 'group-plot')
                        .attr('width', widthPlot)
                        .attr('height', heightPlot)
                        .attr('transform', `translate(${margins.left}, ${margins.top})`);
        const gXAxis = gPlot.selectAll('.group-x-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-x-axis')
                            .attr('transform', `translate(${0}, ${heightPlot})`);
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');
        const time_range = d3.extent(x);
        const scaleX = d3.scaleTime()
                        .domain(time_range)
                        .range([0, widthPlot]);
        const scaleY = d3.scaleLinear()
                        .domain(d3.extent(y))
                        .range([heightPlot, 0]);
        gXAxis.transition()
            .duration(1000)
            .call(d3.axisBottom(scaleX));
        gYAxis.transition()
            .duration(1000)
            .call(d3.axisLeft(scaleY));
        gXAxis.selectAll('.axis-label')
            .data([
                time_range[0] && time_range[1] ?
                `TIME (${time_range[0].toDateString()} - ${time_range[1].toDateString()})`:
                "TIME"
            ])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", widthSvg/2-38)
            .attr("y", 60)
            .attr('fill', 'black')
            .attr('font-style', 'italic');
        gXAxis.selectAll('.tick')
            .select('text')
            .attr('font-size', '10px')
            .attr('font-weight', 'bold')
            .attr('transform', 'rotate(-60) translate(-20, -5)')
        gYAxis.selectAll('.axis-label')
            .data(['VALUES'])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", -1*heightSvg/3)
            .attr("y", -50)
            .attr('fill', 'black')
            .attr('font-style', 'italic')
            .attr('transform', 'rotate(-90)');
        gPlot.selectAll('.path-line')
            .data([d3.line()(dataToPlot.map(d => [scaleX(d3.isoParse(d.x)), scaleY(d.y)]))])
            .join("path")
            .attr('class', 'path-line')
            .attr("fill", "none")
            .attr("stroke", "blue")
            .attr("stroke-width", 1.5)
            .attr('stroke-linecap', 'round')
            .transition()
            .duration(1000)
            .attr("d", d => d);
    }

    const plotHistData = () => {
        // Adding data to histogram.
        const bin = d3.bin()
                    .thresholds(controls.bins)
                    .value(d => d);
        const buckets = bin(dataProcessed.base);
        // Setting up axes.
        const svg = d3.select('#svg-hist')
        const widthSvg = Number(svg.style('width').replace('px', ''));
        const heightSvg = Number(svg.style('height').replace('px', ''));
        const margins = {left: 50, top: 20, right: 20, bottom: 50};
        const widthPlot = widthSvg - margins.left - margins.right;
        const heightPlot = heightSvg - margins.top - margins.bottom;
        const gPlot = svg.selectAll('.group-plot')
                        .data(['g'])
                        .join('g')
                        .attr('class', 'group-plot')
                        .attr('width', widthPlot)
                        .attr('height', heightPlot)
                        .attr('transform', `translate(${margins.left}, ${margins.top})`);
        const gXAxis = gPlot.selectAll('.group-x-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-x-axis')
                            .attr('transform', `translate(${0}, ${heightPlot})`);;
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');
        const scaleX = d3.scaleLinear()
                        .domain([buckets[0].x0, buckets[buckets.length - 1].x1])
                        .range([0, widthPlot]);
        const scaleY = d3.scaleLinear()
                        .domain([0, d3.max(buckets, (d) => d.length)])
                        .range([heightPlot,0]);
        gXAxis.selectAll('.axis-label')
            .data([`VALUES (bin width = ${roundToNPlaces(buckets[0].x1 - buckets[0].x0, 2)})`])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", widthSvg/2-38)
            .attr("y", 40)
            .attr('fill', 'black')
            .attr('font-style', 'italic');
        gYAxis.selectAll('.axis-label')
            .data(['FREQUENCY'])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", -1*heightSvg/3.5)
            .attr("y", -35)
            .attr('fill', 'black')
            .attr('font-style', 'italic')
            .attr('transform', 'rotate(-90)');
        // Adding bars.
        const offset = 10
        gPlot.selectAll('.bar')
            .data(buckets)
            .join("rect")
            .attr('class', 'bar')
            .attr('fill', '#4682B4')
            .attr('opacity', 0.7)
            .attr("x", (d) => scaleX(d.x0) + (offset/2))
            .attr("y", (d) => scaleY(d.length))
            .attr("height", (d) => scaleY(0) - scaleY(d.length))
            .transition()
            .duration(1000)
            .attr("width", (d) => scaleX(d.x1) - scaleX(d.x0) - (offset/2));
        gXAxis.transition()
            .duration(1000)
            .call(d3.axisBottom(scaleX));
        gYAxis.transition()
            .duration(1000)
            .call(d3.axisLeft(scaleY));
    }

    const plotCorrData = () => {
        // Prepare data.
        let dataToPlot = [];
        for (let i = 0; i < dataProcessed.acf.length; i++) dataToPlot.push({
            'x': dataProcessed.corr_lags[i], 
            'y_acf': dataProcessed.acf[i],
            'y_pacf': dataProcessed.pacf[i],
            'ci_pos': dataProcessed.corr_ci[i],
            'ci_neg': -1*dataProcessed.corr_ci[i]
        });

        // Set up plot elements.
        const svg = d3.select('#svg-corr');
        const widthSvg = Number(svg.style('width').replace('px', ''));
        const heightSvg = Number(svg.style('height').replace('px', ''));
        const margins = {left: 50, top: 20, right: 20, bottom: 50};
        const widthPlot = widthSvg - margins.left - margins.right;
        const heightPlot = heightSvg - margins.top - margins.bottom;
        const gPlot = svg.selectAll('.group-plot')
                        .data(['g'])
                        .join('g')
                        .attr('class', 'group-plot')
                        .attr('width', widthPlot)
                        .attr('height', heightPlot)
                        .attr('transform', `translate(${margins.left}, ${margins.top})`);
        const gXAxis = gPlot.selectAll('.group-x-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-x-axis')
                            .attr('transform', `translate(${0}, ${heightPlot})`);
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');
        const scaleX = d3.scaleLinear()
                        .domain([0, d3.max(dataProcessed.corr_lags)])
                        .range([0, widthPlot]);
        const scaleY = d3.scaleLinear()
                        .domain(d3.extent(
                            dataProcessed.acf
                            .concat(dataProcessed.pacf)
                            .concat(dataProcessed.corr_ci)
                            .concat(dataProcessed.corr_ci.map(d => -1*d))
                        ))
                        .range([heightPlot, 0]);
        gXAxis.transition()
            .duration(1000)
            .call(d3.axisBottom(scaleX));
        gXAxis.attr('transform', `translate(${0}, ${scaleY(0)})`);
            
        gXAxis.selectAll('.tick')
            .style('opacity', d => Number(d != 0));
        gYAxis.transition()
            .duration(1000)
            .call(d3.axisLeft(scaleY));
        gXAxis.selectAll('.axis-label')
            .data(["LAG"])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", widthSvg/2-38)
            .attr("y", 40)
            .attr('fill', 'black')
            .attr('font-style', 'italic');
        gYAxis.selectAll('.axis-label')
            .data(['CORRELATION'])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", -1*heightSvg/4)
            .attr("y", -35)
            .attr('fill', 'black')
            .attr('font-style', 'italic')
            .attr('transform', 'rotate(-90)');
        
        // Add ACF Line.
        const gLinesAcf = gPlot.selectAll('.lines-acf')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'lines-acf');
        gLinesAcf.selectAll('.line')
                .data(dataToPlot)
                .join('path')
                .attr('class', 'line')
                .attr('d', d => {
                    return `M ${scaleX(d.x)} ${scaleY(0)} V ${scaleY(d.y_acf)}`;
                })
                .style('stroke-width', 2)
                .attr('stroke-linecap', 'round')
                .style('stroke', 'red')
                .style('opacity', '0.6');
        
        // Add PACF Line.
        const gLinesPacf = gPlot.selectAll('.lines-pacf')
                                .data(['g'])
                                .join('g')
                                .attr('class', 'lines-pacf');

        gLinesPacf.selectAll('.line')
            .data(dataToPlot)
            .join('path')
            .attr('class', 'line')
            .attr('d', d => `M ${scaleX(d.x)} ${scaleY(0)} V ${scaleY(d.y_pacf)}`)
            .style('stroke-width', 5)
            .style('stroke', 'green')
            .attr('stroke-linecap', 'round')
            .style('opacity', '0.6');
        
        // Add Confidence Interval Lines.
        const gLinesCi = gPlot.selectAll('.lines-ci')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'lines-ci');
        const lineCiPos = d3.line()
                        .x((d) => scaleX(d.x))
                        .y((d) => scaleY(d.ci_pos));
        const lineCiNeg = d3.line()
                        .x((d) => scaleX(d.x))
                        .y((d) => scaleY(d.ci_neg));
        gLinesCi.selectAll('.line-pos')
                .data(dataToPlot)
                .join('path')
                .attr('class', 'line-pos')
                .attr('d', lineCiPos(dataToPlot))
                .style('stroke-width', 2)
                .attr('stroke-linecap', 'round')
                .style('opacity', 0.7)
                .style('stroke', 'blue');
        gLinesCi.selectAll('.line-neg')
                .data(dataToPlot)
                .join('path')
                .attr('class', 'line-neg')
                .attr('d', lineCiNeg(dataToPlot))
                .style('stroke-width', 2)
                .attr('stroke-linecap', 'round')
                .style('opacity', 0.7)
                .style('stroke', 'blue');

        // Add confidence interval legend.
        const gLegendCi = gPlot.selectAll('#legend-ci')
                            .data(['g'])
                            .join('g')
                            .attr('id', 'legend-ci');
        gLegendCi.selectAll('text')
                .data(['Confidence Interval'])
                .join('text')
                .text(d => d)
                .attr('font-size', '12px')
                .attr('fill', 'black')
                .attr('transform', `translate(${widthPlot/2-20}, ${heightPlot+margins.bottom-20})`);
        gLegendCi.selectAll('path')
                .data(['p'])
                .join('path')
                .attr('d', 'M 0 0 H 50')
                .style('stroke', 'blue')
                .style('opacity', 0.7)
                .attr('stroke-linecap', 'round')
                .style('stroke-width', '3')
                .attr('transform', `translate(${widthPlot/2-80}, ${heightPlot+margins.bottom-23})`)

    }

    const plotBoxData = () => {
        const svg = d3.select('#svg-box');
        const widthSvg = Number(svg.style('width').replace('px', ''));
        const heightSvg = Number(svg.style('height').replace('px', ''));
        const margins = {left: 50, top: 20, right: 20, bottom: 20};
        const widthPlot = widthSvg - margins.left - margins.right;
        const heightPlot = heightSvg - margins.top - margins.bottom;
        const gPlot = svg.selectAll('.group-plot')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-plot')
                            .attr('width', widthPlot)
                            .attr('height', heightPlot)
                            .attr('transform', `translate(${margins.left}, ${margins.top})`);
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');

        gYAxis.selectAll('.axis-label')
            .data(['VALUE'])
            .join('text')
            .attr('class', 'axis-label')
            .text(d => d)
            .attr("x", -1*heightSvg/3)
            .attr("y", -35)
            .attr('fill', 'black')
            .attr('font-style', 'italic')
            .attr('transform', 'rotate(-90)');
        
        let data_sorted=dataProcessed.base.sort(d3.ascending);
        let q1 = d3.quantile(data_sorted, .25);
        let median = d3.quantile(data_sorted, .5);
        let q3 = d3.quantile(data_sorted, .75);
        let interQuantileRange = q3 - q1;
        let min = q1 - 1.5 * interQuantileRange;
        let max = q3 + 1.5 * interQuantileRange;
        let outliers=[];
        for (let i=0;i<data_sorted.length;i++){
            if (data_sorted[i] < min || data_sorted[i] > max){
                outliers.push(data_sorted[i]);
            } 
        }

        const scaleY = d3.scaleLinear()
                        .domain(
                            controls.outliers ? 
                            d3.extent([min, max].concat(dataProcessed.base)) : 
                            [min, max]
                        ).range([heightPlot,0]);
        
        let center=widthPlot/2;
        let width=widthPlot-20;

        gYAxis.transition()
            .duration(1000)
            .call(d3.axisLeft(scaleY));
        
        gPlot.selectAll('.line')
            .data(['g'])
            .join('line')
            .attr('class','line')
            .attr("stroke","black")
            .transition()
            .duration(1000)
            .attr("x1", center)
            .attr("x2", center)
            .attr("y1", scaleY(min))
            .attr("y2", scaleY(max));

        gPlot.selectAll(".rect")
            .data(['g'])
            .join('rect')
            .attr('class','rect')
            .attr("stroke", "black")
            .style("fill", "green")
            .style("opacity", 0.6)
            .attr("width", width )
            .transition()
            .duration(1000)
            .attr("x", center - width/2)
            .attr("y", scaleY(q3) )
            .attr("height", (scaleY(q1)-scaleY(q3)));

        gPlot.selectAll(".line2")
            .data([min, median, max])
            .join("line")
            .attr("class","line2")
            .attr("stroke", "black")
            .transition()
            .duration(1000)
            .attr("x1", center-width/2)
            .attr("x2", center+width/2)
            .attr("y1", (d) => scaleY(d))
            .attr("y2", (d) => scaleY(d));

        gPlot.selectAll(".circle")
            .data(outliers)
            .join("circle")
            .attr('class','circle')
            .attr('stroke','black')
            .attr('fill','red')
            .style('opacity', 0.8)
            .transition()
            .duration(1000)
            .attr('cx', center)
            .attr('cy',(d) => scaleY(d))
            .attr('r', 3);
    }

    const computeOutliers = () => {
        const data_sorted=data.data.sort(d3.ascending);
        const q1 = d3.quantile(data_sorted, .25);
        const median = d3.quantile(data_sorted, .5);
        const q3 = d3.quantile(data_sorted, .75);
        const interQuantileRange = q3 - q1;
        const min = q1 - 1.5 * interQuantileRange;
        const max = q3 + 1.5 * interQuantileRange;
        outliers=[]; // Global variable.
        let sum = 0;
        for (let i=0;i<data_sorted.length;i++){
            if (data_sorted[i] < min || data_sorted[i] > max){
                outliers.push(data_sorted[i]);
            } 
            sum += data_sorted[i];
        }
        setNumSum(prevVal => {
            prevVal.mean = roundToNPlaces(sum/data.data.length, 2);
            prevVal.min = roundToNPlaces(min, 2);
            prevVal.max = roundToNPlaces(max, 2);
            prevVal.median = roundToNPlaces(median, 2);
            prevVal.q1 = roundToNPlaces(q1, 2);
            prevVal.q3 = roundToNPlaces(q3, 2);
            prevVal.num_outliers = roundToNPlaces(outliers.length, 2);
            prevVal.iqr = roundToNPlaces(interQuantileRange, 2);
            return prevVal;
        })
    }
    
    const setDecompositionType = (e) => {
        controls.decomposition_type = e.currentTarget.value;
    }
    useEffect(() => {
        // Set user controls.
        controls.freq = frequency;
        controls.period = period;
        controls.lags = lags;
        computeOutliers();
        handleApply();
    }, []);

    useEffect(() => {
        plotLineData();
        plotHistData();
        plotCorrData();
        plotBoxData();
    }, [stateDataProcessed]);

    useEffect(() => {
        plotLineData();
    }, [selectedLineType]);

    return (
        <div id='tsa_dashboard'>
            {/* Title. */}
            <div className="p-4">
                <h1 className="text-3xl font-bold text-center mb-2">{title}</h1>
                <hr className="border-t-2 border-gray-200 mb-2" />
            </div>
            <div className='sm:grid sm:grid-rows-3 sm:grid-cols-3 p-5 gap-5 mb-5'>
                <div id='controls mt-10 sm:mt-0'>
                    <div className='font-bold'>CONTROLS</div>
                    <TextBox label={'Frequency'} placeholder={controls.freq} id="text-box-freq" onChange={() => handleTextBoxChange('text-box-freq')} isEditable={false} />
                    <TextBox label={'Period'} placeholder={controls.period} id="text-box-period" onChange={() => handleTextBoxChange('text-box-period')} isEditable={true} />
                    <TextBox label={'Lags'} placeholder={controls.lags} id="text-box-lags" onChange={() => handleTextBoxChange('text-box-lags')} isEditable={true} />   
                    <TextBox label={'Bins'} placeholder={controls.bins} id="text-box-bins" onChange={() => handleTextBoxChange('text-box-bins')} isEditable={true} />    
                    <div className='grid gap-5 grid-cols-2 mt-2'>
                        <label>Outliers</label>
                        <span>
                            <input className='pl-0' type="checkbox" id="box-outliers" name="box-outlier" value="1" onChange={handleChkBoxChange}/>
                        </span>
                    </div>
                    <div className='grid gap-5 grid-cols-2 mt-2'>
                        Decomposition Type
                        <span className="grid-cols-2">
                            <div className="flex items-center space-x-4">
                                <label className="flex items-center">
                                    <input 
                                        type="radio" 
                                        name="radio_btn_decomposition_type" 
                                        value="additive" 
                                        defaultChecked 
                                        onClick={setDecompositionType}
                                        className="text-blue-600 focus:ring-blue-500 border-gray-300"
                                    />
                                    <span className="ml-2 text-sm text-gray-600">+</span>
                                </label>
                                <label className="flex items-center">
                                    <input 
                                        type="radio" 
                                        name="radio_btn_decomposition_type" 
                                        value="multiplicative" 
                                        onClick={setDecompositionType}
                                        className="text-blue-600 focus:ring-blue-500 border-gray-300"
                                    />
                                    <span className="ml-2 text-sm text-gray-600">x</span>
                                </label>
                            </div>
                        </span>
                    </div>
                    <div className='text-center grid grid-cols-2 gap-5 mb-5'> {/* Apply button. */}
                        <button className='py-2 px-5 text-center rounded-full text-sm font-bold bg-blue-500 text-white hover:bg-blue-600' onClick={handleApply}>
                            APPLY
                        </button>
                    </div>
                    <div className={statusMessage.includes('Success') ? 'text-green-600' : 'text-red-600'}>{statusMessage}</div>
                </div>

                <div id='line' className='col-span-2 mt-10 sm:mt-0 mb-16'>
                    <div className="flex justify-between items-center mb-2">
                        <b className="block text-lg font-semibold">Line Plot</b>
                        <a data-tooltip-id="line-plot" data-tooltip-html="Time series decomposition breaks down a dataset into trend, seasonal patterns, and random noise; it's like dissecting a signal to understand its trends and cycles. <br/>
                         When we adjust the data to make it consistent over time—removing upward or downward shifts and repetitive patterns—we make it 'stationary'. The line plot <br />then shows us this smoothed-out data, where any remaining shifts that grow or shrink over time might suggest inconsistent variation in the data's spread.">
                            <FaInfoCircle className="text-lg" />
                        </a>
                        <Tooltip id="line-plot"/>
                    </div>
                    <div className='flex gap-5 justify-between'>
                        <RadioButton label={'Base'} id="radio-base" name="linetype" value="base" selected={selectedLineType == 'base'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Trend'} id="radio-trend" name="linetype" value="trend" selected={selectedLineType == 'trend'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Seasonal'} id="radio-seasonal" name="linetype" value="seasonal" selected={selectedLineType == 'seasonal'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Residual'} id="radio-residual" name="linetype" value="residual" selected={selectedLineType == 'residual'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Stationary'} id="radio-stationary" name="linetype" value="stationary" selected={selectedLineType == "stationary"} uponClick={handleLineTypeSelection} />
                    </div>
                    <svg id='svg-line' className='w-full h-full'></svg>
                </div>

                <div id='num_sum' className='mt-10 sm:mt-0 text-left mb-10'>
                    <b className="block text-lg font-semibold">Number Summary</b>
                    <table className="w-full text-sm text-center text-gray-500 rounded-md shadow dark:text-gray-400">
                        <thead className="text-xs uppercase bg-gray-50 dark:bg-gray-700 dark:text-white">
                        <tr>
                            <th scope="col" className="py-3 px-6">Metric</th>
                            <th scope="col" className="py-3 px-6">Value</th>
                        </tr>
                        </thead>
                        <tbody>
                        {Object.entries(numSum).map(([metric, value], index) => (
                            <tr className={`${index % 2 === 0 ? 'bg-white' : 'bg-gray-50'}`}>
                            <td className="py-1 px-6 font-medium text-gray-900 whitespace-nowrap uppercase">
                                {metric}
                            </td>
                            <td className="py-1 px-6">{value}</td>
                            </tr>
                        ))}
                        <tr>
                            <td className="py-1 px-6 font-medium text-gray-900 whitespace-nowrap uppercase"># Differenced</td>
                            <td>{stateDataProcessed.num_diff}</td>
                        </tr>
                        </tbody>
                    </table>
                </div>

                <div id='hist' className='col-span-2 mt-10 sm:mt-0 mb-10'>
                    <div className="flex justify-between items-center mb-2">
                        <b className="block text-lg font-semibold">Histogram Plot</b>
                        <a data-tooltip-id="histogram-plot" data-tooltip-html="A histogram is a graphical representation of the distribution of a dataset. <br/>It displays the frequency of data points falling within specified intervals, known as bins, along the x-axis, <br/>with the count or frequency of observations in each bin represented on the y-axis.<br/> The no. of approximate (depends on how data range can be divided) bins may be changed from the 'CONTROLS' section.">
                            <FaInfoCircle className="text-lg" />
                        </a>
                        <Tooltip id="histogram-plot" />
                    </div>
                    <svg id='svg-hist' className='w-full h-full'></svg>
                </div>

                <div id='box' className='mt-10 sm:mt-0'>
                    <div className="flex justify-between items-center mb-2">
                        <b className="block text-lg font-semibold">Box Plot</b>
                        <a data-tooltip-id="box-plot" data-tooltip-html="A boxplot visualizes data distribution through a five-number summary:<br/> minimum, first quartile, median, third quartile, and maximum. <br/>It shows the data's spread, central point, potential skewness, and outliers, <br/>which are marked as separate points if they're much higher or lower than the rest.">
                            <FaInfoCircle className="text-lg" />
                        </a>
                        <Tooltip id="box-plot" />
                    </div>
                    <svg id='svg-box' className='w-full h-full'></svg>
                </div>
                
                <div id='corr' className='col-span-2 mt-10 sm:mt-0'>
                    <div className="flex justify-between items-center mb-2">
                        <b className="block text-lg font-semibold">
                        <font color='red'>ACF</font> & <font color='green'>PACF</font> Plot
                        </b>
                        <a data-tooltip-id="corr-plot" data-tooltip-html="The ACF and PACF plots are graphs that help us see how a series of data points relate to their past values (lags), <br/>with ACF including indirect correlations and PACF focusing on direct correlations only. <br/>The plots tell us if past values influence future ones, with lines beyond the blue area hinting at stronger relationships, all adjustable via the control panel.">
                            <FaInfoCircle className="text-lg" />
                        </a>
                        <Tooltip id="corr-plot" />
                    </div>
                    <svg id='svg-corr' className='w-full h-full'></svg>
                </div>
            </div>
        </div>
    )
}
