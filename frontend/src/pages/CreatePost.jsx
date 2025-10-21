import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import axios from "../services/api";
import { useNavigate } from "react-router-dom";

function CreatePost() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title || !content) return setError("All fields are required");

    try {
      setLoading(true);
      setError("");

      const res = await axios.post(
        "/research",
        { title, content },
        { headers: { Authorization: `Bearer ${user.token}` } }
      );

      console.log("Post created:", res.data.post);
      navigate("/dashboard");
    } catch (err) {
      console.error("Error creating post:", err);
      if (err.response?.status === 401 || err.response?.status === 422) {
        logout();
        navigate("/login");
      } else {
        setError(err.response?.data?.error || "Failed to create post");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-post-container">
      <h2>Create New Research Post</h2>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Title"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />
        <textarea
          placeholder="Content"
          value={content}
          onChange={(e) => setContent(e.target.value)}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Posting..." : "Create Post"}
        </button>
      </form>
    </div>
  );
}

export default CreatePost;
