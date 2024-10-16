import React, { useState } from 'react';

const ContextInput = ({ onContextUpdate }) => {
    const [text, setText] = useState('');
    const [file, setFile] = useState(null);

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData();
        if (text) formData.append('text', text);
        if (file) formData.append('file', file);

        onContextUpdate(formData);
        setText('');
        setFile(null);
    };

    return (
        <form onSubmit={handleSubmit} className="context-input-form">
            <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Enter additional context..."
                className="context-textarea"
            />
            <input
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
                className="context-file-input"
            />
            <button type="submit" className="context-submit-button">Update Context</button>
        </form>
    );
};

export default ContextInput;