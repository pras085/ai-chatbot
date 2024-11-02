import React from 'react';
import { X } from 'lucide-react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileArrowUp, faFolderPlus, faGears } from '@fortawesome/free-solid-svg-icons';

const ModalUpload = ({ isOpen, onClose, files, setFiles, process }) => {
  const handleFileUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);
    setFiles((prevFiles) => [...prevFiles, ...uploadedFiles]);
  };

  const handleFolderUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);
    setFiles((prevFiles) => [...prevFiles, ...uploadedFiles]);
  };
    
  return (
    isOpen && (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg w-full max-w-md p-6 relative animate-fade-in">
          {/* Close button */}
          <button 
            onClick={onClose}
            className="absolute top-4 right-4 text-gray-500 hover:text-red-700 hover:bg-red-200 transition-colors rounded-full"
            aria-label="Close modal"
          >
            <X size={20} />
          </button>

          {/* Modal header */}
          <h2 className="text-xl font-semibold text-gray-900 mb-6">
            Upload Files and Folders
          </h2>

          {/* Upload content */}
          <div className="space-y-4">
            <div className="border border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50">
              {files.map((file, index) => (
                <li key={index} className="text-gray-700 text-sm">
                  {file.name}
                </li>
              ))}
              {files.length === 0 && <p className="text-gray-500 mb-2">No files uploaded</p>}
            </div>

            {/* Buttons container */}
            <div className="flex gap-3">
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="hidden"
                id="fileUpload"
              />
              <button className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors" onClick={() => document.getElementById('fileUpload').click()}>
                <FontAwesomeIcon icon={faFileArrowUp} /> Upload Files
              </button>

              <input
                type="file"
                webkitdirectory=""
                multiple
                onChange={handleFolderUpload}
                className="hidden"
                id="folderUpload"
              />
              <button className="flex-1 bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 transition-colors" onClick={() => document.getElementById('folderUpload').click()}>
              <FontAwesomeIcon icon={faFolderPlus} /> Upload Folder
              </button>
            </div>

            {/* Action buttons */}
            <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-gray-200">
              <button className="px-4 py-2 rounded-md bg-blue-500 text-white hover:bg-blue-600 transition-colors" onClick={process}>
                <FontAwesomeIcon icon={faGears} /> Process
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  );
};

export default ModalUpload;