
import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Message } from './types';
import Header from './components/Header';
import ChatMessage from './components/ChatMessage';
import ChatInput from './components/ChatInput';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'initial-ai-message',
      text: 'Dobrý den! Jsem Váš AI asistent. Zeptejte se mě na cokoli a já se pokusím odpovědět s pomocí dostupných dokumentů.',
      sender: 'ai',
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = useCallback(async (inputText: string) => {
    if (isLoading || !inputText.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      text: inputText,
      sender: 'user',
    };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setIsLoading(true);

    const aiMessagePlaceholder: Message = {
      id: `ai-${Date.now()}`,
      text: '',
      sender: 'ai',
    };
    setMessages((prevMessages) => [...prevMessages, aiMessagePlaceholder]);

    try {
      // Assuming the backend is running on the same host/port,
      // and is serving the `/api/chat` endpoint.
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: inputText }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      const aiResponseText = data.response || 'Omlouvám se, došlo k chybě při zpracování vaší odpovědi.';
      
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === aiMessagePlaceholder.id ? { ...msg, text: aiResponseText } : msg
        )
      );
    } catch (error) {
      console.error('Failed to fetch from backend:', error);
      const errorMessage = error instanceof Error ? error.message : 'Nepodařilo se navázat spojení se serverem. Zkuste to prosím později.';
      setMessages((prevMessages) =>
        prevMessages.map((msg) =>
          msg.id === aiMessagePlaceholder.id
            ? { ...msg, text: `Chyba: ${errorMessage}` }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [isLoading]);

  return (
    <div className="flex flex-col h-screen bg-gray-900 text-gray-100 font-sans">
      <Header />
      <main className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6">
        {messages.map((message) => (
          <ChatMessage
            key={message.id}
            message={message}
            isLoading={isLoading && message.sender === 'ai' && !message.text}
          />
        ))}
        <div ref={messagesEndRef} />
      </main>
      <ChatInput onSendMessage={handleSendMessage} isLoading={isLoading} />
    </div>
  );
};

export default App;
