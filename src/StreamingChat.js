import React, { useState } from 'react';
import axios from 'axios';

const StreamingChat = () => {
  const [question, setQuestion] = useState('');
  const [response, setResponse] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setResponse(''); // Clear previous response

    try {
      // Send the question to the backend
      await axios.post('http://127.0.0.1:5000/ask', { question }, {
        headers: { 'Content-Type': 'application/json' },
      });

      // Listen to the streaming response
      const eventSource = new EventSource('http://127.0.0.1:5000/stream');

      eventSource.onmessage = (event) => {
        setResponse((prev) => prev + event.data); // Append each chunk to the response
      };

      eventSource.onerror = () => {
        eventSource.close(); // Close the connection on error
      };
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Type your question"
          required
        />
        <button type="submit">Ask</button>
      </form>
      <div>
        <h3>Response:</h3>
        <pre>{response}</pre>
      </div>
    </div>
  );
};

export default StreamingChat;