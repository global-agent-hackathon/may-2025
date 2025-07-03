import { ChakraProvider } from '@chakra-ui/react';
import React from 'react';
import { useAppState } from './state/store';
import SetAPIKey from './interface/settings/SetAPIKey';
import Interface from './interface';
import theme from './styles/theme';
import { hasValidProvider } from './general/providers/config';
// Import fonts
import './styles/fonts';

const App = () => {
  const { apiKeys, selectedModel, localhostConnected } = useAppState((state) => ({
    apiKeys: state.settings.apiKeys,
    selectedModel: state.settings.selectedModel,
    localhostConnected: state.settings.localhostConnected
  }));
  const hasValidApiKey = hasValidProvider(apiKeys, selectedModel, localhostConnected);

  return (
    <ChakraProvider theme={theme}>
      {hasValidApiKey ? (
        <Interface />
      ) : (
        <SetAPIKey />
      )}
    </ChakraProvider>
  );
};

export default App; 