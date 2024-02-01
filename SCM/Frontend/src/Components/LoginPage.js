import React, { useState } from 'react';
import '../assets/styles/style.css'; // Ensure your CSS file path is correct
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
  let navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState({});

  const validateForm = () => {
    let tempErrors = {};
    tempErrors.email = email ? "" : "Email is required.";
    tempErrors.password = password ? "" : "Password is required.";

    // Check if email follows the right format (simple regex for example purposes)
    if(email && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(email)){
      tempErrors.email = "Email is not valid.";
    }

    // Check if password meets minimum length criteria
    if(password && password.length < 6){
      tempErrors.password = "Password must be at least 6 characters long.";
    }

    setErrors({...tempErrors});
    return Object.values(tempErrors).every(x => x === "");
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if(validateForm()){
      // proceed with login (e.g., API call)
      navigate('/home');
    } else {
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
              placeholder="email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            {errors.email && <div className="error">{errors.email}</div>}
          </div>
          <div>
            <input
              type="password"
              placeholder="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            {errors.password && <div className="error">{errors.password}</div>}
          </div>
          <button type="submit">LOGIN</button>
        </form>
        <button className="signup-link" type="button" onClick={() => navigate('/register')}>Register</button>
      </div>
    </div>
  );
};

export default LoginPage;
