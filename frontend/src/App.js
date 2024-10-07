import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import ChatListPage from "./pages/ChatListPage";
import ChatPage from "./pages/ChatPage";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import "./styles/App.css";
import "highlight.js/styles/sunburst.css";
import { useUser } from "./hooks/useUser";

function App() {
  const { user, loading, error } = useUser(); // Gunakan hook useUser


  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <main>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              path="/"
              element={
                user ? (
                  <HomePage userId={user.id} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/chats"
              element={
                user ? (
                  <ChatListPage userId={user.id} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
            <Route
              path="/chat/:chatId"
              element={
                user ? (
                  <ChatPage userId={user.id} />
                ) : (
                  <Navigate to="/login" replace />
                )
              }
            />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
export default App;
