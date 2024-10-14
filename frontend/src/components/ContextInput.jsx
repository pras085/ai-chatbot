import React, { useState } from 'react';
// import { uploadContext } from '../services/api';

const ContextUpload = ({ onContextUpdate }) => {
    const [text, setText] = useState('');
    const [file, setFile] = useState(null);
    const [isUploading, setIsUploading] = useState(false);

    const handleTextChange = (e) => {
        setText(e.target.value);
    };

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setIsUploading(true);

        try {
            const formData = new FormData();
            if (text) formData.append('text', text);
            if (file) formData.append('file', file);

            // const result = await uploadContext(formData);
            // onContextUpdate(result);
            setText('');
            setFile(null);
        } catch (error) {
            console.error('Error uploading context:', error);
            alert('Failed to upload context. Please try again.');
        } finally {
            setIsUploading(false);
        }
    };

    return (
        <div className="context-upload">
            <h3>Add Context (Optional)</h3>
            <form onSubmit={handleSubmit}>
                <textarea
                    value={text}
                    onChange={handleTextChange}
                    placeholder="Enter additional context here..."
                />
                <input type="file" onChange={handleFileChange} />
                <button type="submit" disabled={isUploading}>
                    {isUploading ? 'Uploading...' : 'Upload Context'}
                </button>
            </form>
        </div>
    );
};

export default ContextUpload;