import React from 'react';
import { Text } from '@chakra-ui/react';

// Simple text component for the send button
export const SendButton: React.FC = () => {
  return (
    <Text
      fontWeight="medium"
      fontSize="lg"
      color="gray.600"
    >
      Send
    </Text>
  );
}; 