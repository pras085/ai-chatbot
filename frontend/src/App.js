import React from "react";
import ChatContainer from "./components/ChatContainer";
import "./styles/App.css";
import "highlight.js/styles/default.css"; // TODO : ganti react-highiliter nnti

/**
 * App Component
 *
 * Komponen utama yang menginisialisasi aplikasi chat.
 * Ini adalah titik masuk utama untuk aplikasi React.
 */
function App() {
  return (
    <div className="App">
      <ChatContainer />
    </div>
  );
}

export default App;
