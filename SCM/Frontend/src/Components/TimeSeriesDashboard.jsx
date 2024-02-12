import * as d3 from 'd3'
import { useRef, useEffect } from 'react'

function TimeSeriesDashboard({ data, seasonalityPeriod, movingAvgWindowSize}) {
    data = data ?? [];
    const svgLineLevel = useRef();
    const svgLineTrend = useRef();
    const svgLineSeasonal = useRef();
    const svgLineResidual = useRef();
    const svgHist = useRef();

    const plots = [
        <div className='mt-10'>
            <svg ref={svgLineLevel} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgLineTrend} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgLineSeasonal} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgLineResidual} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgHist} className='bg-slate-200'></svg>
        </div>
    ]

    const validateData = () => {
        if (data.length == 0) {
            return (
                <div className='flex h-screen w-screen float p-20 flex-col justify-center align-center'>
                    <div className='font-bold bg-red-500 text-white px-10 py-5 rounded-xl text-center border-4'>Please provide data to generate the dashboard.</div>
                </div>
            )
        } else if (
            typeof(data[0]) != typeof({}) 
            || !Object.keys(data[0]).includes('timestamp') 
            || !Object.keys(data[0]).includes('data')
        ) {
            return (
                <div className='flex h-screen w-screen float p-20 flex-col justify-center align-center'>
                    <div className='font-bold bg-red-500 text-white px-10 py-5 rounded-xl text-center border-4'>{"Incorrect data format. Expected data = [{timestamp: <date_time>, data: <float>}, ...]."}</div>
                </div>
            )
        }

        return plots;
    }

    const addLinePlot = (refSvg, y, x) => {
        // If no x is provided, it is set as index of y axis values.
        if (x == undefined) {
            x = [];
            for (let i=0; i<y.length; i++) x.push(i);
        }
        if (x.length != y.length) throw new Error('Inputs x and y must be of the same length.')
        let data = [];
        for (let i = 0; i < x.length; i++) data.push({'x': x[i], 'y': y[i]});
        const widthSvg = 500;
        const heightSvg = 300;
        const svg = d3.select(refSvg.current)
                    .attr('id', '#plot-line')
                    .attr('width', widthSvg)
                    .attr('height', heightSvg);
        const margins = {left: 50, top: 10, right: 10, bottom: 50};
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
            
        let scaleX;
        if (typeof(x[0]) == typeof(0)) scaleX = d3.scaleLinear();
        else scaleX = d3.scaleTime();
        scaleX.domain(d3.extent(x))
            .range([0, widthPlot]);
        const scaleY = d3.scaleLinear()
                        .domain(d3.extent(y))
                        .range([heightPlot, 0]);
        gXAxis.call(d3.axisBottom(scaleX));
        gYAxis.call(d3.axisLeft(scaleY));
        gPlot.selectAll('.path-line')
            .data([d3.line()(data.map(d => [scaleX(d3.isoParse(d.x)), scaleY(d.y)]))])
            .join("path")
            .attr('class', 'path-line')
            .attr("fill", "none")
            .attr("stroke", "blue")
            .attr("stroke-width", 1.5)
            .transition()
            .duration(1000)
            .attr("d", d => d);
    }

    const addHistPlot = (refSvg) => {
        const timeSeriesValues = data.map(d => d.data);
        const bins = d3.bin()
        .thresholds(10)
        .value(d => d)
        (timeSeriesValues);
        const widthSvg = 300;
        const heightSvg = 200;
        const svg = d3.select(refSvg.current)
                    .attr('id', '#plot-histogram')
                    .attr('width', widthSvg)
                    .attr('height', heightSvg);
        const margins = {left: 50, top: 10, right: 10, bottom: 50};
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
                            .domain([bins[0].x0, bins[bins.length - 1].x1])
                            .range([0, widthPlot]);

        const scaleY = d3.scaleLinear()
                            .domain([0, d3.max(bins, (d) => d.length)])
                            .range([heightPlot,0]);
        
        gXAxis.call(d3.axisBottom(scaleX));
        gYAxis.call(d3.axisLeft(scaleY));
        gPlot.selectAll('.bar')
        .data(bins)
        .join("rect")
        .attr('class', 'bar')
        .attr("x", (d) => scaleX(d.x0)+1)
        .attr("width", (d) => scaleX(d.x1) - scaleX(d.x0)-1)
        .attr("y", (d) => scaleY(d.length))
        .attr("height", (d) => scaleY(0) - scaleY(d.length));

    
    }

    const decomposeTimeSeries = (series, seasonalityPeriod, movingAvgWindowSize) => {
        /** This function decomposes a given time series to extract
         *  underlying trend, seasonality and residual components. */
        
        // Trend = Moving average.
        const trend = calculateMovingAverage(series, movingAvgWindowSize);

        // Seasonality = Calculate seasonal component
        const seasonal = calculateSeasonalComponent(series, seasonalityPeriod);
    
        // Residual = Noise = Series - Trend - Seasonality
        const residual = calculateResidual(series, trend, seasonal);
    
        return { trend, seasonal, residual };
    }
    
    const calculateMovingAverage = (series, windowSize) => {
        const movingAverages = [];
        // Loop through each window of data in the series 
        // as per given window size. 
        // Example: If series = [1, 2, 3, 4] & window size = 3,
        //          then, window1 = [1, 2, 3] & avg1 = (1+2+3)/3 = 2
        //          and, window2 = [2, 3, 4] & avg2 = (2+3+4)/3 = 3 ...
        for (let i = 0; i < series.length - windowSize + 1; i++) {
            const window = series.slice(i, i + windowSize); // get window
            const sum = window.reduce((acc, val) => acc + val, 0); // compute sum
            const average = sum / windowSize; // compute average
            movingAverages.push(average); // push average to list of averages
        }
        return movingAverages;
    }
    
    const calculateSeasonalComponent = (series, seasonalityPeriod) => {
        /** Calculates the seasonal component of given time series data 
         *  by computing the average value of data points at each position 
         *  within given seasonal seasonalityPeriod. */
        const seasonal = [];
        for (let i = 0; i < series.length; i++) { // For each element in the series ...
            const index = i % seasonalityPeriod; // Get index of element in seasonal seasonalityPeriod.
            // Get all elements in the series that are at 
            // the same position as this one within the seasonal seasonalityPeriod.
            const season = series.filter((_, j) => j % seasonalityPeriod === index);
            const sum = season.reduce((acc, val) => acc + val, 0); // Compute sum.
            const average = sum / Math.floor(series.length / seasonalityPeriod); // Compute average.
            seasonal.push(average); // Add season average for this element to the list.
        }
        return seasonal;
    }
    
    const calculateResidual = (series, trend, seasonal) => {
        /** Computes residual or noise by subtracting the trend and seasonal
         *  components from the series component for each series element. */
        const residual = [];
        for (let i = 0; i < series.length; i++) {
            residual.push(series[i] - trend[i % trend.length] - seasonal[i % seasonal.length]);
        }
        return residual;
    }

    useEffect(() => {
        // Line plot.
        const timestamps = data.map(d => d3.isoParse(d.timestamp));
        const timeSeriesValues = data.map(d => d.data);
        addLinePlot(svgLineLevel, timeSeriesValues, timestamps);

        // Time Series Decomposition.
        const { trend, seasonal, residual } = decomposeTimeSeries(
            data.map(d => d.data), 
            seasonalityPeriod, 
            movingAvgWindowSize
        );
        addLinePlot(svgLineTrend, trend);
        addLinePlot(svgLineSeasonal, seasonal);
        addLinePlot(svgLineResidual, residual);

        // PACF Plot.

        // Histogram.

        // Box Plot.

        // Descriptive Statistics Summary.
    }, []);

    return (
        <div className='w-full h-full grid justify-items-center'>
            {validateData()}
        </div>
    )
}

export default TimeSeriesDashboard;