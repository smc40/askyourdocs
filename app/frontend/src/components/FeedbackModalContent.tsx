import React, { useRef } from 'react';
import closeIcon from '../img/close.svg';
import thumsUpIcon from '../img/thumsUpIcon.png';
import thumsDownIcon from '../img/thumsDownIcon.png';

interface InfoModalContentProps {
    onClose: () => void;
    feedbackType: string;
}

const InfoModalContent: React.FC<InfoModalContentProps> = ({
    onClose,
    feedbackType,
}) => {
    const feedbackRef = useRef<HTMLTextAreaElement>(null);

    const saveFeedback = (e: React.FormEvent) => {
        e.preventDefault();
        const feedback = feedbackRef.current;

        if (feedback) {
            console.log('Feedback Type:', feedbackType);
            console.log('Feedback:', feedback.value);
        }
        onClose();
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            saveFeedback(e);
        }
    };

    return (
        <div className="modal-content">
            <span
                className="close absolute top-6 right-6 text-xl cursor-pointer"
                onClick={onClose}
            >
                <img src={closeIcon} className="w-8" />
            </span>
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-3">
                {feedbackType === 'positive' ? (
                    <img src={thumsUpIcon} className="w-6 mr-0" />
                ) : (
                    <img src={thumsDownIcon} className="w-6 mr-0" />
                )}
                Feedback Form
            </h2>

            <form onSubmit={saveFeedback}>
                <div className="mb-4">
                    <label htmlFor="feedback" className="block font-bold mb-2">
                        Feedback:
                    </label>
                    <textarea
                        id="feedback"
                        name="feedback"
                        className="w-full border rounded p-2"
                        onKeyDown={handleKeyDown}
                        ref={feedbackRef}
                    />
                </div>
                <div className="text-right">
                    <button
                        type="submit"
                        className="px-4 py-2 rounded border border-gray-300 hover:bg-gray-300"
                    >
                        Submit Feedback
                    </button>
                </div>
            </form>
        </div>
    );
};

export default InfoModalContent;
