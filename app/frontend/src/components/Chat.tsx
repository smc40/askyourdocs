import React, { useState, useEffect, useRef, useCallback } from 'react';
import planeIcon from '../img/plane.png';
import TypingIndicator from './TypingIndicator';
import * as homeService from '../services/home';
import config from '../config.js';
import Modal from 'react-modal';
import FeedbackModalContent from './FeedbackModalContent';
import Authentication from '../auth';

import { Worker } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import HighlightKeywords from './PdfTextSearch';

import Message from './Message';

interface Message {
    type: string;
    text: string;
    source: string[];
    texts: string[];
    filename: string[];
}

const Main: React.FC = () => {
    const [inputValue, setInputValue] = useState('');
    const [showEasterEgg, setShowEasterEgg] = useState(false);
    const [isOpen, setIsOpen] = useState(false);
    const [feedback, setFeedback] = useState('');
    const [feedbackOnSentence, setFeedbackOnSentence] = useState('');
    const [showFeedback, setShowFeedback] = useState(false);

    const closeModal = () => {
        setIsOpen(false);
    };

    // Load chat messages from localStorage on component mount
    useEffect(() => {
        const storedMessages = localStorage.getItem('chatMessages');
        if (storedMessages) {
            setChatMessages(JSON.parse(storedMessages));
        }
    }, []);

    const clearChat = () => {
        if (
            window.confirm(
                'Are you sure you want to clear the chat? This action cannot be undone.'
            )
        ) {
            if (socket.current) {
                socket.current.close(); // Close the socket connection
            }

            const defaultInitialMessage = {
                type: 'bot',
                text: 'Welcome back! Start a new conversation or upload documents to get started.',
                source: [],
                texts: [],
                filename: [],
            };

            setChatMessages([defaultInitialMessage]);

            localStorage.setItem(
                'chatMessages',
                JSON.stringify([defaultInitialMessage])
            );

            setTimeout(() => {
                socket.current = new WebSocket(
                    config.backendUrl.replace('http', 'ws') + '/ws/query'
                );
            }, 1000); // Reopen the socket after 1 second
        }
    };

    const [chatMessages, setChatMessages] = useState<Message[]>(() => {
        const storedMessages = localStorage.getItem('chatMessages');
        return storedMessages
            ? JSON.parse(storedMessages)
            : [
                  {
                      type: 'bot',
                      text:
                          'Hi ' +
                          Authentication.getGivenName() +
                          ', start by either uploading some documents on the left or start by typing your first question below...',
                      source: [''],
                      texts: [''],
                      filename: [''],
                  },
              ];
    });

    const addMessageToChat = useCallback((message: Message) => {
        setChatMessages((prevMessages) => [...prevMessages, message]);
    }, []);

    useEffect(() => {
        localStorage.setItem('chatMessages', JSON.stringify(chatMessages));
    }, [chatMessages]);

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

    const socket = useRef<WebSocket | null>(null);

    useEffect(() => {
        socket.current = new WebSocket(
            config.backendUrl.replace('http', 'ws') + '/ws/query'
        );
    }, []);

    useEffect(() => {
        const handleSocketMessage = (event: MessageEvent) => {
            try {
                const response = JSON.parse(event.data);
                const botMessage = {
                    type: 'bot',
                    text: response[0].answer,
                    source: response[0].doc_ids,
                    texts: response[0].texts,
                    filename: response[0].names,
                };
                addMessageToChat(botMessage);
                setIsBotTyping(false);
            } catch (error) {
                console.error('Error parsing message data:', error);
            }
        };

        if (socket.current) {
            socket.current.addEventListener('message', handleSocketMessage);
        }

        return () => {
            if (socket.current) {
                socket.current.removeEventListener(
                    'message',
                    handleSocketMessage
                );
            }
        };
    }, [addMessageToChat]);

    // useEffect(() => {
    //     const handleSocketError = (event) => {
    //         console.error('WebSocket Error:', event);
    //     };

    //     if (socket.current) {
    //         socket.current.addEventListener('error', handleSocketError);
    //     }

    //     return () => {
    //         if (socket.current) {
    //             socket.current.removeEventListener('error', handleSocketError);
    //         }
    //     };
    // }, []);

    const fetchAnswer = async () => {
        try {
            // If WebSocket is not open, re-establish the connection
            if (
                !socket.current ||
                socket.current.readyState !== WebSocket.OPEN
            ) {
                socket.current = new WebSocket(
                    config.backendUrl.replace('http', 'ws') + '/ws/query'
                );
                // Ensure the new connection has time to establish before sending data
                await new Promise((resolve) => {
                    socket.current!.addEventListener('open', resolve, {
                        once: true,
                    });
                });
            }

            socket.current.send(JSON.stringify({ data: inputValue }));
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (inputValue === config.easterEggTrigger) {
            setIsBotTyping(true);
            setInputValue('');
            setChatMessages((prevMessages) => [
                ...prevMessages,
                {
                    type: 'user',
                    text: config.easterEggTriggerMsg,
                    source: [''],
                    texts: [''],
                    filename: [''],
                },
            ]);
            setTimeout(() => {
                setIsBotTyping(false);
                setShowEasterEgg(!showEasterEgg);
                setChatMessages((prevMessages) => [
                    ...prevMessages,
                    {
                        type: 'bot',
                        text: 'a lil fun is always allowed 😉',
                        source: [''],
                        texts: [''],
                        filename: [''],
                    },
                ]);
            }, 3000);
        } else {
            const newMessage: Message = {
                type: 'user',
                text: inputValue,
                source: [''],
                texts: [''],
                filename: [''],
            };
            addMessageToChat(newMessage); // Update chatMessages and localStorage
            setInputValue('');

            setIsBotTyping(true);
            fetchAnswer();
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

    const [fileUrl, setFileUrl] = useState(config.backendUrl + '/uploads');
    const [keyword, setKeyword] = useState(['']);

    const getDocumentUrl = (source: string, texts: string[]) => {
        setShowFeedback(false);
        setIsOpen(true);

        homeService
            .getDocumentsById(source)
            .then((response) => {
                const filename =
                    config.backendUrl + '/uploads/' + response.data[0].name;
                setFileUrl(filename);
                setKeyword(texts);
            })
            .catch((error) => {
                console.error('Error fetching data:', error);
            });
    };

    return (
        <main className="bg-white p-4 w-full">
            <div className="chat-container max-h-[75vh]">
                <div className="overflow-y-auto max-h-[75vh]">
                    {/* Message list */}
                    {chatMessages.map((message, index) => (
                        <Message
                            key={index}
                            type={message.type}
                            text={message.text}
                            filename={message.filename}
                            source={message.source}
                            texts={message.texts}
                            index={index}
                            onFeedbackClick={(feedbackType, index) => {
                                setMessageFeedback((prevFeedback) => ({
                                    ...prevFeedback,
                                    [index]: feedbackType,
                                }));
                                sendFeedback(feedbackType, index);
                                setShowFeedback(true);
                            }}
                            onDocumentUrl={getDocumentUrl}
                            hideButtons={index === 0}
                            messageFeedback={messageFeedback}
                            isEasterEgg={showEasterEgg}
                        />
                    ))}
                    {isBotTyping && <TypingIndicator />}
                    <div ref={chatEndRef} />
                </div>

                {/* Chat input form  */}
                <form
                    onSubmit={handleSubmit}
                    className="chat-controls fixed bottom-10 w-9/12 max-w-3xl flex justify-between items-center"
                >
                    <textarea
                        value={inputValue}
                        onChange={handleChange}
                        onKeyDown={handleKeyDown}
                        placeholder="Type a question for your documents..."
                        className="w-full p-2 border border-gray-300 rounded-lg mr-2 mt-4 focus:ring-red-500 shadow-lg"
                        style={{ resize: 'none', paddingRight: '3rem' }}
                    />
                    <button
                        type="submit"
                        className="absolute right-0 top-1/2 transform -translate-y-1/2 px-4"
                        style={{ right: '130px' }}
                        disabled={inputValue.length <= 3}
                    >
                        <img src={planeIcon} className="h-8" alt="Submit" />
                    </button>
                    <button
                        onClick={clearChat}
                        className="ml-4 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
                    >
                        Clear Chat
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
                        height: 'fit-content',
                        maxHeight: '90vh',
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
                {showFeedback && (
                    <FeedbackModalContent
                        onClose={closeModal}
                        feedbackType={feedback}
                        answerProvided={feedbackOnSentence}
                    />
                )}

                {!showFeedback && (
                    <Worker workerUrl="https://unpkg.com/pdfjs-dist@3.4.120/build/pdf.worker.min.js">
                        <HighlightKeywords
                            fileUrl={fileUrl}
                            keyword={keyword}
                        />
                    </Worker>
                )}
            </Modal>
        </main>
    );
};

export default Main;
