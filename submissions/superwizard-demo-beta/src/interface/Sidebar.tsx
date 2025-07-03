import React from 'react';
import { 
  Box, 
  useColorModeValue,
  useBreakpointValue
} from '@chakra-ui/react';

interface SidebarProps {
  onNewChat: () => void;
  isOpen?: boolean;
  onClose?: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onNewChat, isOpen = false, onClose }) => {
  const bgColor = useColorModeValue("white", "gray.800");
  const borderColor = useColorModeValue("gray.100", "gray.700");
  
  // Use Chakra UI's breakpoint value hook for responsive behavior
  const isDesktop = useBreakpointValue({ base: false, md: true });

  return (
    <Box 
      w="280px" 
      h="100vh" 
      bg={bgColor}
      borderRight="1px solid" 
      borderColor={borderColor}
      pt={4}
      overflowY="auto"
      position="relative"
      transition="all 0.2s"
      borderTopRightRadius={{ base: "28px", md: "0" }}
      borderBottomRightRadius={{ base: "28px", md: "0" }}
    >
      {/* Empty sidebar */}
    </Box>
  );
};

export default Sidebar; 