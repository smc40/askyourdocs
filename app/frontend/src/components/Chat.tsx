import React, { useState, useEffect, useRef } from 'react';
import botIcon from '../img/robot.png';
import userImage from '../img/avatar.png';
import planeIcon from '../img/plane.png';
import typingIcon from '../img/dots.gif';
import * as homeService from '../services/home';
import config from '../config.js';
import easterEggIcon from '../img/easterEgg.gif';
import thumsUpIcon from '../img/thumsUpIcon.png';
import thumsDownIcon from '../img/thumsDownIcon.png';
import Modal from 'react-modal';
import FeedbackModalContent from './FeedbackModalContent';

interface Message {
    type: 'user' | 'bot';
    text: string;
}

const Main: React.FC = () => {
    const [inputValue, setInputValue] = useState('');
    const [easterEgg, setEasterEgg] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [feedback, setFeedback] = useState('');
    const [feedbackOnSentence, setFeedbackOnSentence] = useState('');

    const closeModal = () => {
        setIsOpen(false);
    };

    const [chatMessages, setChatMessages] = useState<Message[]>([
        {
            type: 'bot',
            text: 'Hi, start by either uploading some documents on the left or start by typing your first question below...',
        },
    ]);
    const [isBotTyping, setIsBotTyping] = useState(false);

    const sendFeedback = (feedback: string, index: number) => {
        setFeedback(feedback);
        setIsOpen(true);
        setFeedbackOnSentence(
            'QUESTION: ' +
                chatMessages[index - 1].text +
                '\nANSWER:' +
                chatMessages[index].text
        );
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setInputValue(e.target.value);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputValue === config.easterEggTrigger) {
            setIsBotTyping(true);
            setInputValue('');
            setChatMessages((prevMessages) => [
                ...prevMessages,
                { type: 'user', text: config.easterEggTriggerMsg },
            ]);
            setTimeout(() => {
                setIsBotTyping(false);
                setEasterEgg(true);
                setChatMessages((prevMessages) => [
                    ...prevMessages,
                    { type: 'bot', text: 'a lil fun is always allowed 😉' },
                ]);
            }, 3000);
        } else {
            const newMessage: Message = { type: 'user', text: inputValue };
            setChatMessages([...chatMessages, newMessage]);
            setInputValue('');

            setIsBotTyping(true);
            homeService
                .getAnswer({ question: inputValue })
                .then((response) => {
                    setIsBotTyping(false);
                    setChatMessages((prevMessages) => [
                        ...prevMessages,
                        { type: 'bot', text: response.data },
                    ]);
                })
                .catch((error) => console.error('Error fetching data:', error));
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (inputValue.length >= 3) {
                handleSubmit(e);
            }
        }
    };

    const chatEndRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [chatMessages]);

    const [messageFeedback, setMessageFeedback] = useState<{
        [key: number]: string;
    }>({});

    return (
        <main className="bg-white p-4 w-full">
            <div className="chat over max-h-[75vh]">
                <div className="overflow-y-auto max-h-[75vh]">
                    {chatMessages.map((message, index) => (
                        <div
                            key={index}
                            className={`flex ${
                                message.type === 'user'
                                    ? 'justify-end'
                                    : 'justify-start'
                            } items-center mb-2`}
                        >
                            {message.type === 'bot' && (
                                <img
                                    src={easterEgg ? easterEggIcon : botIcon}
                                    alt="Bot"
                                    className="w-8 h-8 rounded-full mr-2 border border-gray-100"
                                />
                            )}
                            <div
                                className={`p-2 rounded-tl-lg rounded-tr-lg max-w-lg ${
                                    message.type === 'user'
                                        ? 'border border-red-500 rounded-bl-lg self-end ml-11'
                                        : 'bg-gray-200 rounded-br-lg text-black mr-11'
                                }`}
                            >
                                {message.text}

                                {message.type === 'bot' && index !== 0 && (
                                    <div className="flex justify-end gap-3">
                                        <div
                                            className={`${
                                                messageFeedback[index] ===
                                                'positive'
                                                    ? 'bg-gray-300'
                                                    : ''
                                            } mr-0 rounded-md hover:bg-gray-300`}
                                        >
                                            <img
                                                src={thumsUpIcon}
                                                className="w-5 m-1"
                                                onClick={() => {
                                                    setMessageFeedback(
                                                        (prevFeedback) => ({
                                                            ...prevFeedback,
                                                            [index]: 'positive',
                                                        })
                                                    );
                                                    sendFeedback(
                                                        'positive',
                                                        index
                                                    );
                                                }}
                                            />
                                        </div>
                                        <div
                                            className={`${
                                                messageFeedback[index] ===
                                                'negative'
                                                    ? 'bg-gray-300'
                                                    : ''
                                            } mr-0 rounded-md hover:bg-gray-300`}
                                        >
                                            <img
                                                src={thumsDownIcon}
                                                className="w-5 m-1"
                                                onClick={() => {
                                                    setMessageFeedback(
                                                        (prevFeedback) => ({
                                                            ...prevFeedback,
                                                            [index]: 'negative',
                                                        })
                                                    );
                                                    sendFeedback(
                                                        'negative',
                                                        index
                                                    );
                                                }}
                                            />
                                        </div>
                                    </div>
                                )}
                            </div>

                            {message.type === 'user' && (
                                <img
                                    src={userImage}
                                    alt="User"
                                    className="w-8 h-8 rounded-full ml-2 border border-gray-100"
                                />
                            )}
                        </div>
                    ))}
                    {isBotTyping && (
                        <div className="flex items-center justify-start mb-2">
                            <img
                                src={botIcon}
                                alt="Bot"
                                className="w-8 h-8 rounded-full mr-2 border border-gray-100"
                            />
                            <div className="p-2 rounded-lg bg-gray-200 text-black mr-11">
                                <img src={typingIcon} className="w-6" />
                            </div>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                <form
                    onSubmit={handleSubmit}
                    className="fixed bottom-10 w-9/12 max-w-3xl"
                >
                    <textarea
                        value={inputValue}
                        onChange={handleChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Type a question for your documents..."
                        className="w-full p-2 border border-gray-300 rounded-lg mr-2 mt-4 focus:ring-red-500 shadow-lg"
                        style={{ resize: 'none' }}
                    />

                    <button
                        type="submit"
                        className="absolute right-0 px-4"
                        style={{ top: '50%', transform: 'translateY(-50%)' }}
                        disabled={inputValue.length <= 3}
                    >
                        <img src={planeIcon} className="h-8" alt="Submit" />
                    </button>
                </form>
            </div>

            <Modal
                isOpen={isOpen}
                onRequestClose={closeModal}
                style={{
                    overlay: {
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                    },
                    content: {
                        maxWidth: '800px',
                        maxHeight: '280px',
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
                <FeedbackModalContent
                    onClose={closeModal}
                    feedbackType={feedback}
                    answerProvided={feedbackOnSentence}
                />
            </Modal>
        </main>
    );
};

export default Main;
