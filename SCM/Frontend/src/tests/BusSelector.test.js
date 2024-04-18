import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import BusSelector from '../Components/BusSelector/BusSelector';

jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

beforeAll(() => {
  global.fetch = jest.fn();
});

beforeEach(() => {
  fetch.mockClear().mockResolvedValueOnce({
    ok: true,
    json: async () => ({ data: [{ route_id: '1', bus_name: 'Bus 1' }, { route_id: '2', bus_name: 'Bus 2' }] }),
    headers: {
      get: jest.fn().mockReturnValue('application/json'),
    },
  });
});


test('loads and displays buses', async () => {
  const mockBuses = [
    { route_id: '1', bus_name: 'Bus 1' },
    { route_id: '2', bus_name: 'Bus 2' },
  ];

  fetch.mockResolvedValueOnce({
    ok: true,
    json: async () => ({ data: mockBuses }),
  });

  render(<BusSelector />);

  for (const bus of mockBuses) {
    await screen.findByText(bus.bus_name);
  }

  expect(fetch).toHaveBeenCalledTimes(1);
});


