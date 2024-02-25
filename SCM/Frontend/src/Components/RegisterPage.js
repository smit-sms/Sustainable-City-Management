import React, { useState } from 'react';
import '../assets/styles/style.css';
import { useNavigate } from 'react-router-dom';
import { BASE_URL } from '../services/api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const RegisterPage = () => {
  let navigate = useNavigate();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    try {
      const response = await fetch(`${BASE_URL}/auth/signup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (response.status === 201) {
        navigate('/home');
      } else if (response.status === 400) {
        toast.error(data.message || 'Already existing user');
      } else if (response.status === 401) {
        toast.error(data.message || 'User not authorized, please contact your administrator for access.');
      } else {
        toast.error('Some Error occurred. Please try again.');
      }
    } catch (error) {
      toast.error('Network error, please try again.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form-container">
        <h1>Register</h1>
        <form onSubmit={handleRegister}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="email"
            placeholder="Email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <button type="submit">Register</button>
        </form>
        <button className="signup-link" onClick={() => navigate('/')}>
          Already have an account? Click here to Login
        </button>
      </div>
      <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored"  pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
};

export default RegisterPage;

