import React from 'react';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import BikeMap from '../Components/BikeMap';
import CustomFetch from '../utils/customFetch';

// Mocks
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

jest.mock('react-leaflet', () => ({
  MapContainer: ({ children }) => <div>{children}</div>,
  TileLayer: () => <div></div>,
  Marker: () => <div></div>,
  Popup: ({ children }) => <div>{children}</div>,
}));

jest.mock('leaflet', () => ({
  icon: jest.fn(),
}));

jest.mock('../utils/customFetch');


describe('BikeMap', () => {
  beforeEach(() => {
    // Setup CustomFetch to return a promise that resolves to a mock response
    CustomFetch.mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          data: {
            prediction: [],
            positions: []
          }
        }),
        status: 200
      })
    );

    const testDate = new Date();
    jest.useFakeTimers().setSystemTime(testDate);
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  test('Renders without crashing', async () => {
    await act(async () => {
      render(<BikeMap />);
    });
    expect(screen.getByText(/DUBLIN BIKES/i)).toBeInTheDocument();
  });

  test('UI components are present', async () => {
    await act(async () => {
      render(<BikeMap />);
    });
    expect(screen.getByText(/Select time to view predictions:/i)).toBeInTheDocument();
    expect(screen.getByRole('textbox')).toBeInTheDocument();
  });

  beforeEach(() => {
    // General setup that could be overwritten in specific tests
    CustomFetch.mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          data: {
            prediction: [],
            positions: []
          }
        }),
        status: 200
      })
    );
  });
  
  test('fetches prediction data on mount and updates the state', async () => {
    // Setup a successful fetch scenario specific to this test
    CustomFetch.mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({
          data: {
            prediction: [],
            positions: []
          }
        }),
        status: 200
      })
    );
  
    await act(async () => {
      render(<BikeMap />);
    });

    expect(CustomFetch).toHaveBeenCalled();  
  });
});
