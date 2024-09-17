import ChatApp from "./components/ChatApp";
import "./styles/App.css";
import "highlight.js/styles/sunburst.css";
// import { v4 as uuidv4 } from "uuid"; // Pastikan untuk menginstal package uuid

/**
 * App Component
 *
 * Komponen utama aplikasi yang menampung seluruh aplikasi chat.
 * Bertanggung jawab untuk:
 * - Menyediakan struktur dasar aplikasi
 * - Menginisialisasi dan menyimpan userId
 * - Merender komponen ChatApp yang mengelola seluruh fungsionalitas chat
 */

function App() {
  const userId = "1";
  return (
    <div className="App">
      <header className="App-header">
        <h1>Chatbot AI</h1>
      </header>
      <main>{userId && <ChatApp userId={userId} />}</main>
    </div>
  );
}

export default App;
