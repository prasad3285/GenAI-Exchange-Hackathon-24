import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

// Message Component
const Message = ({ sender, text }) => {
  return (
    <div className={`message ${sender === "user" ? "user" : "ai"}`}>
      <div className="message-bubble">
        <strong>{sender === "user" ? "You" : "AI"}:</strong> {text}
      </div>
    </div>
  );
};

// Main Chatbot Component
const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [chatHistories, setChatHistories] = useState([]);

  // Handle sending user input to the server
  const handleSend = async (e) => {
    e.preventDefault(); // Prevent form submission

    if (inputValue.trim() === '') return;

    // Append the user's message to the chat
    const newMessages = [...messages, { sender: 'user', text: inputValue }];
    setMessages(newMessages);
    const userMessage = inputValue; // Capture the user's message
    setInputValue(''); // Clear the input field

    try {
      // Send user input to the Flask server using axios
      await axios.post('http://127.0.0.1:5000/send_message', { message: userMessage });

      // Start listening to the server's streaming response
      listenToFlaskServer(userMessage);
    } catch (error) {
      console.error('Error sending message to the Flask server:', error);
    }
  };

  // Function to listen to the Flask server using EventSource
  const listenToFlaskServer = (userInput) => {
    const eventSource = new EventSource(`http://127.0.0.1:5000/stream?message=${encodeURIComponent(userInput)}`);
    let responseText = '';

    eventSource.onmessage = (event) => {
      // Append each streamed chunk to responseText
      responseText += event.data;

      // Update the AI message in the chat area with the streamed response
      setMessages((prevMessages) => {
        // Check if there's already an AI response in progress; if so, update it
        const updatedMessages = [...prevMessages];
        const lastMessageIndex = updatedMessages.length - 1;

        if (updatedMessages[lastMessageIndex] && updatedMessages[lastMessageIndex].sender === 'ai') {
          updatedMessages[lastMessageIndex].text = responseText;
        } else {
          // Otherwise, add a new AI message entry
          updatedMessages.push({ sender: 'ai', text: responseText });
        }

        return updatedMessages;
      });
    };

    // Handle any errors
    eventSource.onerror = (error) => {
      console.error('Error with EventSource:', error);
      eventSource.close();
    };
  };

  const handleReset = () => {
    setChatHistories([...chatHistories, messages]);
    setMessages([]);
    setInputValue('');
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleHistoryClick = (history) => {
    setMessages(history);
  };


  // Handles Premade Button Click
  const handlePremadeClick = (question) => {
    setMessages([...messages, { sender: "user", text: question }]);

    // Simulate AI Response
    setTimeout(() => {
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "ai", text: "AI response to: " + question }
      ]);
    }, 1000);
  };

  return (
    <div className="chatbot-wrapper">
      {/* Sidebar for Chat History */}
      <div className="sidebar">
        <h3>Chat History</h3>
        <ul>
          {chatHistories.map((chat, index) => (
            <li key={index} onClick={() => handleHistoryClick(index)}>
              {chat.title}
            </li>
          ))}
        </ul>
      </div>

      {/* Chat Interface */}
      <div className="chatbot-container">
        <div className="chat-area">
          {messages.length === 0 ? (
            <div className="button-grid">
              {buttonOptions.map((text, index) => (
                <button
                  key={index}
                  className={`grid-button button-${index + 1}`}
                  onClick={() => handlePremadeClick(text)}
                >
                  {text}
                </button>
              ))}
            </div>
          ) : (
            messages.map((message, index) => (
              <Message key={index} sender={message.sender} text={message.text} />
            ))
          )}
        </div>

        {/* Input Box with Send and Reset Buttons */}
        <div className="input-box">
          <input
            type="text"
            placeholder="Ask me anything...."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyUp={(e) => e.key === "Enter" && handleSend()}
          />
          <button onClick={handleSend}>Send</button>
          <button onClick={handleReset} className="reset-btn">Reset Chat</button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;