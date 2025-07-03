import React, { RefObject } from 'react';
import { Box, useColorModeValue } from '@chakra-ui/react';
import TaskHistory from './Chat/TaskHistory';

interface BodyProps {
  chatContainerRef: RefObject<HTMLDivElement>;
}

const Body: React.FC<BodyProps> = ({ chatContainerRef }) => {
  const bgColor = useColorModeValue("#ffffff", "gray.900");
  
  return (
    <Box 
      position="relative"
      flex="1" 
      overflowY="auto" 
      overflowX="hidden"
      ref={chatContainerRef}
      p={0}
      bg={bgColor}
      height="calc(100vh - 60px)"
      width="100%"
      css={{
        '&::-webkit-scrollbar': {
          width: '6px',
        },
        '&::-webkit-scrollbar-track': {
          width: '6px',
          background: 'transparent',
        },
        '&::-webkit-scrollbar-thumb': {
          background: '#888',
          borderRadius: '24px',
        },
        '&::before': {
          content: '""',
          position: 'fixed',
          top: '48px', // Header height
          left: 0,
          right: 0,
          height: '18px',
          background: 'linear-gradient(var(--chakra-colors-chakra-body-bg) 5%, transparent)',
          pointerEvents: 'none',
          zIndex: 10,
        }
      }}
    >
      <Box maxW="800px" mx="auto" mt={4} pb="100px" width="100%">
        <TaskHistory />
      </Box>
    </Box>
  );
};

export default Body; 