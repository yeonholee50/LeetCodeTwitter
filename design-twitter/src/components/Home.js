import React from "react";
import { Link } from "react-router-dom";
import "./styles/Home.css";

const Home = () => {
  return (
    <div className="home-container">
      <h1>Welcome to Design Twitter</h1>
      <p>The platform where ideas fly! Connect, share, and explore.</p>
      <div>
        <Link to="/login">
          <button>Login</button>
        </Link>
        <Link to="/signup">
          <button>Sign Up</button>
        </Link>
      </div>
    </div>
  );
};

export default Home;
