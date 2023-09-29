import React from 'react';
interface LoaderProps {
    message?: string;
    type?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = '', type = 'danger' }) => {
    return (
        <div className="inset-0 flex items-center justify-center z-50">
            <div
                className={
                    "py-2 px-4 rounded-lg shadow-lg ${type == 'danger' ? 'bg-red-500' : 'bg-white'}"
                }
            >
                <div
                    className={
                        "flex items-center text-center ${type=='danger'?'text-white':'text-black'}"
                    }
                >
                    <span>{message}</span>
                </div>
            </div>
        </div>
    );
};

export default Loader;
