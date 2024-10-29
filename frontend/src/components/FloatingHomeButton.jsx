import React from 'react';
import { Home } from 'lucide-react';
import { useNavigate, useLocation } from 'react-router-dom';

const FloatingHomeButton = () => {
  const navigate = useNavigate();
  const location = useLocation();

  // Jangan tampilkan button jika sudah di halaman home atau login
  if (location.pathname === '/home' || location.pathname === '/login') {
    return null;
  }

  return (
    <button
      onClick={() => navigate('/home')}
      className="fixed bottom-6 right-6 p-4 bg-blue-500 hover:bg-blue-600 text-white rounded-full shadow-lg transition-all duration-300 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-blue-400 focus:ring-offset-2 z-50"
      aria-label="Go to home"
    >
      <Home size={24} />
    </button>
  );
};

export default FloatingHomeButton;