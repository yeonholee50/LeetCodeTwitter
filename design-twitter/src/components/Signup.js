import React, { useState } from "react";
import axios from "axios";
import "./styles/Signup.css";
import "./styles/Profile.css";
import { Link, useNavigate } from "react-router-dom";

const global_link = "https://design-twitter.onrender.com/";

const Signup = () => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const decrementTimeDelta = async (token) => {
    try {
      const config = {
        headers: {
          token: token,
        },
      };
      await axios.post(`${global_link}decrement_time_delta`, {}, config);
    } catch (error) {
      console.error("Error decrementing time_delta:", error);
    }
  };

  const handleSignup = async () => {
    try {
      const response = await axios.post(`${global_link}signup`, { username, password });
      setMessage(response.data.message);
      const token = response.data.token;
      if (token) {
        localStorage.setItem("token", token);
        await decrementTimeDelta(token);
        navigate("/profile");
      }
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
      <p>
        Already have an account?{" "}
        <Link to="/login" className="login-link">
          Click here to login.
        </Link>
      </p>
    </div>
  );
};

export default Signup;