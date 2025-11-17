
import React from 'react';

const Header: React.FC = () => {
  return (
    <header className="bg-gray-800/50 backdrop-blur-sm border-b border-gray-700 p-4 shadow-lg sticky top-0 z-10">
      <h1 className="text-xl md:text-2xl font-bold text-center text-transparent bg-clip-text bg-gradient-to-r from-sky-400 to-emerald-400">
        RAG Chat AI
      </h1>
      <p className="text-center text-xs text-gray-400 mt-1">Chat s AI obohacenou o znalostní bázi</p>
    </header>
  );
};

export default Header;
