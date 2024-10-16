import React from 'react';
import ContextInput from './ContextInput';

const ProductInformation = ({ contexts, onContextUpdate, onContextDelete }) => {
    // Function to render each context in the list
    const renderContexts = () => {
        if (!contexts || contexts.length === 0) {
            return <p className="text-gray-500">No contexts available</p>; // Informasi jika context tidak tersedia
        }

        return contexts.map((context, index) => (
            <div key={index} className="context-item mb-4 p-4 border rounded-lg bg-gray-50">
                <h4 className="text-lg font-semibold mb-2">Context {index + 1}:</h4>
                <p className="mb-2">{renderContext(context)}</p>
                <button
                    onClick={() => onContextDelete(context.id)}
                    className="py-2 px-4 bg-red-500 text-white rounded-lg hover:bg-red-600 transition"
                >
                    Delete
                </button>
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
            <h2 className="text-xl font-semibold mb-4">Product Information</h2>
            <div className="current-contexts mb-6">
                <h3 className="text-lg font-semibold mb-2">Current Contexts:</h3>
                {renderContexts()}
            </div>
            <ContextInput onContextUpdate={onContextUpdate} />
        </div>
    );
};

export default ProductInformation;
