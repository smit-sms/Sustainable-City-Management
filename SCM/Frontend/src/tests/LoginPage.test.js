import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from '../Components/LoginPage';
import { MemoryRouter } from 'react-router-dom'; // Required for useNavigate

// Mock useNavigate hook
const mockedNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'), // use actual for all non-hook parts
  useNavigate: () => mockedNavigate,
}));

describe('LoginPage', () => {
  beforeEach(() => {
    // Reset the mocked navigate function before each test
    mockedNavigate.mockReset();

    // Render the component before each test
    render(<LoginPage />, { wrapper: MemoryRouter }); // wrap in MemoryRouter for routing
  });

  test('renders login form', () => {
    const emailInput = screen.getByPlaceholderText('email address');
    const passwordInput = screen.getByPlaceholderText('password');
    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();
  });

  test('allows user to enter email and password', () => {
    const emailInput = screen.getByPlaceholderText('email address');
    const passwordInput = screen.getByPlaceholderText('password');
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  test('navigates to home on successful login', () => {
    const emailInput = screen.getByPlaceholderText('email address');
    const passwordInput = screen.getByPlaceholderText('password');
    const loginButton = screen.getByRole('button', { name: 'LOGIN' });

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(loginButton);

    expect(mockedNavigate).toHaveBeenCalledWith('/home');
  });

  test('displays error when the email is invalid', () => {
    const emailInput = screen.getByPlaceholderText('email address');
    fireEvent.change(emailInput, { target: { value: 'invalidemail' } });
    fireEvent.submit(screen.getByRole('button', { name: 'LOGIN' }));

    expect(screen.getByText('Email is not valid.')).toBeInTheDocument();
  });

  test('displays error when the email is empty', () => {
    const emailInput = screen.getByPlaceholderText('email address');
    fireEvent.change(emailInput, { target: { value: '' } });
    fireEvent.submit(screen.getByRole('button', { name: 'LOGIN' }));

    expect(screen.getByText('Email is required.')).toBeInTheDocument();
  });

  test('displays error when the password is too short', () => {
    const passwordInput = screen.getByPlaceholderText('password');
    fireEvent.change(passwordInput, { target: { value: '123' } }); // Less than 6 characters
    fireEvent.submit(screen.getByRole('button', { name: 'LOGIN' }));

    expect(screen.getByText('Password must be at least 6 characters long.')).toBeInTheDocument();
  });

  test('displays error when the password is empty', () => {
    const passwordInput = screen.getByPlaceholderText('password');
    fireEvent.change(passwordInput, { target: { value: '' } });
    fireEvent.submit(screen.getByRole('button', { name: 'LOGIN' }));

    expect(screen.getByText('Password is required.')).toBeInTheDocument();
  });

  // ... Additional tests for validation errors

  // Add more tests as needed
});
