import * as d3 from 'd3'
import { useRef, useEffect } from 'react'

function TimeSeriesDashboard({ data, seasonalityPeriod, movingAvgWindowSize}) {
    data = data ?? [];
    const svgLineLevel = useRef();
    const svgLineTrend = useRef();
    const svgLineSeasonal = useRef();
    const svgLineResidual = useRef();
    const svgHist = useRef();
    const svgBox=useRef();
    const svgSummary=useRef();
    const svgPacf = useRef();

    const plots = [
        <div className='mt-10'>
            <svg ref={svgLineLevel} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgLineTrend} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgLineSeasonal} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgLineResidual} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgHist} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgPacf} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgBox} width={500} height={300} className='bg-slate-200'></svg>
        </div>,
        <div className='mt-10'>
            <svg ref={svgSummary} width={500} height={300} className='bg-slate-200'></svg>
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
        const widthSvg = Number(d3.select(refSvg.current).style('width').replace('px', ''));
        const heightSvg = Number(d3.select(refSvg.current).style('height').replace('px', ''));
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

    const addHistPlot = (refSvg, data) => {
        const bin = d3.bin()
                    .thresholds(10)
                    .value(d => d);
        const buckets = bin(data);
        const widthSvg = Number(d3.select(refSvg.current).style('width').replace('px', ''));
        const heightSvg = Number(d3.select(refSvg.current).style('height').replace('px', ''));
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
                        .domain([buckets[0].x0, buckets[buckets.length - 1].x1])
                        .range([0, widthPlot]);

        const scaleY = d3.scaleLinear()
                        .domain([0, d3.max(buckets, (d) => d.length)])
                        .range([heightPlot,0]);
        
        gXAxis.call(d3.axisBottom(scaleX));
        gYAxis.call(d3.axisLeft(scaleY));
        gPlot.selectAll('.bar')
            .data(buckets)
            .join("rect")
            .attr('class', 'bar')
            .attr("x", (d) => scaleX(d.x0)+1)
            .attr("width", (d) => scaleX(d.x1) - scaleX(d.x0)-1)
            .attr("y", (d) => scaleY(d.length))
            .attr("height", (d) => scaleY(0) - scaleY(d.length));
    }
    
    const addBoxPlot = (refSvg,data) => {
        const widthSvg = 300;
        const heightSvg = 200;
        const svg = d3.select(refSvg.current)
                    .attr('id', '#plot-box')
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
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');
        
        let data_sorted=data.sort(d3.ascending);
        let q1 = d3.quantile(data_sorted, .25);
        let median = d3.quantile(data_sorted, .5);
        let q3 = d3.quantile(data_sorted, .75);
        let interQuantileRange = q3 - q1;
        let min = q1 - 1.5 * interQuantileRange;
        let max = q3 + 1.5 * interQuantileRange;
        let outliers=[];
        for (let i=0;i<data_sorted.length;i++){
            if (data_sorted[i]<min || data_sorted[i] >max)
                {
                    outliers.push(data_sorted[i]);
                } 
        }
        const scaleY = d3.scaleLinear()
                        .domain([min-10,max+10])
                        .range([heightPlot,0]);
        
        let center=120;
        let width=100;

        gYAxis.call(d3.axisLeft(scaleY));
        

        gPlot.selectAll('.line')
        .data(['g'])
        .join('line')
        .attr('class','line')
        .attr("x1", center)
        .attr("x2",center)
        .attr("y1", scaleY(min))
        .attr("y2", scaleY(max))
        .attr("stroke","black");

        gPlot.selectAll(".rect")
        .data(['g'])
        .join('rect')
        .attr('class','rect')
        .attr("x", center - width/2)
        .attr("y", scaleY(q3) )
        .attr("height", (scaleY(q1)-scaleY(q3)) )
        .attr("width", width )
        .attr("stroke", "black")
        .style("fill", "#69b3a2");

        gPlot.selectAll(".line2")
        .data([min, median, max])
        .join("line")
        .attr("class","line2")
        .attr("x1", center-width/2)
        .attr("x2", center+width/2)
        .attr("y1", (d) => scaleY(d) )
        .attr("y2", (d) => scaleY(d) )
        .attr("stroke", "black");

        gPlot.selectAll(".circle")
            .data(outliers)
            .join("circle")
            .attr('class','circle')
            .attr('cx',center)
            .attr('cy',(d) => scaleY(d))
            .attr('r',1)
            .attr('stroke','black')
            .attr('fill','white')
    }

    const AddSummary = (refSvg,data) =>{
            const widthSvg = 300;
            const heightSvg = 200;
            const svg = d3.select(refSvg.current)
                        .attr('id', '#plot-summary')
                        .attr('width', widthSvg)
                        .attr('height', heightSvg);

            let data_sorted=data.sort(d3.ascending);
            let q1 = d3.quantile(data_sorted, .25);
            let median = d3.quantile(data_sorted, .5);
            let q3 = d3.quantile(data_sorted, .75);

            let data2 = [
                ["Measure","Value"],
                ["Max",data_sorted[data_sorted.length-1]],
                ["Min",data_sorted[0]],
                ["Median",median],
                ["First quartile",q1],
                ["Third quartile",q3]

              ];


              
              // Cell dimensions
              const cellWidth = 150;
              const cellHeight = 30;
              
              // Append rows

              const rows = svg.selectAll(".row")
                .data(data2)
                .join("g")
                .attr("class", "row")
                .attr("transform", (d, i) => `translate(0, ${(i) * cellHeight})`);

              rows.selectAll(".hline")
                .data(['g'])
                .join('line')
                .attr("class","hline")
                .attr("x1", (d,i) => {return 0})
                .attr("x2", (d,i) => {return 2*cellWidth})
                .attr("y1", (d,i) => {return i*cellHeight} )
                .attr("y2", (d,i) => {return i*cellHeight} )
                .attr("stroke", "black");
              
              // Append cells
              const cells = rows.selectAll(".cell")
                .data(d => d)
                .join('g')
                .attr("class", "cell")
                .attr("transform", (d, i) => `translate(${i * cellWidth}, 0)`);
              
              // Append cell background
              cells.selectAll(".rect")
                .data(d=>[d])
                .join('rect')
                .attr('class','rect')
                .attr("width", cellWidth)
                .attr("height", cellHeight)
                .attr("fill", (d,i) => {if(d=="Measure" || d=="Value"){return "red";} else {return "lightgray";}});
              
              // Append text content
              cells.selectAll('.text')
                .data(d=>[d])
                .join('text')
                .attr('class','text')
                .attr("x", cellWidth / 2)
                .attr("y", cellHeight / 2)
                .attr("dy", "0.35em")
                .attr("text-anchor", "middle")
                .attr("font-weight",(d,i) => {if(d=="Measure" || d=="Value"){return 900;} else {return 400;}})
                .text(d => d);



            
            
            
            
            
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

    const acfPacf = (series, maxLag) => {
        const pacfValues = [];
        const acfValues = [];
        
        // Compute autocorrelation for each lag up to maxLag
        for (let lag = 1; lag <= maxLag; lag++) {
            // Compute autocorrelation at lag
            const acfAtLag = computeAcf(series, lag);
            acfValues.push(acfAtLag);
            
            // Compute partial autocorrelation at lag
            const pacfAtLag = computePacf(series, lag, acfAtLag);
            
            // Store partial autocorrelation coefficient
            pacfValues.push(pacfAtLag);
        }
        
        return {
            'acf': acfValues,
            'pacf': pacfValues
        };
    }

    const computeAcf = (series, lag) => {
        const n = series.length;
        const mean = series.reduce((acc, val) => acc + val, 0) / n;
        
        let numerator = 0;
        let denominator = 0;
        
        for (let i = lag; i < n; i++) {
            numerator += (series[i] - mean) * (series[i - lag] - mean);
            denominator += Math.pow((series[i] - mean), 2);
        }
        
        return numerator / denominator;
    }

    const computePacfCoefficient = (series, lag) => {
        const n = series.length;
        const mean = series.reduce((acc, val) => acc + val, 0) / n;
        
        let numerator = 0;
        let denominator = 0;
        
        for (let i = lag; i < n; i++) {
            numerator += (series[i] - mean) * (series[i - lag] - mean);
            denominator += Math.pow((series[i] - mean), 2);
        }
        
        return numerator / denominator;
    }
    
    const computePacf = (series, lag, acfAtLag) => {
        const n = series.length;
        
        // Calculate partial autocorrelation coefficient using Yule-Walker equations
        let sum = acfAtLag;
        
        for (let j = 1; j <= lag - 1; j++) {
            sum += (computePacfCoefficient(series, j) * computePacfCoefficient(series, lag - j));
        }
        
        return sum;
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
        addBoxPlot(svgBox,timeSeriesValues);
        AddSummary(svgSummary,timeSeriesValues);

        // Histogram.
        addHistPlot(svgHist, timeSeriesValues);

        // PACF Plot.
        const res = acfPacf(timeSeriesValues, timeSeriesValues.length);
        console.log('PACF =', res);

        // Box Plot.

        // Descriptive Statistics Summary.
    }, []);

    return (
        <div className='w-full h-full grid justify-items-center'>
            { validateData() }
        </div>
    )
}

export default TimeSeriesDashboard;