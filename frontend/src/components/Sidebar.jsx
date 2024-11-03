import React from 'react';
import { 
  Book, 
  Shield, 
  Users, 
  History,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const MenuItem = ({ icon: Icon, label, isCollapsed, isActive, onClick }) => (
  <button
    onClick={onClick}
    className={`
      w-full flex items-center px-3 py-2 my-1 rounded-lg transition-colors duration-200
      ${isActive 
        ? 'bg-blue-100 text-blue-600' 
        : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
      }
    `}
  >
    <Icon size={20} className="flex-shrink-0" />
    {!isCollapsed && (
      <span className="ml-3 font-medium">{label}</span>
    )}
  </button>
);

const Sidebar = () => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const path = window.location.pathname;
  const navigate = useNavigate();

  const handleMenuItemClick = (id) => {
    navigate(`/admin/${id}`);
  };

  const menuItems = [
    {
      id: 'knowledge-base',
      label: 'Knowledge Base',
      icon: Book
    },
    {
      id: 'rules',
      label: 'Rules',
      icon: Shield
    },
    {
      id: 'user-management',
      label: 'User Management',
      icon: Users
    },
    {
      id: 'logs',
      label: 'Logs',
      icon: History
    }
  ];

  return (
    <div 
      className={`
        h-full bg-white border-r border-gray-200 transition-all duration-300
        ${isCollapsed ? 'w-16' : 'w-64'}
      `}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-3 border-b border-gray-200">
        {!isCollapsed && (
          <span className="text-lg font-semibold text-gray-800">
            Admin Panel
          </span>
        )}
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="p-1.5 rounded-lg hover:bg-gray-100 text-gray-600"
        >
          {isCollapsed ? (
            <ChevronRight size={20} />
          ) : (
            <ChevronLeft size={20} />
          )}
        </button>
      </div>

      {/* Menu Items */}
      <div className="p-3">
        {menuItems.map((item) => (
          <MenuItem
            key={item.id}
            icon={item.icon}
            label={item.label}
            isCollapsed={isCollapsed}
            isActive={path.split('/')[2] === item.id}
            onClick={() => handleMenuItemClick(item.id)}
          />
        ))}
      </div>
    </div>
  );
};

export default Sidebar;