import React from "react";
import { Link } from "react-router-dom";
import "./styles/Home.css";
import twitterLogo from './twitterlogo.png'
import { Helmet } from "react-helmet";

const Home = () => {
  return (
    <div className="home-container">
        <Helmet>
        <link rel="icon" href="./twitterlogo.png" type="image/png" size="16x16"/>
        <title>Leetcode Twitter</title>
        
      </Helmet>
      <img src={twitterLogo} alt="Twitter Logo" className="twitter-logo" />
      <h1>Welcome to Leetcode Twitter</h1>
      <p>A Meme Project Inspired From a System Design Leetcode Problem</p>
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
