import React from 'react';
import { render, fireEvent, waitFor, screen } from '@testing-library/react';
import RegisterPage from '../Components/RegisterPage';

jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
}));

test('renders learn react link', () => {
  console.log("Register Page Tests...");
});


describe('RegisterPage Component', () => {
  test('should render RegisterPage correctly', () => {
    render(<RegisterPage />);
    
    expect(screen.getByPlaceholderText('Name')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email address')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Confirm password')).toBeInTheDocument();
  });

  test('should show error message if passwords do not match', async () => {
    render(<RegisterPage />);
    
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password1' } });
    fireEvent.change(screen.getByPlaceholderText('Confirm password'), { target: { value: 'password2' } });
    fireEvent.submit(screen.getByPlaceholderText('Confirm password'));

    await waitFor(() => {
      expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    });
  });

  test('should handle API error and display error message', async () => {
    // Mocking fetch API to simulate an error response
    jest.spyOn(global, 'fetch').mockImplementation(() =>
      Promise.resolve({
        json: () => Promise.resolve({ message: 'Error message from API' }),
        status: 401,
      })
    );

    render(<RegisterPage />);
    
    fireEvent.change(screen.getByPlaceholderText('Name'), { target: { value: 'John Doe' } });
    fireEvent.change(screen.getByPlaceholderText('Email address'), { target: { value: 'john.doe@example.com' } });
    fireEvent.change(screen.getByPlaceholderText('Password'), { target: { value: 'password123' } });
    fireEvent.change(screen.getByPlaceholderText('Confirm password'), { target: { value: 'password123' } });
    fireEvent.submit(screen.getByPlaceholderText('Confirm password'));

    await waitFor(() => {
      expect(screen.getByText('Error message from API')).toBeInTheDocument();
    });

    // Restore fetch API to its original implementation
    global.fetch.mockRestore();
  });

});
