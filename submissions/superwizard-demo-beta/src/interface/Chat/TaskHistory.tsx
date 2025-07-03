import {
  VStack,
  Box,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Text,
  Avatar,
  Flex,
  Divider,
  Badge,
  HStack,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress,
  Spinner,
  useColorModeValue,
  Button,
  useDisclosure,
} from '@chakra-ui/react';
import React from 'react';
import { TaskHistoryEntry } from '../../state/currentTask';
import { useAppState } from '../../state/store';
import { PlannerIcon } from '../ui/PlannerIcon';
import { FONT_FAMILY } from '../../styles/fonts';
import { WarningIcon } from '@chakra-ui/icons';

// Enhanced history entry type for UI
interface EnhancedHistoryEntry extends TaskHistoryEntry {
  userInput?: string;
  aiResponse?: string;
  phase: 'user_input' | 'ai_response' | 'error';
  error?: string;
  timestamp: string;
  previousActions?: string[];
  pageContents?: string;
}

type TaskHistoryItemProps = {
  index: number;
  entry: EnhancedHistoryEntry;
};

// Timestamp component with improved styling
const TimeStamp = ({ time }: { time: string }) => (
  <Flex justify="center" my={2}>
    <Badge 
      px={2} 
      py={1} 
      borderRadius="full" 
      colorScheme="gray" 
      fontSize="xs"
    >
      {time}
    </Badge>
  </Flex>
);

// User avatar component
const UserAvatar = () => (
  <Avatar 
    size="sm" 
    name="AH" 
    bg="gray.700"
    color="white"
    fontWeight="bold"
  />
);

// Assistant avatar component
const AssistantAvatar = () => (
  <Avatar 
    size="sm" 
    name="Superwizard" 
    src="/icon-34.png"
    bg="white"
    border="1px solid"
    borderColor="gray.200"
  />
);

interface MessageContainerProps {
  isUser: boolean;
  children: React.ReactNode;
  showSpinner?: boolean;
}

interface MessageContent {
  pageContents?: string;
  [key: string]: any;
}

// Add this new component for collapsible text
const CollapsibleText = ({ text, maxHeight = "300px" }: { text: string, maxHeight?: string }) => {
  const [isExpanded, setIsExpanded] = React.useState(false);
  const textRef = React.useRef<HTMLDivElement>(null);
  const [shouldShowButton, setShouldShowButton] = React.useState(false);
  const [copySuccess, setCopySuccess] = React.useState(false);
  const bgColor = useColorModeValue("gray.50", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");

  React.useEffect(() => {
    if (textRef.current) {
      const element = textRef.current;
      setShouldShowButton(element.scrollHeight > element.clientHeight);
    }
  }, [text]);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess(true);
      // Reset copy success after 2 seconds
      setTimeout(() => setCopySuccess(false), 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <Box>
      <Box
        ref={textRef}
        bg={bgColor}
        p={4}
        borderRadius="md"
        fontSize="sm"
        whiteSpace="pre-wrap"
        wordBreak="break-word"
        fontFamily={FONT_FAMILY.mono}
        border="1px solid"
        borderColor={borderColor}
        maxHeight={isExpanded ? "none" : maxHeight}
        overflow={isExpanded ? "visible" : "hidden"}
        position="relative"
        css={{
          transition: 'max-height 0.3s ease-in-out',
          '&:after': !isExpanded ? {
            content: '""',
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '50px',
            background: 'linear-gradient(transparent, var(--chakra-colors-chakra-body-bg))',
            pointerEvents: 'none'
          } : {}
        }}
      >
        {text}
      </Box>
      <HStack spacing={2} mt={2}>
        {shouldShowButton && (
          <Button
            size="xs"
            variant="ghost"
            onClick={() => setIsExpanded(!isExpanded)}
            flex="1"
            colorScheme="blue"
          >
            {isExpanded ? "Show Less" : "Show More"}
          </Button>
        )}
        <Button
          size="xs"
          variant="ghost"
          onClick={handleCopy}
          colorScheme={copySuccess ? "green" : "gray"}
          minW="80px"
        >
          {copySuccess ? "Copied!" : "Copy"}
        </Button>
      </HStack>
    </Box>
  );
};

// Enhanced message container
const MessageContainer = ({ isUser, children, showSpinner = false }: MessageContainerProps) => {
  const bgColor = useColorModeValue("gray.50", "gray.800");
  const borderColor = useColorModeValue("gray.200", "gray.700");
  
  return (
    <Flex 
      w="full" 
      px={{ base: 2, md: 4 }}
      py={3}
      borderBottom="1px solid"
      borderColor={borderColor}
      overflowX="hidden"
      maxWidth="100%"
      animation="fadeIn 0.3s ease-in-out"
      css={{
        '@keyframes fadeIn': {
          '0%': {
            opacity: 0,
          },
          '100%': {
            opacity: 1,
          }
        }
      }}
    >
      <Box flex="1" overflowX="hidden">
        <VStack spacing={3} align="stretch" width="100%">
          {/* Header with user/AI indicator */}
          <Flex justify="space-between" align="center">
            <HStack>
              <Text fontWeight="bold" fontSize="sm" color={isUser ? "blue.500" : "green.500"}>
                {isUser ? "You" : "Superwizard"}
              </Text>
              {showSpinner && (
                <Spinner size="xs" color="blue.500" />
              )}
            </HStack>
          </Flex>

          {/* Main content */}
          {typeof children === 'string' ? (
            <CollapsibleText text={children} />
          ) : (
            <Box
              bg={bgColor}
              p={4}
              borderRadius="md"
              fontSize="sm"
              whiteSpace="pre-wrap"
              wordBreak="break-word"
              fontFamily={FONT_FAMILY.mono}
              border="1px solid"
              borderColor={borderColor}
            >
              {children}
            </Box>
          )}
        </VStack>
      </Box>
    </Flex>
  );
};

// Session divider with timestamp
const SessionDivider = ({ timestamp }: { timestamp?: string }) => {
  return (
    <Flex align="center" my={4}>
      <Divider flex="1" borderColor="gray.300" />
      {timestamp && (
        <Box px={4}>
          <Badge px={3} py={1} borderRadius="full" bg="gray.100" color="gray.600" fontSize="xs">
            {new Date(timestamp).toLocaleString()}
          </Badge>
        </Box>
      )}
      <Divider flex="1" borderColor="gray.300" />
    </Flex>
  );
};

// Individual task history item component
const TaskHistoryItem = ({ index, entry }: TaskHistoryItemProps) => {
  // Format timestamp for display
  const timestamp = new Date(entry.timestamp).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit'
  });

  // Helper function to extract message content from response
  const extractMessageContent = (response: string): string => {
    try {
      // Try to parse as JSON first
      const parsed = JSON.parse(response);
      
      // Check if it has a message property
      if (parsed.message) {
        return parsed.message;
      }
      
      // If it's an object but no message property, stringify it nicely
      if (typeof parsed === 'object') {
        return JSON.stringify(parsed, null, 2);
      }
      
      // If it's a primitive value, return as string
      return String(parsed);
    } catch (error) {
      // If it's not valid JSON, return the original string
      return response;
    }
  };

  // Handle different types of AI responses
  const renderAIResponse = () => {
    // Default text response
    if (typeof entry.response === 'string') {
      const messageContent = extractMessageContent(entry.response);
      
      return (
        <MessageContainer isUser={false}>
          <VStack spacing={3} align="stretch">
            {/* Context prompt section */}
            <Box>
              <Text fontWeight="medium" mb={2}>Context Prompt:</Text>
              <CollapsibleText text={entry.prompt} maxHeight="150px" />
            </Box>

            {/* Response section */}
            <Box>
              <Text fontWeight="medium" mb={2}>Response:</Text>
              <CollapsibleText text={messageContent} />
            </Box>

            {/* Tool calls and actions */}
            {entry.action && (
              <Box>
                <Text fontWeight="medium" mb={2}>Actions Taken:</Text>
                {'parsedAction' in entry.action && (
                  <Box 
                    p={3} 
                    bg={useColorModeValue("gray.50", "gray.700")} 
                    borderRadius="md"
                    fontSize="sm"
                    border="1px solid"
                    borderColor={useColorModeValue("gray.200", "gray.600")}
                  >
                    <Text fontWeight="medium">Tool: {entry.action.parsedAction.name}</Text>
                    <Text mt={1}>Arguments:</Text>
                    <Box 
                      as="pre" 
                      p={2} 
                      mt={1}
                      bg={useColorModeValue("white", "gray.800")}
                      borderRadius="sm"
                      fontSize="xs"
                      border="1px solid"
                      borderColor={useColorModeValue("gray.200", "gray.600")}
                      whiteSpace="pre-wrap"
                      wordBreak="break-word"
                      overflowWrap="break-word"
                    >
                      {(() => {
                        // Special handling for "respond" tool to extract message content
                        if (entry.action.parsedAction.name === 'respond' && 
                            entry.action.parsedAction.args && 
                            typeof entry.action.parsedAction.args === 'object' &&
                            'message' in entry.action.parsedAction.args) {
                          return entry.action.parsedAction.args.message;
                        }
                        // For other tools, show the JSON structure
                        return JSON.stringify(entry.action.parsedAction.args, null, 2);
                      })()}
                    </Box>
                  </Box>
                )}
                
                {'error' in entry.action && (
                  <Alert status="error" borderRadius="md">
                    <AlertIcon />
                    {entry.action.error}
                  </Alert>
                )}
              </Box>
            )}
          </VStack>
        </MessageContainer>
      );
    }

    // Fallback for empty response
    return (
      <MessageContainer isUser={false}>
        <Text fontStyle="italic" color="gray.500">No response</Text>
      </MessageContainer>
    );
  };

  // Rendering based on task phase
  if (entry.phase === 'user_input') {
    return (
      <Box key={`history-${index}`}>
        {index > 0 && <TimeStamp time={timestamp} />}
        <MessageContainer isUser={true}>
          <CollapsibleText text={entry.prompt} />
        </MessageContainer>
      </Box>
    );
  } else if (entry.phase === 'ai_response') {
    return (
      <Box key={`history-${index}`}>
        {renderAIResponse()}
      </Box>
    );
  } else if (entry.phase === 'error') {
    return (
      <Box key={`history-${index}`} px={4} py={2}>
        <Alert status="error" borderRadius="md">
          <AlertIcon />
          {entry.error || 'An error occurred during processing'}
        </Alert>
      </Box>
    );
  }

  // Fallback for unknown phases
  return null;
};

// Main TaskHistory component
const TaskHistory = () => {
  const taskHistory = useAppState((state) => state.currentTask.history);
  const taskStatus = useAppState((state) => state.currentTask.status);
  const actionStatus = useAppState((state) => state.currentTask.actionStatus);
  const consecutiveFailures = useAppState((state) => state.currentTask.consecutiveFailures);
  const lastActionResult = useAppState((state) => state.currentTask.lastActionResult);
  
  if (taskHistory.length === 0) {
    return (
      <VStack spacing={4} p={8} textAlign="center" color="gray.500">
      </VStack>
    );
  }

  // Transform the API history to our UI format by grouping user inputs with their AI responses
  const enhancedHistory: EnhancedHistoryEntry[] = [];
  let currentUserEntry: EnhancedHistoryEntry | null = null;
  let aiResponses: EnhancedHistoryEntry[] = [];

  taskHistory.forEach((entry) => {
    // Only process entries that are either:
    // 1. User messages from the bottom text box (no response)
    // 2. AI responses to user messages
    if (!entry.response) {
      // This is a user input from the bottom text box
      if (currentUserEntry) {
        // Push the previous user entry and its AI responses if they exist
        enhancedHistory.push(currentUserEntry);
        if (aiResponses.length > 0) {
          enhancedHistory.push(...aiResponses);
        }
      }
      // Start a new user entry
      currentUserEntry = {
        ...entry,
        userInput: entry.prompt,
        phase: 'user_input' as const,
        timestamp: entry.timestamp || new Date().toISOString()
      };
      aiResponses = [];
    } else if (currentUserEntry) {
      // This is an AI response to the current user message
      aiResponses.push({
        ...entry,
        aiResponse: entry.response,
        phase: 'ai_response' as const,
        timestamp: entry.timestamp || new Date().toISOString()
      });
    }
    // Ignore any other entries (system prompts, etc.)
  });

  // Push the last user entry and its responses if they exist
  if (currentUserEntry) {
    enhancedHistory.push(currentUserEntry);
    if (aiResponses.length > 0) {
      enhancedHistory.push(...aiResponses);
    }
  }
  
  // Group entries by session (using timestamp to determine breaks)
  const sessionGroups: EnhancedHistoryEntry[][] = [];
  let currentSession: EnhancedHistoryEntry[] = [];
  
  enhancedHistory.forEach((entry, index) => {
    if (index === 0) {
      currentSession.push(entry);
    } else {
      const prevEntry = enhancedHistory[index - 1];
      const timeDiff = new Date(entry.timestamp).getTime() - new Date(prevEntry.timestamp).getTime();
      
      // If more than 30 minutes between entries, start a new session
      if (timeDiff > 30 * 60 * 1000) {
        sessionGroups.push([...currentSession]);
        currentSession = [entry];
      } else {
        currentSession.push(entry);
      }
    }
    
    // Add the last session if we've reached the end
    if (index === enhancedHistory.length - 1) {
      sessionGroups.push([...currentSession]);
    }
  });

  // Reverse the sessions to show newest at the bottom
  const reversedSessions = [...sessionGroups].reverse();
  
  return (
    <VStack spacing={0} align="stretch" w="full" pb={8}>
      {reversedSessions.map((session, sessionIndex) => (
        <Box key={`session-${sessionIndex}`}>
          {sessionIndex > 0 && (
            <SessionDivider timestamp={session[0].timestamp} />
          )}
          
          {session.map((entry, entryIndex) => (
            <TaskHistoryItem 
              key={`entry-${sessionIndex}-${entryIndex}`} 
              index={entryIndex} 
              entry={entry} 
            />
          ))}
        </Box>
      ))}
      
      {/* Show detailed status when task is running */}
      {taskStatus === 'running' && (
        <VStack spacing={3} my={4} p={4} bg={useColorModeValue("blue.50", "blue.900")} borderRadius="md" mx={4}>
          {/* Main progress indicator */}
          <HStack spacing={3} width="100%">
            <Spinner size="sm" color="blue.500" />
            <VStack spacing={1} align="start" flex={1}>
              <Text fontSize="sm" fontWeight="medium" color="blue.700">
                {actionStatus === 'pulling-dom' && 'Analyzing page content...'}
                {actionStatus === 'transforming-dom' && 'Processing page structure...'}
                {actionStatus === 'performing-query' && 'Planning next action...'}
                {actionStatus === 'performing-action' && 'Executing action...'}
                {actionStatus === 'waiting' && 'Waiting for page to load...'}
                {actionStatus === 'initializing' && 'Starting task...'}
                {actionStatus === 'ai-recovery' && 'AI attempting recovery from failed actions...'}
                {actionStatus === 'idle' && 'Task in progress...'}
              </Text>
              
              {/* Show recovery info if there are recent failures */}
              {consecutiveFailures > 0 && (
                <HStack spacing={2}>
                  <WarningIcon color="orange.500" boxSize="12px" />
                  <Text fontSize="xs" color="orange.600">
                    {consecutiveFailures === 1 ? 'Recovering from 1 failed action' : 
                     consecutiveFailures === 2 ? 'Recovering from 2 failed actions' :
                     'Final recovery attempt (3/3 failures)'}
                    {lastActionResult?.error && actionStatus === 'performing-query' && (
                      <Text as="span" color="gray.600"> - AI analyzing error and planning alternative approach</Text>
                    )}
                  </Text>
                </HStack>
              )}
              
              {/* Show last action result if it failed */}
              {lastActionResult && !lastActionResult.success && actionStatus === 'performing-query' && (
                <Text fontSize="xs" color="gray.600" noOfLines={2}>
                  Previous error: {lastActionResult.error?.substring(0, 100)}
                  {lastActionResult.error && lastActionResult.error.length > 100 ? '...' : ''}
                </Text>
              )}
            </VStack>
          </HStack>
          
          {/* Progress bar */}
          <Progress 
            size="xs" 
            isIndeterminate 
            colorScheme="blue" 
            width="100%" 
            borderRadius="full"
          />
        </VStack>
      )}
    </VStack>
  );
};

export default TaskHistory; 