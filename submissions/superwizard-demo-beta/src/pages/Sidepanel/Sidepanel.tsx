import React, { useEffect } from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import { callRPC } from '../../general/browser/pageRPC';
import { getCurrentTab } from '../../general/utils/utils';
import theme from '../../styles/theme';
import Interface from '../../interface';

const Sidepanel: React.FC = () => {
  useEffect(() => {
    const initializeSidebar = async () => {
      try {
        const tab = await getCurrentTab();
        if (tab?.id) {
          await chrome.tabs.sendMessage(tab.id, { type: 'SIDEBAR_ACTIVATED' });
          console.log('Sidebar activation message sent');
        }
      } catch (error) {
        console.error('Failed to initialize sidebar:', error);
      }
    };

    const cleanupSidebar = async () => {
      try {
        const tab = await getCurrentTab();
        if (tab?.id) {
          await chrome.tabs.sendMessage(tab.id, { type: 'SIDEBAR_DEACTIVATED' });
          console.log('Sidebar deactivation message sent');
        }
      } catch (error) {
        console.error('Failed to cleanup sidebar:', error);
      }
    };

    initializeSidebar();

    // Cleanup when the sidebar is closed
    return () => {
      cleanupSidebar();
    };
  }, []); // Run once when component mounts

  return (
    <ChakraProvider theme={theme}>
      <Interface />
    </ChakraProvider>
  );
};

export default Sidepanel; 