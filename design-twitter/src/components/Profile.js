import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./styles/Profile.css";

const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [feed, setFeed] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [tweetContent, setTweetContent] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");

    // If no token, redirect to login
    if (!token) {
      setMessage("Unauthorized. Please log in.");
      navigate("/login");
      return;
    }

    const fetchProfileData = async () => {
      try {
        const config = {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        };

        const profileResponse = await axios.get("https://design-twitter.onrender.com/profile", config);
        const feedResponse = await axios.get("https://design-twitter.onrender.com/feed", config);

        setUserData(profileResponse.data);
        setFeed(feedResponse.data);
      } catch (error) {
        if (error.response?.status === 401) {
          setMessage("Session expired. Please log in again.");
          localStorage.removeItem("token");
          navigate("/login");
        } else {
          setMessage(error.response?.data?.detail || "Failed to load profile or feed.");
        }
      }
    };

    fetchProfileData();
  }, [navigate]);

  const handleSearch = async () => {
    const token = localStorage.getItem("token");
    try {
      const config = {
        headers: {
            Authorization: `Bearer ${token}`,
        },
      };
      const response = await axios.get(`https://design-twitter.onrender.com/search?prefix=${searchQuery}`, config);
      setSearchResults(response.data);
    } catch (error) {
      setMessage(error.response?.data?.detail || "Search failed.");
    }
  };

  const handleTweet = async () => {
    const token = localStorage.getItem("token");
    try {
      const config = {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      };
      await axios.post(
        "https://design-twitter.onrender.com/tweet",
        { content: tweetContent },
        config
      );
      setMessage("Tweet posted!");
      setTweetContent(""); // Clear the tweet input
    } catch (error) {
      setMessage(error.response?.data?.detail || "Failed to post tweet.");
    }
  };

  return (
    <div className="profile-container">
      <h1>Welcome, {userData?.username}</h1>
      {message && <p className="error-message">{message}</p>}

      <div className="tweet-section">
        <h2>Create a Tweet</h2>
        <textarea
          value={tweetContent}
          onChange={(e) => setTweetContent(e.target.value)}
          placeholder="What's on your mind?"
        />
        <button onClick={handleTweet}>Tweet</button>
      </div>

      <div className="search-section">
        <h2>Search</h2>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search by username"
        />
        <button onClick={handleSearch}>Search</button>
        {searchResults.length > 0 && (
          <ul>
            {searchResults.map((result) => (
              <li key={result.id}>{result.username}</li>
            ))}
          </ul>
        )}
      </div>

      <div className="feed-section">
        <h2>Your Feed</h2>
        {feed.length > 0 ? (
          <ul>
            {feed.map((post) => (
              <li key={post.id}>
                <strong>{post.username}:</strong> {post.content}
              </li>
            ))}
          </ul>
        ) : (
          <p>No posts to show.</p>
        )}
      </div>
    </div>
  );
};

export default Profile;
