import React from 'react';
interface LoaderProps {
    message?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = '' }) => {
    return (
        <div className="inset-0 flex items-center justify-center z-50">
            <div className="bg-red-500 py-2 px-4 rounded-lg shadow-lg">
                <div className="flex items-center text-white">
                    <span>{message}</span>
                </div>
            </div>
        </div>
    );
};

export default Loader;
