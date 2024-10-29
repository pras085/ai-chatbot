import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/LoginPage.css";
import { login } from "../services/api";

function LoginPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);  // State untuk loading
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");   // Reset error sebelum login
    setLoading(true); // Set loading menjadi true saat proses login dimulai

    try {
      const response = await login(username, password);

      // Pengecekan respons dengan optional chaining
      if (response?.detail) {
        setError(response?.detail);
      } else if (response?.access_token) {
        navigate("/home");
      } else {
        setError("Unexpected error occurred");
      }
    } catch (error) {
      setError("Invalid username or password");
    } finally {
      setLoading(false);  // Set loading menjadi false setelah proses selesai
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username:</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password:</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        {error && <p className="error-message">{error}</p>}

        <button type="submit" disabled={loading} className="button-login">
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>
    </div>
  );
}

export default LoginPage;
