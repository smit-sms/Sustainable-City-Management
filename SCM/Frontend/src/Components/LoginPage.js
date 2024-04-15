import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'js-cookie';
import { BASE_URL } from '../services/api';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const LoginPage = () => {
  let navigate = useNavigate();
  let password_length = 5

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const validateForm = () => {
    let tempErrors = {};
    tempErrors.email = email ? "" : "Email is required.";
    tempErrors.password = password ? "" : "Password is required.";

    if(email && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(email)){
      tempErrors.email = "Email is not valid.";
    }

    if(password && password.length < password_length){
      tempErrors.password = `Password must be at least ${password_length} characters long.`;
    }

    // Use toast for displaying validation errors
    Object.values(tempErrors).forEach(error => {
      if (error) toast.error(error);
    });

    return Object.values(tempErrors).every(x => x === "");
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (validateForm()) {
      try {
        const response = await fetch(`${BASE_URL}/auth/login/`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        if (response.status === 200) {
          Cookies.set('access_token', data.access_token);
          Cookies.set('refresh_token', data.refresh_token);
          navigate('/bus');
        } else if (response.status === 401) {
          toast.error(data.message || 'Invalid credentials, please check and try again');
        } else {
          toast.error('Some Error occurred. Please try again.');
        }
      } catch (error) {
        toast.error('Network error, please try again.');
      }
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-gradient-to-br from-blue-100 to-green-300">
      <div className="bg-white p-8 rounded-lg shadow-2xl max-w-sm w-full">
        <div className="mb-5">
          <img src="/logo.png" alt="Dashboard Logo" className="h-16 w-16 mx-auto"/>
          <h1 className="text-center text-4xl mt-2 mb-8">EcoCity</h1>
        </div>
        <h1 className="text-2xl text-white-800 mt-10 mb-8 text-center">Login</h1>
        <form onSubmit={handleLogin}>
          <div className="mb-4">
            <input
              type="email"
              placeholder="Email address"
              className="text-dark w-full p-2 border rounded border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-600"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="mb-4">
            <input
              type="password"
              placeholder="Password"
              className="w-full p-2 border rounded border-gray-300 focus:outline-none focus:ring-2 focus:ring-green-600"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="w-full p-2 bg-green-600 text-white rounded login-button hover:bg-green-700 transition duration-300"
          >
            Login
          </button>
        </form>
        <button
          className="mt-4 text-green-600 hover:text-green-800 transition duration-300 w-full text-center"
          type="button"
          onClick={() => navigate('/register')}
        >
          Don't have an account? Register here
        </button>
      </div>
      <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored" pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
};

export default LoginPage;
