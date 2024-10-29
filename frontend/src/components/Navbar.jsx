import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { ReactComponent as MuatmuatIcon } from "../assets/logo-muatmuat.svg";
import { useNavigate } from 'react-router-dom';

const NavigationBar = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await apiRequest("/logout", { method: "POST" });
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      navigate("/login");
    } catch (error) {
      console.error("Logout failed:", error);
      localStorage.removeItem("token");
      localStorage.removeItem("username");
      navigate("/login");
    }
  };

  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };

  const handleClickOutside = () => {
    setIsDropdownOpen(false);
  };

  if (location.pathname === '/login') {
    return null;
  }

  return (
    <nav className="h-16 bg-white border-b border-gray-200">
      <div className="h-full px-4 flex items-center justify-between">
        {/* Left side - Logo and Navigation */}
        <div className="flex items-center space-x-8">
          {/* Logo */}
        <MuatmuatIcon viewBox='0 0 35 14' width={46} height={46} />

          {/* Navigation Links */}
          <div className="flex items-center space-x-6">
            <a href="#" className="text-blue-600 font-medium border-b-2 border-blue-600 py-4">
              Home
            </a>
            <a href="#" className="text-gray-600 hover:text-gray-900 py-4">
              Dashboard
            </a>
          </div>
        </div>

        {/* Right side - Notification and Profile */}
        <div className="flex items-center space-x-4">
          {/* Notification Bell */}
          <button 
            className="p-2 text-gray-600 hover:text-gray-900 rounded-full hover:bg-gray-100"
            onClick={() => {/* Handle notification click */}}
          >
            <Bell size={20} />
          </button>

          {/* Profile Dropdown */}
          <div className="relative">
            <button
              onClick={() => toggleDropdown()}
              className="flex items-center space-x-2"
            >
              <img
                src="/api/placeholder/32/32"
                alt="Profile"
                className="w-8 h-8 rounded-full"
              />
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg py-1 border border-gray-200">
                <button
                  onClick={() => {/* Handle profile click */}}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Your Profile
                </button>
                <button
                  onClick={() => {/* Handle settings click */}}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Settings
                </button>
                <button
                  onClick={() => handleLogout()}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  Sign out
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default NavigationBar;