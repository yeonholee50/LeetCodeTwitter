import React, { useState } from "react";
import axios from "axios";
import "./styles/Signup.css";
import "./styles/Profile.css";
import { Link, useNavigate } from "react-router-dom";


const Signup = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleSignup = async () => {
    try {
      const response = await axios.post('https://design-twitter.onrender.com/signup', { username, password });
      setMessage(response.data.message);
      localStorage.setItem("token", response.data.token);
      navigate("/profile");
    } catch (error) {
      console.error("Error during signup:", error); // Add this line for debugging
      setMessage(error.response?.data?.detail || "Signup failed");
    }
  };

  return (
    <div className="signup-container">
      <h1>Sign Up</h1>
      <input
        type="text"
        placeholder="Username"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
      />
      <br />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <br />
      <button onClick={handleSignup}>Sign Up</button>
      <p className="message">{message}</p>
    </div>
  );
};

export default Signup;