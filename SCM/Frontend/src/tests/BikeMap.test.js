import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from './';
import LoginPage from '../Components/BikeMap.js';

test('renders dublin bikes map react link', async() => {
  const { getByText } = render(<App />);
  const markerElements = screen.getAllByRole('button');
  expect(markerElements[0]).toBeInTheDocument();
  fireEvent.click(markerElements[2]);
  console.log(markerElements);
  await waitFor(() => {
    expect(getByText(/Available Bikes/i))[0].toBeInTheDocument();
  });
});

