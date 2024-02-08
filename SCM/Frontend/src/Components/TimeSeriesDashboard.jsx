import * as d3 from 'd3'
import { useRef, useEffect } from 'react'

function TimeSeriesDashboard({ data }) {
    data = data ?? [];
  const svgLine = useRef();

  const plots = [
      <div className='mt-10'>
        <svg ref={svgLine} className='bg-slate-200'></svg>
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

  useEffect(() => {
    const timestamps = data.map(d => d3.isoParse(d.timestamp));
    const timeSeriesValues = data.map(d => d.data);
    const widthSvg = 500;
    const heightSvg = 300;
    const svg = d3.select(svgLine.current)
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

    gPlot.append("path")
      .datum(data)
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5)
      .attr("d", d3.line()
        .x(d => scaleX(d3.isoParse(d.timestamp)))
        .y(d => scaleY(d.data))
      )
  }, []);

  return (
      <div className='w-full h-full grid justify-items-center'>
          {validateData()}
      </div>
  )
}

export default TimeSeriesDashboard;