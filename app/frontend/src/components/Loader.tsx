import React from 'react';
interface LoaderProps {
    message?: string;
}

const Loader: React.FC<LoaderProps> = ({ message = '' }) => {
    return (
        <div className="inset-0 flex items-center justify-center z-50">
            <div className="bg-white border py-2 px-4 rounded-lg shadow-lg">
                <div className="flex items-center">
                    <svg
                        className="animate-spin h-5 w-5 mr-3 text-blue-600"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                    >
                        <circle
                            className="opacity-25"
                            cx="12"
                            cy="12"
                            r="10"
                            stroke="currentColor"
                            strokeWidth="4"
                        ></circle>
                        <path
                            className="opacity-75"
                            fill="currentColor"
                            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A8.004 8.004 0 014.51 14H0v4h6v-6H6.242z"
                        ></path>
                    </svg>
                    <span>{message}</span>
                </div>
            </div>
        </div>
    );
};

export default Loader;
