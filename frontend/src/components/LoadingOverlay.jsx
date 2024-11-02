import React from 'react';

const LoadingOverlay = ({ isLoading }) => {
  if (!isLoading) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 flex flex-col items-center space-y-4">
        {/* Spinning Animation */}
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
        
        {/* Loading Text */}
        <div className="text-gray-700">
          <p className="text-center font-medium">Processing...</p>
          <p className="text-sm text-gray-500">Please wait while we process your request.</p>
        </div>
      </div>
    </div>
  );
};

export default LoadingOverlay;