import React from 'react';
import { 
  Box, 
  Heading, 
  Flex, 
  Button, 
  IconButton, 
  Tooltip,
  Image,
  Icon,
  Badge,
  Text,
  HStack
} from '@chakra-ui/react';
import { CloseIcon, WarningIcon } from '@chakra-ui/icons';
import { useAppState } from '../state/store';

interface HeaderProps {
  onClearChat: () => void;
  onToggleSidebar?: () => void;
  isSidebarOpen?: boolean;
}

// Custom MenuIcon component that looks like two horizontal lines
const MenuIcon = (props: any) => (
  <Icon viewBox="0 0 24 24" {...props}>
    <path
      fill="#1d7ba7"
      d="M4 6.5h16a1.5 1.5 0 0 1 0 3H4a1.5 1.5 0 0 1 0-3zm0 8h12a1.5 1.5 0 0 1 0 3H4a1.5 1.5 0 0 1 0-3z"
    />
  </Icon>
);

// Custom NewChatIcon component
const NewChatIcon = (props: any) => (
  <Icon viewBox="0 0 18.75 18.75" {...props}>
    <defs>
      <clipPath id="a">
        <path d="M0 0h18.504v17.762H0Zm0 0"/>
      </clipPath>
    </defs>
    <g clipPath="url(#a)">
      <path fill="#b1b1b1" d="M9.418.004C4.441.004.391 4.054.391 9.03a9.03 9.03 0 0 0 1.699 5.274L.55 15.707c-.413.379-.55.965-.347 1.488.203.528.7.867 1.262.867h7.953c4.977 0 9.027-4.05 9.027-9.03 0-4.977-4.05-9.028-9.027-9.028Zm0 16.5H1.984l1.688-1.54a.776.776 0 0 0 .066-1.077A7.479 7.479 0 0 1 1.945 9.03c0-4.117 3.352-7.469 7.473-7.469s7.473 3.352 7.473 7.47c0 4.12-3.352 7.472-7.473 7.472Zm0 0"/>
    </g>
    <path fill="#b1b1b1" d="M12.336 8.254h-2.14V6.117a.78.78 0 0 0-.778-.781.78.78 0 0 0-.777.781v2.137H6.5a.78.78 0 0 0 0 1.559h2.14v2.136c0 .43.348.781.778.781a.78.78 0 0 0 .777-.78V9.812h2.14a.78.78 0 0 0 0-1.56Zm0 0"/>
  </Icon>
);

const Header: React.FC<HeaderProps> = ({ onClearChat, onToggleSidebar, isSidebarOpen }): JSX.Element => {
  const taskStatus = useAppState((state) => state.currentTask.status);
  const taskHistory = useAppState((state) => state.currentTask.history);
  const consecutiveFailures = useAppState((state) => state.currentTask.consecutiveFailures);
  const lastActionResult = useAppState((state) => state.currentTask.lastActionResult);
  
  const isTaskRunning = taskStatus === 'running';
  const hasHistory = taskHistory.length > 0;
  const hasFailures = consecutiveFailures > 0;

  return (
    <Box 
      w="full" 
      py={0}
      px={2}
      borderBottom="none" 
      borderColor="#ececec"
      bg="white"
      height="48px"
      position="sticky"
      top={0}
      zIndex={20}
      overflow="visible"
    >
      {/* Darkening overlay */}
      {isSidebarOpen && (
        <Box 
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg="blackAlpha.600"
          zIndex={20}
          display={{ base: 'block', md: 'none' }}
        />
      )}
      <Flex alignItems="center" height="100%" position="relative" zIndex={21}>
        {/* Mobile sidebar toggle */}
        <IconButton
          display={{ base: 'flex', md: 'none' }}
          aria-label="Toggle Sidebar"
          icon={<MenuIcon boxSize="23px" />}
          variant="ghost"
          size="sm"
          mr={2}
          onClick={onToggleSidebar}
          _hover={{}}
        />
        
        {/* Failure status indicator */}
        {hasFailures && (
          <Tooltip 
            label={`${consecutiveFailures} consecutive action failure${consecutiveFailures > 1 ? 's' : ''}. ${
              lastActionResult?.error ? `Last error: ${lastActionResult.error.substring(0, 100)}${lastActionResult.error.length > 100 ? '...' : ''}` : ''
            }`}
            placement="bottom" 
            hasArrow 
            maxW="300px"
            pointerEvents="none"
            gutter={8}
            offset={[0, 4]}
            openDelay={300}
          >
            <HStack spacing={1} mr={2}>
              <WarningIcon color="orange.500" boxSize="16px" />
              <Badge colorScheme="orange" variant="solid" fontSize="xs">
                {consecutiveFailures}/3
              </Badge>
            </HStack>
          </Tooltip>
        )}
        
        {/* Spacer */}
        <Box flex={1} />

        {/* Logo in center */}
        <Image
          src={require('../assets/img/Superwizard.svg')}
          alt="Superwizard"
          height="26.4px"
          position="absolute"
          left="50%"
          transform="translateX(-50%)"
        />

        {/* New Chat button */}
        <Tooltip 
          label={hasHistory ? "New Chat" : "No conversation history"} 
          placement="bottom" 
          hasArrow 
          pointerEvents="none"
          gutter={8}
          offset={[0, 4]}
          openDelay={300}
        >
          <IconButton
            aria-label="New Chat"
            icon={<NewChatIcon boxSize="23px" />}
            variant="ghost"
            size="sm"
            ml={2}
            onClick={onClearChat}
            isDisabled={isTaskRunning || !hasHistory}
            opacity={hasHistory ? 1 : 0.5}
            _hover={{}}
          />
        </Tooltip>
      </Flex>
    </Box>
  );
};

export default Header; 