import React from 'react';
import ContextInput from './ContextInput';

const ProductInformation = ({ contexts, onContextUpdate, onContextDelete }) => {
    // Function to render each context in the list
    const renderContexts = () => {
        if (!contexts || contexts.length === 0) {
            return <p className="text-gray-500">No contexts available</p>; // Informasi jika context tidak tersedia
        }

        return contexts.map((context, index) => (
            <div key={index} className="context-item mb-4 p-4 border rounded-lg bg-gray-50 relative">
                {/* Tombol cross di pojok kanan atas */}
                <button
                    onClick={() => onContextDelete(context.id)}
                    className="absolute top-2 right-2 w-8 h-8 flex items-center justify-center text-red-500 hover:text-red-600 hover:bg-red-50 rounded-full transition-colors duration-200"
                    aria-label="Delete context"
                >
                    <svg 
                        xmlns="http://www.w3.org/2000/svg" 
                        className="h-5 w-5" 
                        viewBox="0 0 20 20" 
                        fill="currentColor"
                    >
                        <path 
                            fillRule="evenodd" 
                            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" 
                            clipRule="evenodd" 
                        />
                    </svg>
                </button>

                <h4 className="text-lg font-semibold mb-2">Context {index + 1}:</h4>
                <p className="mb-2">{renderContext(context)}</p>
            </div>
        ));
    };

    // Function to handle rendering of the context content
    const renderContext = (context) => {
        if (typeof context === 'string') return context;
        if (typeof context === 'object') {
            if (context.message) return context.message;
            if (context.content) return `${context.content} (${context.content_type})`;
            return JSON.stringify(context);
        }
        return 'Invalid context format';
    };

    return (
        <div className="product-information p-4 bg-white shadow-md rounded-lg">
            <h2 className="text-xl font-semibold mb-4">Active Contexts</h2>
            <div className="current-contexts mb-6">
                <h3 className="text-lg font-semibold mb-2">Current Contexts:</h3>
                {renderContexts()}
            </div>
            <ContextInput onContextUpdate={onContextUpdate} />
        </div>
    );
};

export default ProductInformation;
