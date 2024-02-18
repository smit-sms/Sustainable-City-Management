import React, { useEffect, useState } from 'react'
import * as d3 from "d3"
import TextBox from './TextBox'
import RadioButton from './RadioButton'

let controls = {
    freq: 'None',
    period: 0,
    lags: 1
}

let feedback = "";

const TSADashboard = ({ data, frequency, period, lags, title }) => {
    const [dataLinePlot, setDataLinePlot] = useState({
        base:[], base_time: [], trend:[], 
        seasonal:[], decomposed_time:[], 
        residual:[], stationary: [], stationary_time: []
    });
    const [numDiff, setNumDiff] = useState(0);
    const [selectedLineType, setSelectedLineType] = useState('base');
    const [statusMessage, setStatusMessage] = useState("");

    const handleTextBoxChange = (id) => {
        feedback = "";
        const textBox = d3.select(`#${id}`).select('input');
        const textBoxType = id.split('-')[2];
        const val = textBox.property("value");
        if (sanityCheckControls(textBoxType, val)) {
            if (textBoxType == 'freq') controls[textBoxType] = val;
            if (textBoxType == 'period' || textBoxType == 'lags') controls[textBoxType] = parseInt(val);  
            textBox.attr('style', 'border: 2px solid green');
        } else {
            if (textBoxType == 'freq') controls.freq = frequency;
            if (textBoxType == 'period') controls.period = period;
            if (textBoxType == 'lags') controls.lags = lags;
            textBox.attr('style', 'border: 2px solid red');
        }
    }

    const handleApply = (e) => {
        feedback = "";
        ['freq', 'period', 'lags'].forEach(tb => {
            d3.select(`#text-box-${tb}`).select('input').property("value", "").attr('style', 'border:none');
        });
        // Update data.
        updateLineData();
    }

    const sanityCheckControls = (textBoxType, val) => {
        if (textBoxType == 'freq') return val.length > 0 && val.slice(0, 1) != 0;
        if (textBoxType == 'period') return val > 0 && val <= Math.floor(data.data.length/2);
        if (textBoxType == 'lags') return val > 0 && val <= data.data.length;
        return false
    }

    const handleLineTypeSelection = (e) => {
        const value = e.currentTarget.value;
        setSelectedLineType(prevVal => value);
    }

    const updateLineData = async () => {
        let lineData = {
            base: data.data,
            base_time: data.time,
            decomposed_time: [],
            trend: [], 
            seasonal: [], 
            residual: [], 
            stationary: [],
            stationary_time: []
        }
        let decomposed = await fetch('http://127.0.0.1:8001/tsa/decompose/', {
            method: 'POST',
            body: JSON.stringify({"data": data, "freq": controls.freq, "period": controls.period, "model_type": "additive"}),
            headers: {'Content-Type':'application/json'}
        })
        decomposed = await decomposed.json();
        if (decomposed.message.includes('Failure')) {
            feedback += decomposed.message;
        }
        decomposed = decomposed.data;
        lineData.decomposed_time = decomposed.time;
        lineData.trend = decomposed.trend;
        lineData.seasonal = decomposed.seasonal;
        lineData.residual = decomposed.residual;

        let dataStationary = data;
        let stationarity;
        let diff;
        while (true) {
            // Check data stationarity.
            stationarity = await fetch('http://127.0.0.1:8001/tsa/stationarity/', {
                method: 'POST',
                body: JSON.stringify({"data": dataStationary.data}),
                headers: {'Content-Type':'application/json'}
            });
            stationarity = await stationarity.json();
            if (stationarity.message.includes('Failure')) {
                feedback += stationarity.message;
                break; // If there was a failure, exit loop.
            }
            if (stationarity.data.is_stationary == 1) break; // If stationary, exit loop.
            else {  // If not stationary, make stationary by differencing.
                diff = await fetch('http://127.0.0.1:8001/tsa/first_difference/', {
                    method: 'POST',
                    body: JSON.stringify({"data": dataStationary, "freq": controls.freq}),
                    headers: {'Content-Type':'application/json'}
                });
                diff = await diff.json();
                if (diff.message.includes('Failure')) {
                    feedback += diff.message;
                    break;
                }
                dataStationary = diff.data;
                setNumDiff(prevVal => prevVal + 1);
            }
        }
        lineData.stationary = dataStationary.data;
        lineData.stationary_time = dataStationary.time;
        if (feedback.length > 0) {
            setStatusMessage(feedback);
            setTimeout(() => setStatusMessage(prevVal => ""), 5000);
        }
        setDataLinePlot(prevVal => lineData);
    }

    const plotLineData = () => {
        // Get appropriate x axis and y axis data.
        let x;
        let y;
        if (selectedLineType == 'base') {
            y = dataLinePlot.base;
            x = dataLinePlot.base_time;
        } else if (selectedLineType == 'trend') {
            y = dataLinePlot.trend;
            x = dataLinePlot.decomposed_time;
        } else if (selectedLineType == 'seasonal') {
            y = dataLinePlot.seasonal;
            x = dataLinePlot.decomposed_time;
        } else if (selectedLineType == 'residual') {
            y = dataLinePlot.residual;
            x = dataLinePlot.decomposed_time;
        } else { // selectedLineType == 'stationary'
            y = dataLinePlot.stationary;
            x = dataLinePlot.stationary_time;
        }
        x = x.map(d => d3.isoParse(d));

        // Define plot elements.
        const svg = d3.select('#svg-line');
        let dataToPlot = [];
        for (let i = 0; i < x.length; i++) dataToPlot.push({'x': x[i], 'y': y[i]});
        const widthSvg = Number(svg.style('width').replace('px', ''));
        const heightSvg = Number(svg.style('height').replace('px', ''));
        const margins = {left: 65, top: 5, right: 5, bottom: 65};
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
            .attr("y", 50)
            .attr('fill', 'black')
            .attr('font-style', 'italic');
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
            .transition()
            .duration(1000)
            .attr("d", d => d);
    }
    
    useEffect(() => {
        // Set user controls.
        controls.freq = frequency;
        controls.period = period;
        controls.lags = lags;
        handleApply();
    }, []);

    useEffect(() => {
        plotLineData();
    }, [dataLinePlot]);

    useEffect(() => {
        plotLineData();
    }, [selectedLineType])
    
    return (
        <div>
            {/* Title. */}
            <div className='text-3xl p-5 text-center'>{title}</div>
            <div className='grid grid-rows-3 grid-cols-3 p-5 gap-5'>
                <div id='controls'>
                    <div className='text-center flex justify-center gap-5'> {/* Apply button. */}
                        <div className='font-bold min-h-full flex flex-row items-center'>CONTROLS</div>
                        <button className='py-2 px-5 text-center rounded-full text-sm font-bold bg-blue-500 text-white hover:bg-blue-600' onClick={handleApply}>
                            APPLY
                        </button>
                    </div>
                    <TextBox label={'Frequency'} placeholder={controls.freq} id="text-box-freq" onChange={() => handleTextBoxChange('text-box-freq')} />
                    <TextBox label={'Period'} placeholder={controls.period} id="text-box-period" onChange={() => handleTextBoxChange('text-box-period')} />
                    <TextBox label={'Lags'} placeholder={controls.lags} id="text-box-lags" onChange={() => handleTextBoxChange('text-box-lags')} />       
                    <div className={statusMessage.includes('Success') ? 'text-green-600' : 'text-red-600'}>{statusMessage}</div>
                </div>
                <div id='line' className='col-span-2'>
                    <p>Line Plot</p>
                    <svg id='svg-line' className='w-full h-72 bg-slate-200'></svg>
                    <div className='flex gap-5 justify-between'>
                        <RadioButton label={'Base'} id="radio-base" name="linetype" value="base" selected={selectedLineType == 'base'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Trend'} id="radio-trend" name="linetype" value="trend" selected={selectedLineType == 'trend'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Seasonal'} id="radio-seasonal" name="linetype" value="seasonal" selected={selectedLineType == 'seasonal'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Residual'} id="radio-residual" name="linetype" value="residual" selected={selectedLineType == 'residual'} uponClick={handleLineTypeSelection} />
                        <RadioButton label={'Stationary'} id="radio-stationary" name="linetype" value="stationary" selected={selectedLineType == "stationary"} uponClick={handleLineTypeSelection} />
                    </div>
                </div>
                <div id='num_sum'>
                    Number Summery
                </div>
                <div id='hist' className='col-span-2'>
                    Histogram Plot
                    <svg id='svg-hist' className='w-full h-72 bg-slate-200'></svg>
                </div>
                <div id='box'>
                    Box Plot
                    <svg id='svg-box' className='w-full h-72 bg-slate-200'></svg>
                </div>
                <div id='corr' className='col-span-2'>
                    ACF & PACF Plot
                    <svg id='svg-corr' className='w-full h-72 bg-slate-200'></svg>
                </div>
            </div>
        </div>
    )
}

export default TSADashboard