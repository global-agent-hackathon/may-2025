import React from 'react';
import {
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  Text,
  Button,
  Stack,
  Box,
  Select,
  FormControl,
  FormLabel,
  HStack,
  Switch,
  Flex,
  Tooltip,
} from '@chakra-ui/react';
import { useAppState } from '../../state/store';

interface OptionsDropdownProps {
  inMenu?: boolean;
}

export const OptionsDropdown: React.FC<OptionsDropdownProps> = ({ inMenu = false }) => {
  const { cursorEnabled, toggleCursor, clearAllApiKeys } = useAppState((state) => ({
    cursorEnabled: state.settings.cursorEnabled,
    toggleCursor: state.settings.actions.toggleCursor,
    clearAllApiKeys: state.settings.actions.clearAllApiKeys,
  }));

  // When in a menu, use buttons instead of a nested menu
  if (inMenu) {
    return (
      <Box width="100%" p={1}>
        <Text fontSize="sm" fontWeight="medium" mb={2}>Options</Text>
        <Stack spacing={2}>
          <Flex justify="space-between" align="center" width="100%" py={1}>
            <Text fontSize="sm">Show Cursor</Text>
            <Switch 
              size="sm" 
              isChecked={cursorEnabled} 
              onChange={toggleCursor}
              colorScheme="blue"
            />
          </Flex>
          <Button size="sm" variant="outline" onClick={clearAllApiKeys} width="100%">
            Clear API Keys
          </Button>
          <Button 
            size="sm" 
            variant="outline" 
            as="a" 
            href="https://github.com/amirulhamizan12/superwizard-ai" 
            target="_blank"
            width="100%"
          >
            About
          </Button>
        </Stack>
      </Box>
    );
  }

  return (
    <Menu>
      <MenuButton as={Button} size="sm" variant="ghost">
        Options
      </MenuButton>
      <MenuList>
        <MenuItem>
          <Flex justify="space-between" align="center" width="100%">
            <Text>Show Cursor</Text>
            <Switch 
              size="sm" 
              isChecked={cursorEnabled} 
              onChange={toggleCursor}
              colorScheme="blue"
            />
          </Flex>
        </MenuItem>
        <MenuItem onClick={clearAllApiKeys}>Clear API Keys</MenuItem>
        <MenuItem as="a" href="https://github.com/amirulhamizan12/superwizard-ai" target="_blank">
          About
        </MenuItem>
      </MenuList>
    </Menu>
  );
}; 