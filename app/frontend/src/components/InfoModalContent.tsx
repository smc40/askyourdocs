// InfoModalContent.tsx
import React from 'react';
import closeIcon from '../img/close.svg';
import logo from '../img/logo.png';

interface InfoModalContentProps {
    onClose: () => void;
}

const InfoModalContent: React.FC<InfoModalContentProps> = ({ onClose }) => {
    return (
        <div className="modal-content">
            <span
                className="close absolute top-2 right-2 text-xl cursor-pointer"
                onClick={onClose}
            >
                <img src={closeIcon} className="w-8" />
            </span>
            <img src={logo} className="h-25" />
            <div className="text-center m-4">
                <p>
                    <strong>Goal:</strong> Locally hosted chatbot answering
                    questions to your documents <br />
                </p>

                <p className="mt-4">
                    <strong>User Story:</strong> As a public relations employee
                    I would like to ask questions to documents, so I can answer
                    to requests faster
                </p>

                <p className="mt-8 text-red-500 text-lg">
                    <strong>Attention / Achtung / Attenzione / Attentie</strong>
                    <br />
                    Use only public data
                </p>
            </div>
        </div>
    );
};

export default InfoModalContent;
