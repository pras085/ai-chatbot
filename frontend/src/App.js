import React from "react";
import {
  BrowserRouter as Router,
  Route,
  Routes,
  Navigate,
} from "react-router-dom";
import ChatListPage from "./pages/ChatListPage";
import ChatPage from "./pages/ChatPage";
import "./styles/App.css";
import "highlight.js/styles/sunburst.css";
import { ReactComponent as MuatmuatIcon } from "./assets/logo-muatmuat.svg";

function App() {
  const userId = "1";

  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <div>
            <MuatmuatIcon />
          </div>
        </header>
        <main>
          <Routes>
            <Route path="/chats" element={<ChatListPage userId={userId} />} />
            <Route
              path="/chat/:chatId"
              element={<ChatPage userId={userId} />}
            />
            <Route path="/" element={<Navigate to="/chats" replace />} />{" "}
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
