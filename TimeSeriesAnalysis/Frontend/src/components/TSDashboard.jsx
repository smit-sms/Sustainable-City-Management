import React, { useEffect, useState } from 'react'
import * as d3 from "d3"
import TextBox from './TextBox'

let controls = {
    freq: 'None',
    period: 0,
    lags: 1
}

const TSDashboard = ({ data, frequency, period, lags, title }) => {
    const [stateChangeControls, setStateChangeControls] = useState(0);
    const [decomposed, setDecomposed] = useState({'trend':[], 'seasonality':[], 'residual':[]});

    const handleTextBoxChange = (id) => {
        const textBox = d3.select(`#${id}`).select('input');
        const textBoxType = id.split('-')[2];
        const val = textBox.property("value");
        if (sanityCheckControls(textBoxType, val)) {
            controls[textBoxType] = val;
            textBox.attr('style', 'border: 2px solid green');
        } else {
            if (textBoxType == 'freq') controls.freq = frequency;
            if (textBoxType == 'period') controls.period  = period;
            if (textBoxType == 'lags') controls.lags = lags;
            textBox.attr('style', 'border: 2px solid red');
        }
    }

    const handleApply = (e) => {
        ['freq', 'period', 'lags'].forEach(tb => {
            d3.select(`#text-box-${tb}`).select('input').property("value", "").attr('style', 'border:none');
        })
        setStateChangeControls(prevVal => 1 - prevVal);
    }

    const sanityCheckControls = (textBoxType, val) => {
        if (textBoxType == 'freq') return val.length > 0;
        if (textBoxType == 'period') return val > 0 || val < data.data.length;
        if (textBoxType == 'lags') return val > 0 || val < data.data.length;
        return false
    }
    
    useEffect(() => {
        // Set user controls.
        controls.freq = frequency;
        controls.period = period;
        controls.lags = lags;

        // Fetch decomposition data.
        fetch('http://127.0.0.1:8001/tsa/decompose/', {
            method: 'POST',
            body: JSON.stringify({"data": data, "freq": controls.freq, "period": controls.period, "model_type": "additive"}),
            headers: {'Content-Type':'application/json'}
        })
        .then(response => response.json())
        .then(response => {
            setDecomposed(prevVal => response.data);
        });

        handleApply();
    }, []);

    useEffect(() => {
        
    }, [decomposed]);
    
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
                    {  
                        stateChangeControls >= 0 ?
                        <>
                            <TextBox label={'Frequency'} placeholder={controls.freq} id="text-box-freq" onChange={() => handleTextBoxChange('text-box-freq')} />
                            <TextBox label={'Period'} placeholder={controls.period} id="text-box-period" onChange={() => handleTextBoxChange('text-box-period')} />
                            <TextBox label={'Lags'} placeholder={controls.lags} id="text-box-lags" onChange={() => handleTextBoxChange('text-box-lags')} />
                        </> : 
                        <></>
                    }
                </div>
                <div id='line' className='col-span-2'>
                    Line Plot
                    <svg id='svg-line' className='w-full h-72 bg-slate-200'></svg>
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

export default TSDashboard