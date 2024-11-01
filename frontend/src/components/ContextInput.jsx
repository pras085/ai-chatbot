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
                className="w-full h-20 px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-400 focus:border-transparent focus:outline-none resize-none bg-white text-slate-700 placeholder-slate-400 transition-all duration-200"
            />
            <div className="flex items-center mt-4">
                <label className="relative cursor-pointer">
                    <input
                    type="file"
                    onChange={(e) => setFile(e.target.files[0])}
                    className="hidden"  // Sembunyikan input asli
                    />
                    <div className="flex items-center gap-2 px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors duration-200">
                    <svg 
                        className="w-5 h-5" 
                        fill="none" 
                        stroke="currentColor" 
                        viewBox="0 0 24 24"
                    >
                        <path 
                        strokeLinecap="round" 
                        strokeLinejoin="round" 
                        strokeWidth={2} 
                        d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" 
                        />
                    </svg>
                    <span>Choose File</span>
                    </div>
                </label>
                {/* Opsional: Menampilkan nama file yang dipilih */}
                <span className="ml-3 text-sm text-slate-600">
                    {file ? file.name : 'No file chosen'}
                </span>
            </div>
            <div className="flex justify-end">
                <button 
                    type="submit" 
                    className="mt-4 px-4 py-2 bg-green-700 text-white font-medium rounded hover:bg-green-900 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-400"
                >
                    + Context
                </button>
            </div>
        </form>
    );
};

export default ContextInput;