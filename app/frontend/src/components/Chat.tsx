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
import Authentication from '../auth';

import { Worker } from '@react-pdf-viewer/core';
import '@react-pdf-viewer/core/lib/styles/index.css';
import HighlightKeywords from './PdfTextSearch';

interface Message {
    type: 'user' | 'bot';
    text: string;
    source: string[];
    texts: string[];
    filename: string[];
}

const Main: React.FC = () => {
    const [inputValue, setInputValue] = useState('');
    const [easterEgg, setEasterEgg] = useState(false);
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

    const addMessageToChat = (message: Message) => {
        setChatMessages((prevMessages) => [...prevMessages, message]);
    };

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
                setEasterEgg(true);
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
            homeService
                .getAnswer({ question: inputValue })
                .then((response) => {
                    console.log(response);

                    setIsBotTyping(false);
                    const botMessage: Message = {
                        type: 'bot',
                        text: response.data[0].answer,
                        source: response.data[0].doc_ids,
                        texts: response.data[0].texts,
                        filename: response.data[0].names,
                    };
                    addMessageToChat(botMessage); // Update chatMessages and localStorage
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

    const [fileUrl, setFileUrl] = useState('http://localhost:8000/uploads');
    const [keyword, setKeyword] = useState(['']);

    const getDocumentUrl = (source: string, texts: string[]) => {
        console.log(source);
        console.log(texts);
        setShowFeedback(false);
        setIsOpen(true);

        homeService
            .getDocumentsById(source)
            .then((response) => {
                const filename =
                    'http://localhost:8000/uploads/' + response.data[0].name;
                console.log(filename);
                setFileUrl(filename);
                setKeyword(texts);
            })
            .catch((error) => {
                console.error('Error fetching data:', error);
            });
    };

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
                                    <div className="flex justify-end gap-3 mt-3">
                                        {Array.isArray(message.filename)
                                            ? message.filename
                                                  .map((filename, index) => ({
                                                      filename,
                                                      source: message.source[
                                                          index
                                                      ],
                                                  }))
                                                  .filter(
                                                      (item, index, array) =>
                                                          array.findIndex(
                                                              (otherItem) =>
                                                                  otherItem.source ===
                                                                  item.source
                                                          ) === index
                                                  )
                                                  .map(
                                                      (
                                                          { filename, source },
                                                          index
                                                      ) => {
                                                          // Truncate filename to a max of 20 characters
                                                          const truncatedFilename =
                                                              filename.length >
                                                              20
                                                                  ? filename.slice(
                                                                        0,
                                                                        12
                                                                    ) +
                                                                    '...' +
                                                                    filename.slice(
                                                                        -3
                                                                    )
                                                                  : filename;

                                                          return (
                                                              <a
                                                                  key={index}
                                                                  onClick={() => {
                                                                      getDocumentUrl(
                                                                          source,
                                                                          message.texts
                                                                      );
                                                                  }}
                                                                  style={{
                                                                      backgroundColor:
                                                                          'DodgerBlue',
                                                                      color: 'white',
                                                                      paddingLeft:
                                                                          '12px',
                                                                      paddingRight:
                                                                          '12px',
                                                                      borderRadius:
                                                                          '8px',
                                                                      cursor: 'pointer',
                                                                      display:
                                                                          'block',
                                                                      maxWidth:
                                                                          '320px',
                                                                  }}
                                                              >
                                                                  {
                                                                      truncatedFilename
                                                                  }
                                                              </a>
                                                          );
                                                      }
                                                  )
                                            : null}

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
                                                    setShowFeedback(true);
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
                                                    setShowFeedback(true);
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
