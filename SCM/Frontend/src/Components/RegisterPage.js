import React, { useState } from 'react';
import '../assets/styles/style.css'; // Make sure to create a LoginPage.css file with the styles
import { useNavigate } from 'react-router-dom';

const RegisterPage = () => {
  let navigate = useNavigate();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleRegister = (e) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      return;
    }
    // Proceed with the registration logic
  };

  return (
    <div className="login-container">
      <div className="login-form-container">
        <h1>Register</h1>
        <form onSubmit={handleRegister}>
          <input
            type="email"
            placeholder="email address"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="confirm password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <button onClick={() => navigate('/home')}>REGISTER</button>
        </form>
        <button className="signup-link" onClick={() => navigate('/')}>
          Already have an account? Login
        </button>
      </div>
    </div>
  );
};

export default RegisterPage;
