import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LoginPage from '../Components/LoginPage';
import { MemoryRouter } from 'react-router-dom';


const mockedNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockedNavigate,
}));

describe('LoginPage', () => {
  beforeEach(() => {
    mockedNavigate.mockReset();
    // eslint-disable-next-line testing-library/no-render-in-setup
    render(<LoginPage />, { wrapper: MemoryRouter });
  });

  test('renders login form', () => {
    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();
  });

  test('allows user to enter email and password', () => {
    const emailInput = screen.getByPlaceholderText('Email address');
    const passwordInput = screen.getByPlaceholderText('Password');
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    
    expect(emailInput.value).toBe('test@example.com');
    expect(passwordInput.value).toBe('password123');
  });

  test('displays error when the email is invalid', () => {
    const emailInput = screen.getByPlaceholderText('Email address');
    fireEvent.change(emailInput, { target: { value: 'invalidmail' } });
    fireEvent.submit(screen.getByRole('button', { name: 'Login' }));

    expect(screen.getByText('Email is not valid.')).toBeInTheDocument();
  });

  test('displays error when the email is empty', () => {
    const emailInput = screen.getByPlaceholderText('Email address');
    fireEvent.change(emailInput, { target: { value: '' } });
    fireEvent.submit(screen.getByRole('button', { name: 'Login' }));

    expect(screen.getByText('Email is required.')).toBeInTheDocument();
  });

  test('displays error when the password is too short', () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.submit(screen.getByRole('button', { name: 'Login' }));

    expect(screen.getByText('Password must be at least 5 characters long.')).toBeInTheDocument();
  });

  test('displays error when the password is empty', () => {
    const passwordInput = screen.getByPlaceholderText('Password');
    fireEvent.change(passwordInput, { target: { value: '' } });
    fireEvent.submit(screen.getByRole('button', { name: 'Login' }));

    expect(screen.getByText('Password is required.')).toBeInTheDocument();
  });
});
