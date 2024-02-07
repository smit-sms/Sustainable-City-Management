import { render, screen } from '@testing-library/react';
import TimeSeriesDashboard from '../Components/TimeSeriesDashboard';
import { dummyDataRaw, dummyData } from '../DummyData/air';

test("Input data is required.", () => {
    render(<TimeSeriesDashboard />);
    const errorMessage = screen.queryByText('Please provide data to generate the dashboard.');
    expect(errorMessage).toBeVisible();
});

test("Input data must be of format [{timestamp: <date_time>, data: <float>}, ...].", () => {
    render(<TimeSeriesDashboard data={dummyDataRaw}/>);
    const errorMessage = screen.queryByText('Incorrect data format. Expected data = [{timestamp: <date_time>, data: <float>}, ...].');
    expect(errorMessage).toBeVisible();
});

// test("If valid data was input then an SVG element must appear on the screen with id #plot-line", () => {
//     render(<TimeSeriesDashboardPage data={dummyData}/>);
//     const plotLineSvg = screen.queryByTestId('plot-line');
//     expect(plotLineSvg).toBeInTheDocument();
// });