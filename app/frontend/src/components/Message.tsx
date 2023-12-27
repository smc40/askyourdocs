import React from 'react';
import botIcon from '../img/robot.png';
import userImage from '../img/avatar.png';
import thumsUpIcon from '../img/thumsUpIcon.png';
import thumsDownIcon from '../img/thumsDownIcon.png';

interface MessageProps {
    type: string;
    text: string;
    filename?: string[];
    source?: string[];
    texts?: string[];
    onFeedbackClick?: (feedback: string, index: number) => void;
    feedbackType?: string;
    index: number;
    onDocumentUrl?: (source: string, texts: string[]) => void;
    hideButtons: boolean;
    messageFeedback: { [key: number]: string };
}

const Message: React.FC<MessageProps> = ({
    type,
    text,
    filename,
    source,
    texts,
    onFeedbackClick,
    feedbackType,
    index,
    onDocumentUrl,
    hideButtons,
    messageFeedback,
}) => {
    return (
        <div
            className={`flex ${
                type === 'user' ? 'justify-end' : 'justify-start'
            } items-center mb-2`}
        >
            {type === 'bot' && (
                <img
                    src={botIcon} // Assuming botIcon is available in this component
                    alt="Bot"
                    className="w-8 h-8 rounded-full mr-2 border border-gray-100"
                />
            )}
            <div
                className={`p-2 rounded-tl-lg rounded-tr-lg max-w-lg ${
                    type === 'user'
                        ? 'border border-red-500 rounded-bl-lg self-end ml-11'
                        : 'bg-gray-200 rounded-br-lg text-black mr-11'
                }`}
            >
                {text}
                {type === 'bot' &&
                    !hideButtons &&
                    filename &&
                    Array.isArray(filename) &&
                    filename.length > 0 && (
                        <div className="flex justify-end gap-3 mt-3">
                            {filename
                                .map((filename, index) => ({
                                    filename,
                                    source: source && source[index],
                                }))
                                .filter(
                                    (item, index, array) =>
                                        array.findIndex(
                                            (otherItem) =>
                                                otherItem.source === item.source
                                        ) === index
                                )
                                .map(({ filename, source }, index) => {
                                    const truncatedFilename =
                                        filename.length > 20
                                            ? filename.slice(0, 12) +
                                              '...' +
                                              filename.slice(-3)
                                            : filename;

                                    return (
                                        <a
                                            key={index}
                                            onClick={() => {
                                                onDocumentUrl &&
                                                    source &&
                                                    texts &&
                                                    onDocumentUrl(
                                                        source,
                                                        texts
                                                    );
                                            }}
                                            style={{
                                                backgroundColor: 'DodgerBlue',
                                                color: 'white',
                                                paddingLeft: '12px',
                                                paddingRight: '12px',
                                                borderRadius: '8px',
                                                cursor: 'pointer',
                                                display: 'block',
                                                maxWidth: '320px',
                                            }}
                                        >
                                            {truncatedFilename}
                                        </a>
                                    );
                                })}
                            <div
                                className={`${
                                    messageFeedback[index] === 'positive'
                                        ? 'bg-gray-300'
                                        : ''
                                } mr-0 rounded-md hover:bg-gray-300`}
                            >
                                <img
                                    src={thumsUpIcon}
                                    className="w-5 m-1"
                                    onClick={() => {
                                        onFeedbackClick &&
                                            onFeedbackClick('positive', index);
                                    }}
                                />
                            </div>
                            <div
                                className={`${
                                    messageFeedback[index] === 'negative'
                                        ? 'bg-gray-300'
                                        : ''
                                } mr-0 rounded-md hover:bg-gray-300`}
                            >
                                <img
                                    src={thumsDownIcon}
                                    className="w-5 m-1"
                                    onClick={() => {
                                        onFeedbackClick &&
                                            onFeedbackClick('negative', index);
                                    }}
                                />
                            </div>
                        </div>
                    )}
            </div>

            {type === 'user' && (
                <img
                    src={userImage}
                    alt="User"
                    className="w-8 h-8 rounded-full ml-2 border border-gray-100"
                />
            )}
        </div>
    );
};

export default Message;
