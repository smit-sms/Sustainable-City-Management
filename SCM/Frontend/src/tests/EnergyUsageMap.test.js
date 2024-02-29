// EnergyUsageMap.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom/extend-expect';
import EnergyUsageMap from './EnergyUsageMap';
import fetchMock from 'jest-fetch-mock';

// Mocks for map and leaflet
jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }) => <div>{children}</div>,
  TileLayer: () => <div></div>,
  Marker: () => <div></div>,
  Popup: () => <div></div>,
  GeoJSON: () => <div></div>,
}));
jest.mock('leaflet', () => ({
  Icon: jest.fn(),
}));

// Mock for fetch calls
fetchMock.enableMocks();

beforeEach(() => {
  fetch.resetMocks();
});

// Checking for specific elements int the component
describe('EnergyUsageMap Component Tests', () => {
  test('renders EnergyUsageMap component', () => {
    render(<EnergyUsageMap />);
    expect(screen.getByText(/Latest weather statistics:/i)).toBeInTheDocument();
  });

  //Check if the weather dat fetch is working properly
  test('fetches weather data successfully', async () => {
    const mockWeatherData = {
      weatherDescription: "Clear skies",
      windSpeed: 5,
      rainfall: 0,
    };
    fetch.mockResponseOnce(JSON.stringify([mockWeatherData]));

    render(<EnergyUsageMap />);
    await waitFor(() => expect(fetch).toHaveBeenCalledTimes(1));
    expect(screen.getByText(/Clear skies/i)).toBeInTheDocument();
  });

  //Check if chaging the sliders work properly
  test('handleSliderChange updates slider value', () => {
    const { getByTestId } = render(<EnergyUsageMap />);
    // Assuming you add data-testid attributes to your sliders for the test
    const slider = getByTestId('slider-test-id');
    fireEvent.change(slider, { target: { value: '50' } });
    expect(slider.value).toBe('50');
  });

  // Additional tests can be written here to cover more functionality
});

