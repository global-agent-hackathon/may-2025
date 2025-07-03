import React, { useState } from 'react';
import { Box, Flex, IconButton, useToast, VStack, Menu, MenuButton, MenuList, MenuItem, Tooltip, Text } from '@chakra-ui/react';
import { CloseIcon, SettingsIcon, RepeatIcon, ChevronDownIcon } from '@chakra-ui/icons';
import { useAppState } from '../state/store';
import { TextInput } from './ui/TextInput';
import { SendButton } from './ui/SendButton';
import ModelDropdown from './settings/ModelDropdown';
import { OptionsDropdown } from './ui/OptionsDropdown';
import { getFriendlyModelName } from '../general/providers/config';

interface BottomProps {
  handleKeyDown: (e: React.KeyboardEvent) => void;
}

const Bottom: React.FC<BottomProps> = ({ handleKeyDown }) => {
  const state = useAppState((state) => ({
    taskStatus: state.currentTask.status,
    runTask: state.currentTask.actions.runTask,
    interrupt: state.currentTask.actions.interrupt,
    instructions: state.ui.instructions,
    setInstructions: state.ui.actions.setInstructions,
    selectedModel: state.settings.selectedModel,
  }));

  const [isModelMenuOpen, setIsModelMenuOpen] = useState(false);

  const taskInProgress = state.taskStatus === 'running';
  const toast = useToast();

  const runTask = () => {
    if (state.instructions) {
      state.runTask((message: string) => {
        toast({
          title: 'Error',
          description: message,
          status: 'error',
          duration: 5000,
          isClosable: true,
          position: "top",
          containerStyle: {
            width: '340px',
            maxWidth: '100%'
          }
        });
      });
      state.setInstructions('');
    }
  };

  const stopTask = () => {
    state.interrupt();
    toast({
      title: 'Task stopped',
      description: 'The AI agent has been stopped',
      status: 'info',
      duration: 3000,
      isClosable: true,
      position: "top",
      containerStyle: {
        width: '340px',
        maxWidth: '100%'
      }
    });
  };

  return (
    <Box 
      position="fixed"
      bottom={0}
      left={{ base: 0, md: "280px" }}
      right={0}
      display="flex"
      justifyContent="center"
      width={{ base: "100%", md: "calc(100% - 280px)" }}
      zIndex={10}
    >
      <Box
        width="100%"
        maxWidth="600px"
        bg="#f6f6f6" 
        p="10px"
        borderTop="none"
        borderColor="#ececec"
        boxShadow="sm"
        borderRadius="32px 32px 0 0"
      >
        <VStack 
          maxW="1200px"  
          mx="auto"
          spacing={2}
          justifyContent="flex-end"
          pb={0}
        >
          {/* Top Row - Text Input */}
          <Flex 
            w="100%"
            border="none"
            borderColor="#ececec"
            bg="#f6f6f6"
            overflow="visible"
            position="relative"
            align="center"
            pl={0}
            pr={0}
          >
            <TextInput
              autoFocus
              placeholder="Chat with Superwizard"
              value={state.instructions || ''}
              isDisabled={taskInProgress}
              onChange={(e) => state.setInstructions(e.target.value)}
              onKeyDown={handleKeyDown}
              resize="none"
              border="none"
              py={2}
              px={2}
              _focus={{
                boxShadow: "none",
                border: "none",
                outline: "none"
              }}
              color="gray.500"
              fontWeight="medium"
              fontSize="md"
              width="100%"
              position="relative"
              zIndex={1}
              lineHeight="1.2"
              minH="auto"
              textAlign="left"
              maxRows={15}
              overflowY="auto"
              css={{
                '&::-webkit-scrollbar': {
                  width: '0px',
                  display: 'none'
                },
                '-ms-overflow-style': 'none',
                'scrollbarWidth': 'none'
              }}
            />
          </Flex>
          
          {/* Bottom Row - Settings, Model Selector and Send Button */}
          <Flex 
            w="100%"
            justify="space-between"
            align="center"
          >
            {/* Left - Settings and Model Selector Buttons */}
            <Flex gap={2} align="center">
              {/* Settings Button */}
              <Tooltip 
                label="Settings" 
                placement="bottom" 
                hasArrow 
                pointerEvents="none"
                gutter={8}
                offset={[0, 4]}
                openDelay={300}
              >
                <Menu closeOnSelect={false}>
                  <MenuButton 
                    as={IconButton}
                    aria-label="Settings"
                    icon={<SettingsIcon boxSize="18px" />}
                    variant="ghost"
                    size="md"
                    color="gray.600"
                    w="36px"
                    h="36px"
                    minW="36px"
                    borderRadius="24px"
                    _hover={{}}
                    bg="#ececec"
                  />
                  <MenuList minWidth="240px">
                    <MenuItem onClick={(e) => e.stopPropagation()}>
                      <OptionsDropdown inMenu={true} />
                    </MenuItem>
                  </MenuList>
                </Menu>
              </Tooltip>

              {/* Model Selector Button */}
              <Tooltip 
                label="Select AI Model" 
                placement="bottom" 
                hasArrow 
                pointerEvents="none"
                gutter={8}
                offset={[0, 4]}
                openDelay={300}
              >
                <Menu 
                  closeOnSelect={false}
                  onOpen={() => setIsModelMenuOpen(true)}
                  onClose={() => setIsModelMenuOpen(false)}
                >
                  <MenuButton 
                    as={IconButton}
                    aria-label="Select AI Model"
                    variant="ghost"
                    size="md"
                    color="#1d7ba7"
                    w="auto"
                    h="20px"
                    minW="100px"
                    maxW="220px"
                    borderRadius="24px"
                    _hover={{}}
                    bg="#ececec"
                    display="flex"
                    alignItems="center"
                    justifyContent="flex-start"
                    pl={2}
                    pr={1}
                  >
                    <Text 
                      fontSize="sm" 
                      fontWeight="semibold"
                      isTruncated
                      textAlign="left"
                      width="auto"
                      color="#1d7ba7"
                      lineHeight="20px"
                      display="flex"
                      alignItems="center"
                      justifyContent="space-between"
                      gap={0.5}
                    >
                      {getFriendlyModelName(state.selectedModel) || 'Select Model'}
                      <ChevronDownIcon 
                        boxSize="24px" 
                        transform={isModelMenuOpen ? 'rotate(180deg)' : 'rotate(0deg)'}
                        transition="transform 0.2s ease"
                        flexShrink={0}
                      />
                    </Text>
                  </MenuButton>
                  <MenuList minWidth="240px">
                    <MenuItem onClick={(e) => e.stopPropagation()}>
                      <ModelDropdown inMenu={true} />
                    </MenuItem>
                  </MenuList>
                </Menu>
              </Tooltip>
            </Flex>
            
            {/* Right - Send Button */}
            <IconButton
              aria-label={taskInProgress ? "Stop task" : "Send message"}
              icon={taskInProgress ? <CloseIcon /> : <SendButton />}
              colorScheme="gray"
              variant="solid"
              size="md"
              onClick={taskInProgress ? stopTask : runTask}
              isDisabled={!taskInProgress && !state.instructions}
              fontSize="14px"
              fontWeight="semibold"
              w="70px"
              h="36px"
              minW="36px"
              bg="#ececec"
              color="gray.600"
              borderRadius="12px"
              _hover={{}}
            />
          </Flex>
        </VStack>
      </Box>
    </Box>
  );
};

export default Bottom;