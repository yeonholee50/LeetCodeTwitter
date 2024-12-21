import React, { useState, useEffect } from "react";
import axios from "axios";
import "./styles/Profile.css";

const Profile = () => {
  const [search, setSearch] = useState("");
  const [users, setUsers] = useState([]);
  const [tweet, setTweet] = useState("");
  const [feed, setFeed] = useState([]);
  const [message, setMessage] = useState("");

  const token = localStorage.getItem("token");

  const searchUsers = async () => {
    try {
      const response = await axios.get(`https://design-twitter.onrender.com/search?prefix=${search}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(response.data);
    } catch (error) {
      setMessage("Error searching users");
    }
  };

  const followUser = async (username) => {
    try {
      const response = await axios.post(
        "http://localhost:8000/follow",
        { target_username: username },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error following user");
    }
  };

  const unfollowUser = async (username) => {
    try {
      const response = await axios.post(
        "http://localhost:8000/unfollow",
        { target_username: username },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error unfollowing user");
    }
  };

  const postTweet = async () => {
    try {
      const response = await axios.post(
        "http://localhost:8000/tweet",
        { content: tweet, timestamp: Date.now() / 1000 },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setMessage(response.data.message);
      setTweet("");
      loadFeed();
    } catch (error) {
      setMessage("Error posting tweet");
    }
  };

  const loadFeed = async () => {
    try {
      const response = await axios.get("http://localhost:8000/feed", {
        headers: { Authorization: `Bearer ${token}` },
      });
      setFeed(response.data);
    } catch (error) {
      setMessage("Error loading feed");
    }
  };

  useEffect(() => {
    loadFeed();
  }, []);

  return (
    <div className="profile-container">
      <h1>Profile</h1>
      <div>
        <input
          type="text"
          placeholder="Search users"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <button onClick={searchUsers}>Search</button>
      </div>
      <div>
        {users.map((user) => (
          <div key={user}>
            {user}
            <button onClick={() => followUser(user)}>Follow</button>
            <button onClick={() => unfollowUser(user)}>Unfollow</button>
          </div>
        ))}
      </div>
      <div>
        <textarea
          placeholder="What's happening?"
          value={tweet}
          onChange={(e) => setTweet(e.target.value)}
        />
        <button onClick={postTweet}>Tweet</button>
      </div>
      <div>
        <h2>Feed</h2>
        {feed.map((tweet) => (
          <div key={tweet.timestamp}>
            <p><strong>{tweet.username}</strong>: {tweet.content}</p>
            <p>{new Date(tweet.timestamp * 1000).toLocaleString()}</p>
          </div>
        ))}
      </div>
      <p className="message">{message}</p>
    </div>
  );
};

export default Profile;