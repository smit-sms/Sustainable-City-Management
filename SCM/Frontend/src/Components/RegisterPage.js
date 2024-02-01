// import React, { useState } from 'react';
// import '../assets/styles/style.css'; // Make sure to create a LoginPage.css file with the styles
// import { useNavigate } from 'react-router-dom';

// const RegisterPage = () => {
//   let navigate = useNavigate();
  
//   const [email, setEmail] = useState('');
//   const [password, setPassword] = useState('');
//   const [confirmPassword, setConfirmPassword] = useState('');
//   const [errors, setErrors] = useState({});

//   const handleRegister = (e) => {
//     e.preventDefault();
//     if (password !== confirmPassword) {
//       return;
//     }
//     // Proceed with the registration logic
//   };

//   const validate = () => {
//     let tempErrors = {};
//     tempErrors.email = email ? "" : "Email is required";
//     tempErrors.password = password ? "" : "Password is required";
//     tempErrors.confirmPassword = confirmPassword ? "" : "Confirm password is required";
    
//     if (email && !/^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i.test(email)) {
//       tempErrors.email = "Email is not valid";
//     }

//     if (password && password !== confirmPassword) {
//       tempErrors.confirmPassword = "Passwords do not match";
//     }

//     setErrors(tempErrors);
//     return Object.values(tempErrors).every(x => x === "");
//   };

//   return (
//     <div className="login-container">
//       <div className="login-form-container">
//         <h1>Register</h1>
//         <form onSubmit={handleRegister}>
//           <input
//             type="email"
//             placeholder="email address"
//             value={email}
//             onChange={(e) => setEmail(e.target.value)}
//             required
//           />
//           <input
//             type="password"
//             placeholder="password"
//             value={password}
//             onChange={(e) => setPassword(e.target.value)}
//             required
//           />
//           <input
//             type="password"
//             placeholder="confirm password"
//             value={confirmPassword}
//             onChange={(e) => setConfirmPassword(e.target.value)}
//             required
//           />
//           {errors.password && <p className="error">{errors.password}</p>}
//           <input
//             type="password"
//             placeholder="confirm password"
//             value={confirmPassword}
//             onChange={(e) => setConfirmPassword(e.target.value)}
//             required
//           />
//           {errors.confirmPassword && <p className="error">{errors.confirmPassword}</p>}
//           <button onClick={() => navigate('/home')}>REGISTER</button>
//         </form>
//         <button className="signup-link" onClick={() => navigate('/')}>
//           Already have an account? Login
//         </button>
//       </div>
//     </div>
//   );
// };

// export default RegisterPage;
