import React, { useState, useEffect, useRef } from 'react';
import './ChatEdit.css';

// Configure backend URL - adjust as needed
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:5000';

const ChatEdit = ({ show, initialMessage, messageId, onClose, onSave }) => {
  const [editedMessage, setEditedMessage] = useState('');
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const currentMessageIdRef = useRef(null);
  
  // Store edited messages in localStorage to persist them
  const saveToLocalStorage = (id, message) => {
    try {
      const editedMessages = JSON.parse(localStorage.getItem('editedMessages') || '{}');
      editedMessages[id] = message;
      localStorage.setItem('editedMessages', JSON.stringify(editedMessages));
      console.log(`Saved edited message for ID ${id} to localStorage`);
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };
  
  // Retrieve edited message from localStorage if available
  const getFromLocalStorage = (id) => {
    try {
      const editedMessages = JSON.parse(localStorage.getItem('editedMessages') || '{}');
      return editedMessages[id];
    } catch (error) {
      console.error('Error reading from localStorage:', error);
      return null;
    }
  };

  useEffect(() => {
    if (show) {
      // When opening the edit dialog, check if we have a stored edited version
      const storedMessage = messageId ? getFromLocalStorage(messageId) : null;
      
      // Use the stored message if available, otherwise use initialMessage
      setEditedMessage(storedMessage || initialMessage);
      setNewMessage('');
      setError(null);
      currentMessageIdRef.current = messageId;
    }
  }, [show, initialMessage, messageId]);

  if (!show) {
    return null;
  }

  const handleSave = () => {
    // Save to localStorage to persist the edit
    if (messageId) {
      saveToLocalStorage(messageId, editedMessage);
    }
    
    // Pass the edited message back to parent component
    onSave(editedMessage, messageId);
  };

  const handleSendNewMessage = async () => {
    if (!newMessage.trim()) {
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      console.log(`Sending request to ${BACKEND_URL}/api/edit-message`);
      console.log('Request payload:', {
        original_message: editedMessage,
        edit_request: newMessage
      });

      const response = await fetch(`${BACKEND_URL}/api/edit-message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({
          original_message: editedMessage,
          edit_request: newMessage
        }),
      });

      console.log('Response status:', response.status);
      
      // For network errors that don't trigger catch
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('Error response:', errorData);
        throw new Error(errorData.error || `Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      
      if (data.success && data.edited_message) {
        setEditedMessage(data.edited_message);
        
        // Also save the AI-edited message to localStorage immediately
        if (messageId) {
          saveToLocalStorage(messageId, data.edited_message);
        }
        
        setNewMessage('');
      } else {
        throw new Error(data.error || 'No edited message returned');
      }
    } catch (err) {
      console.error('Error editing message:', err);
      
      // Special handling for network errors
      if (err.message === 'Failed to fetch') {
        setError('Could not connect to the server. Please check if the backend is running.');
      } else {
        setError(err.message || 'Failed to edit message');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="edit-dialog-overlay" onClick={onClose}>
      <div className="edit-dialog-content" onClick={e => e.stopPropagation()}>
        <h3>Edit Message</h3>
        <textarea
          className="edit-message-textarea"
          value={editedMessage}
          onChange={(e) => setEditedMessage(e.target.value)}
          rows={6}
          autoFocus
        />
        <div className="new-message-container">
          <textarea
            className="new-message-textarea"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            rows={3}
            placeholder="What would you like to edit?"
            disabled={isLoading}
          />
        </div>
        {error && <div className="edit-error-message">{error}</div>}
        <div className="edit-dialog-actions">
          <button 
            className="edit-dialog-cancel" 
            onClick={onClose}
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            className="new-message-send-button"
            onClick={handleSendNewMessage}
            disabled={isLoading || !newMessage.trim()}
          >
            {isLoading ? 'Processing...' : 'Send'}
          </button>
          <button 
            className="edit-dialog-save" 
            onClick={handleSave}
            disabled={isLoading}
          >
            Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatEdit; 