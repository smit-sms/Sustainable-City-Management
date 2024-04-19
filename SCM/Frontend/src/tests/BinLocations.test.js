import React from 'react';
import { render, screen } from '@testing-library/react';
import { act } from 'react-dom/test-utils';
import CustomFetch from '../utils/customFetch';
import BinLocations from '../Components/BinLocations';

// Mocking Leaflet and its plugin globally
global.L = {
  map: jest.fn(() => ({
    setView: jest.fn(),
    addLayer: jest.fn(),
    removeLayer: jest.fn(),
    hasLayer: jest.fn(),
    on: jest.fn(),
    off: jest.fn(),
    control: {
      layers: jest.fn(() => ({
        addTo: jest.fn(),
        addOverlay: jest.fn(),
      })),
    },
    tileLayer: jest.fn(() => ({
      addTo: jest.fn(),
    })),
    layerGroup: jest.fn(() => ({
      addTo: jest.fn(),
      clearLayers: jest.fn(),
    })),
    marker: jest.fn(() => ({
      bindPopup: jest.fn(() => ({
        openPopup: jest.fn(),
      })),
      addTo: jest.fn(),
    })),
    markerClusterGroup: jest.fn(() => ({
      addTo: jest.fn(),
      clearLayers: jest.fn(),
      addLayer: jest.fn(),
    })),
    divIcon: jest.fn(),
  })),
  icon: jest.fn(),
  tileLayer: jest.fn(),
  control: {
    layers: jest.fn(() => ({
      addTo: jest.fn(),
    })),
  }
};

// MarkerCluster plugin simulation
require('leaflet.markercluster');

// Mock CustomFetch
jest.mock('../utils/customFetch');

jest.mock('react-router-dom', () => ({
    useNavigate: () => jest.fn(),
}));

// Mock navigator.geolocation
global.navigator.geolocation = {
  getCurrentPosition: jest.fn().mockImplementation((success, fail) => success({
    coords: {
      latitude: 53.349805,
      longitude: -6.26031,
    },
  })),
};

describe('BinLocations', () => {
  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    CustomFetch.mockResolvedValue({
      json: () => Promise.resolve({ data: { features: [] } })
    });
  });

  test('renders without crashing', async () => {
    await act(async () => {
      render(<BinLocations />);
    });
    expect(screen.getByText(/BINS/i)).toBeInTheDocument();
  });

  test('fetches bin and waste facility data on mount', async () => {
    await act(async () => {
      render(<BinLocations />);
    });
    expect(CustomFetch).toHaveBeenCalledTimes(1);
  });

  test('initializes current location marker if geolocation is available', async () => {
    await act(async () => {
      render(<BinLocations />);
    });
    expect(navigator.geolocation.getCurrentPosition).toHaveBeenCalled();
  });
});
