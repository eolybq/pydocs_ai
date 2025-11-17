
import React from 'react';
import { Message } from '../types';
import LoadingSpinner from './LoadingSpinner';

interface ChatMessageProps {
  message: Message;
  isLoading: boolean;
}

const UserIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
        <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 1 1 9 0 4.5 4.5 0 0 1-9 0ZM3.751 20.105a8.25 8.25 0 0 1 16.498 0 .75.75 0 0 1-.437.695A18.683 18.683 0 0 1 12 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 0 1-.437-.695Z" clipRule="evenodd" />
    </svg>
);

const AiIcon: React.FC<{ className?: string }> = ({ className }) => (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className={className}>
        <path fillRule="evenodd" d="M8.25 7.5a3.75 3.75 0 1 1 7.5 0 3.75 3.75 0 0 1-7.5 0ZM8.25 4.5a.75.75 0 0 0 0 1.5h7.5a.75.75 0 0 0 0-1.5h-7.5Z" clipRule="evenodd" />
        <path d="M3 13.5a.75.75 0 0 0-1.5 0v2.625a3 3 0 0 0 3 3h15a3 3 0 0 0 3-3V13.5a.75.75 0 0 0-1.5 0v2.625a1.5 1.5 0 0 1-1.5 1.5h-15a1.5 1.5 0 0 1-1.5-1.5V13.5Z" />
    </svg>
);


const ChatMessage: React.FC<ChatMessageProps> = ({ message, isLoading }) => {
  const isUser = message.sender === 'user';

  const messageClasses = `flex items-start gap-3 max-w-xl md:max-w-2xl lg:max-w-3xl ${isUser ? 'ml-auto flex-row-reverse' : 'mr-auto'}`;
  const bubbleClasses = `p-4 rounded-2xl ${isUser ? 'bg-sky-600 rounded-br-none' : 'bg-gray-700 rounded-bl-none'}`;
  
  const icon = isUser ? (
    <UserIcon className="w-8 h-8 p-1.5 bg-gray-600 rounded-full text-sky-300 flex-shrink-0" />
  ) : (
    <AiIcon className="w-8 h-8 p-1.5 bg-gray-600 rounded-full text-emerald-300 flex-shrink-0" />
  );
  
  return (
    <div className={messageClasses}>
      {icon}
      <div className={bubbleClasses}>
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <p className="whitespace-pre-wrap">{message.text}</p>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
