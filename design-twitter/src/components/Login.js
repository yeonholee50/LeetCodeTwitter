import React, { useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import "./styles/Login.css";

const Login = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");

  const handleLogin = async () => {
    try {
      const response = await axios.post("http://localhost:8000/login", { email, password });
      setMessage(response.data.message);
      localStorage.setItem("token", response.data.token);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Login failed");
    }
  };

  return (
    <div className="login-container">
      <h1>Login</h1>
      <input
        type="email"
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <br />
      <input
        type="password"
        placeholder="Password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
      />
      <br />
      <button onClick={handleLogin}>Login</button>
      <p className="message">{message}</p>
      <p>
        Don't have an account?{" "}
        <Link to="/signup" className="signup-link">
          Click here to sign up.
        </Link>
      </p>
    </div>
  );
};

export default Login;

