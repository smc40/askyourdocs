// TypingIndicator.tsx
import React from 'react';
import botIcon from '../img/robot.png';
import typingIcon from '../img/dots.gif';

const TypingIndicator: React.FC = () => (
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
);

export default TypingIndicator;
