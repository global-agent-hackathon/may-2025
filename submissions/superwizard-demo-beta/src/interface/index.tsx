import React, { useRef, useEffect, useState, useCallback } from 'react';
import { Box, Flex, VStack, useDisclosure, useToast, AlertDialog, AlertDialogBody, AlertDialogFooter, AlertDialogHeader, AlertDialogContent, AlertDialogOverlay, Button } from '@chakra-ui/react';
import Header from './Header';
import Body from './Body';
import Bottom from './Bottom';
import Sidebar from './Sidebar';
import { useAppState } from '../state/store';

const Interface: React.FC = () => {
  const state = useAppState((state) => ({
    taskHistory: state.currentTask.history,
    taskStatus: state.currentTask.status,
    clearHistory: state.currentTask.actions.clearHistory,
  }));

  // Sidebar management for mobile
  const { isOpen: isSidebarOpen, onOpen: openSidebar, onClose: closeSidebar, onToggle: toggleSidebar } = useDisclosure();

  const [prevTaskStatus, setPrevTaskStatus] = useState(state.taskStatus);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const toast = useToast();
  
  // Alert dialog for clearing chat
  const { isOpen, onOpen, onClose } = useDisclosure();
  const cancelRef = useRef<HTMLButtonElement>(null);

  // Clear chat handler
  const handleClearChat = () => {
    state.clearHistory();
    // Close the sidebar on mobile if it's open
    if (isSidebarOpen) {
      closeSidebar();
    }
    
    toast({
      title: "Chat cleared",
      description: "Started a new conversation",
      status: "success",
      duration: 3000,
      isClosable: true,
      position: "top",
      containerStyle: {
        width: '340px',
        maxWidth: '100%'
      }
    });
  };

  // Auto scroll to bottom when new messages arrive
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [state.taskHistory]);

  // Show toast when task is completed
  useEffect(() => {
    if (prevTaskStatus === 'running' && (state.taskStatus === 'completed' || state.taskStatus === 'success')) {
      toast({
        title: 'Task completed',
        description: 'The AI agent has successfully completed the task',
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: "top",
        containerStyle: {
          width: '340px',
          maxWidth: '100%'
        }
      });
    } else if (prevTaskStatus === 'running' && state.taskStatus === 'error') {
      toast({
        title: 'Task failed',
        description: 'The AI agent encountered an error',
        status: 'error',
        duration: 3000,
        isClosable: true,
        position: "top",
        containerStyle: {
          width: '340px',
          maxWidth: '100%'
        }
      });
    }
    setPrevTaskStatus(state.taskStatus);
  }, [state.taskStatus, prevTaskStatus, toast]);

  // Handle key commands
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    // Send message on Enter without shift
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const submitButton = document.querySelector('[aria-label="Send message"]') as HTMLButtonElement;
      if (submitButton && !submitButton.disabled) {
        submitButton.click();
      }
    }
  }, []);

  return (
    <Flex h="100vh" w="100%" overflow="hidden" maxWidth="100vw">
      {/* Desktop Sidebar */}
      <Box 
        position="relative" 
        w={{ base: "0", md: "280px" }} 
        flexShrink={0}
        display={{ base: "none", md: "block" }}
        borderRight="1px solid"
        borderColor="gray.200"
      >
        <Sidebar 
          onNewChat={handleClearChat} 
          isOpen={true} 
        />
      </Box>

      {/* Mobile Sidebar (Overlay) */}
      <Box 
        position="fixed"
        top={0}
        left={0}
        w="280px"
        h="100vh"
        display={{ base: "block", md: "none" }}
        zIndex={30}
        transform={isSidebarOpen ? "translateX(0)" : "translateX(-100%)"}
        transition="transform 0.3s ease-in-out"
      >
        <Sidebar 
          onNewChat={handleClearChat} 
          isOpen={isSidebarOpen} 
          onClose={closeSidebar} 
        />
      </Box>
      
      {/* Click-away overlay for mobile sidebar */}
      {isSidebarOpen && (
        <Box 
          position="fixed" 
          top={0} 
          left={0} 
          right={0} 
          bottom={0} 
          bg="blackAlpha.600" 
          zIndex={20} 
          display={{ base: 'block', md: 'none' }}
          onClick={closeSidebar}
        />
      )}
      
      {/* Main Content */}
      <Box flex="1" minW={0}>
        <VStack 
          h="100vh" 
          spacing={0} 
          align="stretch"
        >
          <Header onClearChat={handleClearChat} onToggleSidebar={toggleSidebar} isSidebarOpen={isSidebarOpen} />
          <Body chatContainerRef={chatContainerRef} />
          <Bottom handleKeyDown={handleKeyDown} />
        </VStack>
      </Box>
    </Flex>
  );
};

export default Interface; 