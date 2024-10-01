import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ChatListPage from "./pages/ChatListPage";
import ChatPage from "./pages/ChatPage";
import "./styles/App.css";
import "highlight.js/styles/sunburst.css";
import HomePage from "./pages/HomePage";

function App() {
  const userId = "1";

  return (
    <Router>
      <div className="App">
        <main>
          <Routes>
            <Route path="/chats" element={<ChatListPage userId={userId} />} />
            <Route
              path="/chat/:chatId"
              element={<ChatPage userId={userId} />}
            />
            <Route path="/" element={<HomePage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
