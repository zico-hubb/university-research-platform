import React, { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import axios from "../services/api";
import { useNavigate } from "react-router-dom";
import "../assets/styles.css";

function Dashboard() {
  const { user, logout } = useAuth();
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    if (!user?.token) {
      logout();
      navigate("/login");
      return;
    }
    fetchPosts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const res = await axios.get("/research", {
        headers: { Authorization: `Bearer ${user.token}` },
      });

      setPosts(res.data.posts || []);
    } catch (err) {
      console.error("Error fetching research posts:", err);
      if (err.response?.status === 422 || err.response?.status === 401) {
        logout();
        navigate("/login");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      <header className="dashboard-header">
        <h1>Welcome, {user?.name || "Professor"}</h1>
        <div>
          <button onClick={() => navigate("/create")}>New Post</button>
          <button onClick={logout} className="logout-btn">
            Logout
          </button>
        </div>
      </header>

      <main>
        <h2>Research Posts in {user?.field || "your field"}</h2>
        {loading ? (
          <p>Loading...</p>
        ) : posts.length === 0 ? (
          <p>No posts yet.</p>
        ) : (
          <div className="posts-list">
            {posts.map((post) => (
              <div key={post.id} className="post-card">
                <h3>{post.title}</h3>
                <p>{post.content}</p>
                <small>
                  By {post.author_name} on{" "}
                  {new Date(post.created_at).toLocaleString()}
                </small>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default Dashboard;
