import * as d3 from 'd3'
import { useRef, useEffect } from 'react'

function TimeSeriesDashboard({ data }) {
    data = data ?? [];
    const svgLine = useRef();
    const svgHist = useRef();

    const plots = [
        <div className='mt-10'>
            <svg ref={svgLine} className='bg-slate-200'></svg>
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

    const addLinePlot = (refSvg) => {
        const timestamps = data.map(d => d3.isoParse(d.timestamp));
        const timeSeriesValues = data.map(d => d.data);
        const widthSvg = 300;
        const heightSvg = 200;
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
                            .attr('transform', `translate(${0}, ${heightPlot})`);;
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');
        const scaleX = d3.scaleTime()
                        .domain(d3.extent(timestamps))
                        .range([0, widthPlot]);
        const scaleY = d3.scaleLinear()
                        .domain(d3.extent(timeSeriesValues))
                        .range([heightPlot, 0]);
        gXAxis.call(d3.axisBottom(scaleX));
        gYAxis.call(d3.axisLeft(scaleY));
        console.log(data.map(d => [scaleX(d.timestamp), scaleY(d.data)]));
        gPlot.selectAll('.path-line')
            .data([d3.line()(data.map(d => [scaleX(d3.isoParse(d.timestamp)), scaleY(d.data)]))])
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
        const timestamps = data.map(d => d3.isoParse(d.timestamp));
        const timeSeriesValues = data.map(d => d.data);
        const widthSvg = 300;
        const heightSvg = 200;
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
                            .attr('transform', `translate(${0}, ${heightPlot})`);;
        const gYAxis = gPlot.selectAll('.group-y-axis')
                            .data(['g'])
                            .join('g')
                            .attr('class', 'group-y-axis');
        const scaleX = d3.scaleTime()
                        .domain(d3.extent(timestamps))
                        .range([0, widthPlot]);
        const scaleY = d3.scaleLinear()
                        .domain(d3.extent(timeSeriesValues))
                        .range([heightPlot, 0]);
        gXAxis.call(d3.axisBottom(scaleX));
        gYAxis.call(d3.axisLeft(scaleY));
        console.log(data.map(d => [scaleX(d.timestamp), scaleY(d.data)]));
        gPlot.selectAll('.path-line')
            .data([d3.line()(data.map(d => [scaleX(d3.isoParse(d.timestamp)), scaleY(d.data)]))])
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
        // Line plot.
        addLinePlot(svgLine);
        // addHistPlot(svgHist);
    }, []);

    return (
        <div className='w-full h-full grid grid-cols-2 justify-items-center'>
            {validateData()}
        </div>
    )
}

export default TimeSeriesDashboard;