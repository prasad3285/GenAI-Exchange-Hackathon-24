import React, { useState } from 'react';
import axios from 'axios';

const ChatBox = () => {
  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]); // Store the chat history

  const handleSubmit = async (e) => {
    e.preventDefault();

    // Display user's question in the chat history
    setChatHistory((prev) => [...prev, { sender: 'user', text: question }]);
    setQuestion(''); // Clear input after submission

    try {
      // Send the question to the backend
      await axios.post('http://127.0.0.1:5000/ask', { question }, {
        headers: { 'Content-Type': 'application/json' },
      });

      // Listen to the streaming response
      const eventSource = new EventSource('http://127.0.0.1:5000/stream');
      let responseText = '';

      eventSource.onmessage = (event) => {
        responseText += event.data; // Collect the streaming response
        setChatHistory((prev) =>
          prev.map((entry, index) =>
            index === prev.length - 1 ? { ...entry, text: responseText } : entry
          )
        );
      };

      eventSource.onerror = () => {
        eventSource.close();
      };

      // Add an empty response entry to the chat history
      setChatHistory((prev) => [...prev, { sender: 'bot', text: '' }]);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div style={{ width: '50%', margin: '0 auto', padding: '20px', border: '1px solid #ccc' }}>
      <div style={{ height: '300px', overflowY: 'scroll', border: '1px solid #ccc', padding: '10px' }}>
        {chatHistory.map((entry, index) => (
          <div key={index} style={{ marginBottom: '10px', textAlign: entry.sender === 'user' ? 'right' : 'left' }}>
            <strong>{entry.sender === 'user' ? 'You' : 'Bot'}:</strong>
            <p style={{ whiteSpace: 'pre-wrap' }}>{entry.text}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} style={{ marginTop: '10px' }}>
        <textarea
          rows="3"
          style={{ width: '100%', padding: '10px', fontSize: '16px' }}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question here..."
          required
        />
        <button type="submit" style={{ marginTop: '10px', padding: '10px 20px', fontSize: '16px' }}>Send</button>
      </form>
    </div>
  );
};

export default ChatBox;