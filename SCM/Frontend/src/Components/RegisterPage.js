import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { BASE_URL } from '../services/api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Cookies from 'js-cookie';

const RegisterPage = () => {
  let navigate = useNavigate();

  const [name, setName] = useState('');
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
      const response = await fetch(`${BASE_URL}/auth/register/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, email, password }),
      });

      const data = await response.json();
      if (response.status === 201 || response.status === 200) {
        Cookies.set('access_token', data.access_token);
        Cookies.set('refresh_token', data.refresh_token);
        navigate('/bus');
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
    <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-100 to-green-300">
      <div className="bg-white p-8 rounded-lg shadow-2xl max-w-sm w-full">
        <div className="mb-5">
          <img src="/logo.png" alt="Dashboard Logo" className="h-16 w-16 mx-auto" />
          <h1 className="text-center text-4xl mt-2 mb-8">EcoCity</h1>
        </div>
        <h1 className="text-2xl text-white-800 mt-10 mb-8 text-center">Register</h1>
        <form  onSubmit={handleRegister}>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Name"
              className="text-dark w-full p-2 border rounded border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-600"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required />
          </div>
          <div className="mb-4">
            <input
              type="email"
              placeholder="Email address"
              className="text-dark w-full p-2 border rounded border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-600"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required />
          </div>
          <div className="mb-4">
            <input
              type="password"
              placeholder="Password"
              className="text-dark w-full p-2 border rounded border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-600"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required />
          </div>
          <div className="mb-4">
            <input
              type="password"
              placeholder="Confirm password"
              className="text-dark w-full p-2 border rounded border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-600"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required />
          </div>
          <button
            type="submit"
            className="w-full p-2 bg-green-600 register-button text-white rounded hover:bg-green-700 transition duration-300"
          >
            Register
          </button>
        </form>
        <button
          className="mt-4 text-green-600 hover:text-green-800 transition duration-300 w-full text-center"
          type="button"
          onClick={() => navigate('/')}
        >
          Already have an account? Login
        </button>
      </div>
      <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored" pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
};

export default RegisterPage;
