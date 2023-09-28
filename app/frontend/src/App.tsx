// App.tsx
import React from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Chat from './components/Chat';

const App: React.FC = () => {
    const handleFileUpload = (file: File) => {
        console.log('File uploaded:', file.name);
    };

    return (
        <div className="mx-auto w-80vw max-w-6xl  shadow-lg">
            <div className="flex flex-col h-screen">
                <Header />
                <div className="flex flex-grow">
                    <Sidebar onFileUpload={handleFileUpload} />
                    <Chat />
                </div>

                <div className="absolute bottom-0 left-0 p-2 text-sm text-gray-600 text-center w-full">
                    Copyright by Interagency Task Force, 2023
                </div>
            </div>
        </div>
    );
};

export default App;
