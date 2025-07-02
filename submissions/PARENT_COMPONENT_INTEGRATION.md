# Integration Guide for ChatEdit Component

## Overview

The ChatEdit component has been updated to persist edited messages locally. To integrate this functionality properly, you'll need to make a few changes to the parent component that uses ChatEdit.

## Required Changes

### 1. Pass a unique messageId to ChatEdit

The ChatEdit component now expects a `messageId` prop which is used to store and retrieve edited messages. This should be a unique identifier for each message node.

```jsx
<ChatEdit
  show={showEditDialog}
  initialMessage={selectedMessage.text}
  messageId={selectedMessage.id} // Add this line
  onClose={handleCloseEdit}
  onSave={handleSaveEdit}
/>
```

### 2. Update your onSave handler

The onSave function now receives both the edited message and the messageId. Update your handler to save the message to your application state:

```jsx
const handleSaveEdit = (editedText, messageId) => {
  // Update your messages state/store
  // Example if using React state:
  setMessages((prevMessages) =>
    prevMessages.map((msg) =>
      msg.id === messageId ? { ...msg, text: editedText } : msg
    )
  );

  // Close the dialog
  setShowEditDialog(false);
};
```

### 3. When loading a message for editing

When a user clicks on a node to edit it, make sure you're checking localStorage first:

```jsx
const handleNodeClick = (nodeId) => {
  // Find the message in your state
  const message = messages.find((msg) => msg.id === nodeId);

  if (message) {
    // Try to get edited version from localStorage
    try {
      const editedMessages = JSON.parse(
        localStorage.getItem("editedMessages") || "{}"
      );
      const editedText = editedMessages[nodeId];

      // If we have an edited version, use it instead of the original
      if (editedText) {
        // You might want to update your state here as well
        setSelectedMessage({
          id: nodeId,
          text: editedText,
        });
      } else {
        setSelectedMessage({
          id: nodeId,
          text: message.text,
        });
      }
    } catch (error) {
      console.error("Error reading from localStorage:", error);
      setSelectedMessage({
        id: nodeId,
        text: message.text,
      });
    }

    // Show the edit dialog
    setShowEditDialog(true);
  }
};
```

### 4. When rendering messages

When rendering your message nodes, also check localStorage for edited versions:

```jsx
const getMessageText = (messageId, originalText) => {
  try {
    const editedMessages = JSON.parse(
      localStorage.getItem("editedMessages") || "{}"
    );
    return editedMessages[messageId] || originalText;
  } catch (error) {
    console.error("Error reading from localStorage:", error);
    return originalText;
  }
};

// Then in your render function:
{
  messages.map((msg) => (
    <MessageNode
      key={msg.id}
      id={msg.id}
      text={getMessageText(msg.id, msg.text)}
      onClick={() => handleNodeClick(msg.id)}
    />
  ));
}
```

## Important Notes

1. This implementation uses localStorage for persistence, which has limitations:

   - Data is only stored in the current browser
   - Limited storage space
   - No synchronization across devices

2. For a production app, consider:
   - Saving edits to a database
   - Using a state management solution like Redux
   - Implementing proper error handling and user feedback
