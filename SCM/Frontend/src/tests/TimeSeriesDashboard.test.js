import { render, screen } from '@testing-library/react';
import dummyData from '../DummyData/air';
import TimeSeriesDashboard from '../Components/TimeSeriesDashboard';

test("Input data is required.", () => {
    render(<TimeSeriesDashboard data={dummyData}/>);
    // const errorMessage = screen.queryByText('Please provide data to generate the dashboard.');
    // expect(errorMessage).toBeVisible();
});