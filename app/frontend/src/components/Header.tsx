// Header.tsx
import React, { useState } from 'react';
import logoIcon from '../img/logo.png';
import infoIcon from '../img/info.png';
import Modal from 'react-modal';
import InfoModalContent from './InfoModalContent';

Modal.setAppElement('#root');

const Header: React.FC = () => {
    const [isOpen, setIsOpen] = useState(false);

    const openModal = () => {
        setIsOpen(true);
    };

    const closeModal = () => {
        setIsOpen(false);
    };

    return (
        <>
            <header className="h-21 border-b p-4 flex items-center justify-between">
                <div className="flex items-center flex-grow">
                    <img src={logoIcon} className="h-20 mx-auto" alt="Logo" />
                </div>
                <img
                    src={infoIcon}
                    className="h-8 w-8"
                    onClick={openModal}
                    alt="Info Icon"
                    style={{ cursor: 'pointer' }}
                />
            </header>
            <Modal
                isOpen={isOpen}
                onRequestClose={closeModal}
                style={{
                    overlay: {
                        backgroundColor: 'rgba(0, 0, 0, 0.5)', // Change overlay color here
                    },
                    content: {
                        width: '50%',
                        height: '50%',
                        maxWidth: '800px',
                        margin: 'auto',
                        border: '1px solid #ccc',
                        background: '#fff',
                        overflow: 'auto',
                        WebkitOverflowScrolling: 'touch',
                        borderRadius: '4px',
                        outline: 'none',
                        padding: '20px',
                    },
                }}
            >
                <InfoModalContent onClose={closeModal} />
            </Modal>
        </>
    );
};

export default Header;
