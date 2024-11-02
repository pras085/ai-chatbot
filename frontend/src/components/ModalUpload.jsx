import { faFile, faFileAlt, faFolder, faFolderBlank, faGears } from "@fortawesome/free-solid-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { useState } from "react";

const ModalUpload = ({ isOpen, onClose }) => {
    const [files, setFiles] = useState([]);
  
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
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900 bg-opacity-50">
          <div className="bg-white rounded-lg shadow-lg p-6 w-96">
            <h2 className="text-lg font-semibold text-gray-700 mb-4">Upload Files and Folders</h2>
            {/* List of Files */}
            <div className="mt-6">
              <h3 className="text-gray-600 font-semibold">Uploaded Files</h3>
              <ul className="mt-2 max-h-32 overflow-y-auto border border-gray-200 rounded-lg p-2">
                {files.map((file, index) => (
                  <li key={index} className="text-gray-700 text-sm">
                    {file.name}
                  </li>
                ))}
                {files.length === 0 && <p className="text-gray-500">No files uploaded</p>}
              </ul>
            </div>

            <div className="flex flex-row justify-between gap-4 mt-5">
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                className="hidden"
                id="fileUpload"
              />
              <label
                htmlFor="fileUpload"
                className="bg-blue-500 text-white text-center rounded-md p-2 cursor-pointer hover:bg-blue-600 w-full"
              >
                <FontAwesomeIcon icon={faFileAlt} /> Upload File
              </label>
  
              <input
                type="file"
                webkitdirectory=""
                multiple
                onChange={handleFolderUpload}
                className="hidden"
                id="folderUpload"
              />
              <label
                htmlFor="folderUpload"
                className="bg-blue-500 text-white text-center rounded-md p-2 cursor-pointer hover:bg-blue-600 w-full"
              >
                <FontAwesomeIcon icon={faFolderBlank} /> Upload Folder
              </label>
            </div>
  
            <div className="flex justify-end mt-4">
              <button
                onClick={onClose}
                className="bg-red-500 text-white rounded-lg py-2 px-4 hover:bg-red-600"
              >
                Close
              </button>
              <button
                onClick={onClose}
                className="bg-blue-500 text-white rounded-lg py-2 px-4 hover:bg-blue-600 ml-2"
              >
                <FontAwesomeIcon icon={faGears} /> Process
              </button>
            </div>
          </div>
        </div>
      )
    );
  };

  export default ModalUpload;