import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import BusMap from './BusMap';

jest.mock('react-leaflet', () => ({
  MapContainer: () => <div>MapContainer Mock</div>,
  TileLayer: () => <div>TileLayer Mock</div>,
  Marker: () => <div>Marker Mock</div>,
  Popup: () => <div>Popup Mock</div>,
  GeoJSON: () => <div>GeoJSON Mock</div>,
  useMapEvents: jest.fn(),
}));

jest.mock('leaflet', () => ({
  ...jest.requireActual('leaflet'),
  geoJSON: () => ({
    getBounds: () => ({}),
  }),
}));

describe('BusMap Component', () => {
  test('renders without crashing', () => {

    const selectedBusRoute = { data: { features: [] } };
    const selectedBus = "Bus 1";


    render(<BusMap selectedBusRoute={selectedBusRoute} selectedBus={selectedBus} />);

    expect(screen.getByText('MapContainer Mock')).toBeInTheDocument();
  });
});
