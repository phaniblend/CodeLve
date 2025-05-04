import React, { useState } from 'react';

const PromptInput = ({ onSendMessage, loading }) => {
  const [message, setMessage] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!message.trim() || loading) return;
    
    onSendMessage(message);
    setMessage('');
  };

  return (
    <form onSubmit={handleSubmit} className="flex space-x-2">
      <div className="flex-1 relative">
        <textarea
          className="input min-h-[2.5rem] resize-none py-2 pr-10"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask about your codebase..."
          rows={1}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          style={{
            height: 'auto',
            minHeight: '2.5rem',
            maxHeight: '10rem',
          }}
        />
      </div>
      <button
        type="submit"
        disabled={loading || !message.trim()}
        className={`btn-primary ${
          loading || !message.trim() ? 'opacity-50 cursor-not-allowed' : ''
        }`}
      >
        {loading ? (
          <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
          </svg>
        )}
      </button>
    </form>
  );
};

export default PromptInput;