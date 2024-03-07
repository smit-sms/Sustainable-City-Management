import React, { useState } from 'react';
import '../assets/styles/style.css';
import { useNavigate } from 'react-router-dom';
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
        const response = await fetch(`${BASE_URL}/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        console.log(response.status);
        if (response.status === 200) {
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
    <div className="login-container">
      <div className="login-form-container">
        <h1>Login</h1>
        <form onSubmit={handleLogin}>
          <div>
            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Login</button>
        </form>
        <button className="signup-link" type="button" onClick={() => navigate('/register')}>Register</button>
      </div>
      <ToastContainer position="top-right" autoClose={5000} hideProgressBar={false} newestOnTop={false} closeOnClick rtl={false} theme="colored" pauseOnFocusLoss draggable pauseOnHover />
    </div>
  );
};

export default LoginPage;
