import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Button, 
  FormControl, 
  FormLabel, 
  Input, 
  Text, 
  VStack, 
  Link, 
  IconButton,
  InputGroup,
  InputRightElement,
  Heading,
  Container,
  Flex,
  useColorModeValue,
  Card,
  CardBody,
  Image,
  Center,
  Divider,
  useToast,
  HStack,
  Badge,
  Icon,
  Stack,
  SimpleGrid
} from '@chakra-ui/react';
import { useAppState } from '../../state/store';
import { ViewIcon, ViewOffIcon, ExternalLinkIcon, CheckCircleIcon, InfoIcon, RepeatIcon } from '@chakra-ui/icons';
import { PROVIDERS, hasAnyApiKey } from '../../general/providers/config';

const SetAPIKey = () => {
  const { apiKeys, updateApiKey, updateLocalhostStatus } = useAppState((state) => ({
    apiKeys: state.settings.apiKeys,
    updateApiKey: state.settings.actions.updateApiKey,
    updateLocalhostStatus: state.settings.actions.updateLocalhostStatus,
  }));

  const [localApiKeys, setLocalApiKeys] = useState<Record<string, string>>(
    Object.keys(PROVIDERS).reduce((acc, providerId) => {
      acc[providerId] = apiKeys[providerId] || '';
      return acc;
    }, {} as Record<string, string>)
  );
  
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>(
    Object.keys(PROVIDERS).reduce((acc, providerId) => {
      acc[providerId] = false;
      return acc;
    }, {} as Record<string, boolean>)
  );

  const [localhostStatus, setLocalhostStatus] = useState<'checking' | 'connected' | 'disconnected'>('checking');

  const toast = useToast();
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const headingColor = useColorModeValue('gray.800', 'white');
  const inputBg = useColorModeValue('gray.50', 'gray.700');
  const hoverBg = useColorModeValue('gray.100', 'gray.600');

  const handleApiKeyChange = (providerId: string, value: string) => {
    setLocalApiKeys(prev => ({
      ...prev,
      [providerId]: value
    }));
  };

  const togglePasswordVisibility = (providerId: string) => {
    setShowPasswords(prev => ({
      ...prev,
      [providerId]: !prev[providerId]
    }));
  };

  const checkLocalhostStatus = async () => {
    try {
      setLocalhostStatus('checking');
      const response = await fetch('http://localhost:7777/health', {
        method: 'GET',
        // Add timeout to prevent hanging
        signal: AbortSignal.timeout(5000)
      });
      
      if (response.ok) {
        setLocalhostStatus('connected');
        updateLocalhostStatus(true);
      } else {
        setLocalhostStatus('disconnected');
        updateLocalhostStatus(false);
      }
    } catch (error) {
      console.log('Localhost server not available:', error);
      setLocalhostStatus('disconnected');
      updateLocalhostStatus(false);
    }
  };

  // Check localhost status on component mount and periodically
  useEffect(() => {
    checkLocalhostStatus();
    
    // Check every 10 seconds
    const interval = setInterval(checkLocalhostStatus, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const saveKeys = () => {
    let hasAtLeastOneKey = false;
    
    // Check if localhost is connected (counts as a valid provider)
    if (localhostStatus === 'connected') {
      hasAtLeastOneKey = true;
    }
    
    // Save all configured keys
    Object.entries(localApiKeys).forEach(([providerId, key]) => {
      const trimmedKey = key.trim();
      if (trimmedKey) {
        hasAtLeastOneKey = true;
        updateApiKey(providerId, trimmedKey);
      } else {
        updateApiKey(providerId, null);
      }
    });

    if (!hasAtLeastOneKey) {
      toast({
        title: 'No Valid Providers',
        description: 'Please enter at least one API key or ensure your localhost server is running.',
        status: 'warning',
        duration: 5000,
        isClosable: true,
        position: "top",
      });
      return;
    }

    // If localhost is connected but no model selected, set localhost as default
    const state = useAppState.getState();
    if (localhostStatus === 'connected' && !Object.values(localApiKeys).some(key => key.trim())) {
      state.settings.actions.update({ selectedModel: 'local-model' });
    }

    toast({
      title: 'Success!',
      description: 'Your settings have been saved. Redirecting to chat interface...',
      status: 'success',
      duration: 2000,
      isClosable: true,
      position: "top",
    });
  };

  const isAnythingEntered = localhostStatus === 'connected' || Object.values(localApiKeys).some(key => key.trim());
  const hasValidKey = (providerId: string) => {
    if (providerId === 'localhost') {
      return localhostStatus === 'connected';
    }
    return localApiKeys[providerId]?.trim().length > 0;
  };

  return (
    <Container maxW="2xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* API Keys Grid */}
        <SimpleGrid columns={{ base: 1, md: 1 }} spacing={6}>
          {Object.values(PROVIDERS).map((provider) => (
            <Card 
              key={provider.id}
              bg={cardBg} 
              borderRadius="2xl" 
              overflow="hidden"
              borderColor={borderColor}
              borderWidth="1px"
              shadow="sm"
              transition="all 0.2s ease"
              _hover={{
                shadow: "md",
                transform: "translateY(-2px)"
              }}
            >
              <CardBody p={8}>
                <VStack spacing={5} align="stretch">
                  {/* Provider Header */}
                  <HStack justify="space-between" align="flex-start">
                    <VStack align="flex-start" spacing={1} flex={1}>
                      <HStack spacing={3}>
                        <Heading size="md" color={headingColor} fontWeight="600">
                          {provider.displayName}
                        </Heading>
                        {(hasValidKey(provider.id) || provider.id === 'localhost') && (
                          <Badge 
                            colorScheme={
                              provider.id === 'localhost' 
                                ? (localhostStatus === 'connected' ? 'green' : localhostStatus === 'checking' ? 'yellow' : 'red')
                                : 'green'
                            }
                            variant="subtle"
                            borderRadius="full"
                            px={3}
                            py={1}
                          >
                            <HStack spacing={1}>
                              <CheckCircleIcon boxSize={3} />
                              <Text fontSize="xs">
                                {provider.id === 'localhost' 
                                  ? (localhostStatus === 'connected' ? 'Connected' : localhostStatus === 'checking' ? 'Checking...' : 'Not Connected')
                                  : 'Connected'}
                              </Text>
                            </HStack>
                          </Badge>
                        )}
                      </HStack>
                      {provider.description && (
                        <Text fontSize="sm" color={textColor} lineHeight="1.5">
                          {provider.description}
                        </Text>
                      )}
                      {provider.id === 'localhost' && (
                        <Button
                          leftIcon={<RepeatIcon />}
                          size="sm"
                          variant="outline"
                          colorScheme="blue"
                          onClick={checkLocalhostStatus}
                          isLoading={localhostStatus === 'checking'}
                          loadingText="Checking..."
                          borderRadius="lg"
                          mt={3}
                          fontSize="sm"
                          fontWeight="500"
                          _hover={{
                            bg: "blue.50",
                            borderColor: "blue.300",
                            transform: "translateY(-1px)"
                          }}
                          _active={{
                            transform: "translateY(0)"
                          }}
                          transition="all 0.2s ease"
                          shadow="sm"
                          _focus={{
                            boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.15)"
                          }}
                        >
                          Refresh Connection
                        </Button>
                      )}
                    </VStack>
                  </HStack>

                  {/* API Key Input - Only show for non-localhost providers */}
                  {provider.id !== 'localhost' && (
                    <FormControl>
                      <FormLabel 
                        fontSize="sm" 
                        fontWeight="600"
                        color={headingColor}
                        mb={3}
                      >
                        API Key
                        <Badge 
                          ml={2} 
                          colorScheme="blue" 
                          variant="subtle"
                          fontSize="xs"
                          borderRadius="full"
                        >
                          Optional
                        </Badge>
                      </FormLabel>
                      <InputGroup size="lg">
                        <Input
                          pr="4.5rem"
                          type={showPasswords[provider.id] ? 'text' : 'password'}
                          placeholder={provider.apiKeyPlaceholder}
                          value={localApiKeys[provider.id]}
                          onChange={(e) => handleApiKeyChange(provider.id, e.target.value)}
                          borderRadius="xl"
                          fontSize="md"
                          bg={inputBg}
                          borderColor={borderColor}
                          _focus={{
                            borderColor: "blue.400",
                            boxShadow: "0 0 0 3px rgba(66, 153, 225, 0.1)",
                            bg: cardBg
                          }}
                          _hover={{
                            borderColor: "gray.300",
                            bg: hoverBg
                          }}
                          transition="all 0.2s ease"
                        />
                        <InputRightElement h="full">
                          <IconButton
                            aria-label={showPasswords[provider.id] ? "Hide API key" : "Show API key"}
                            size="sm"
                            variant="ghost"
                            onClick={() => togglePasswordVisibility(provider.id)}
                            icon={showPasswords[provider.id] ? <ViewOffIcon /> : <ViewIcon />}
                            borderRadius="lg"
                            _hover={{
                              bg: hoverBg
                            }}
                          />
                        </InputRightElement>
                      </InputGroup>
                    </FormControl>
                  )}

                  {/* Get API Key Link - Only show for non-localhost providers */}
                  {provider.id !== 'localhost' && (
                    <HStack justify="space-between" align="center">
                      <Link
                        href={provider.apiKeyUrl}
                        color="blue.500"
                        isExternal
                        fontSize="sm"
                        fontWeight="500"
                        _hover={{
                          color: "blue.600",
                          textDecoration: "none"
                        }}
                        transition="color 0.2s ease"
                      >
                        <HStack spacing={2}>
                          <Text>Get {provider.displayName} API key</Text>
                          <ExternalLinkIcon boxSize={3} />
                        </HStack>
                      </Link>
                    </HStack>
                  )}
                </VStack>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>



        {/* Save Button */}
        <Button
          onClick={saveKeys}
          colorScheme="blue"
          size="lg"
          isDisabled={!isAnythingEntered}
          borderRadius="xl"
          py={7}
          fontSize="md"
          fontWeight="600"
          shadow="sm"
          _hover={{ 
            transform: 'translateY(-2px)',
            shadow: 'lg',
            transition: 'all 0.2s ease'
          }}
          _active={{
            transform: 'translateY(0)',
            shadow: 'sm'
          }}
          transition="all 0.2s ease"
          leftIcon={<CheckCircleIcon />}
        >
          Save API Keys
        </Button>
      </VStack>
    </Container>
  );
};

export default SetAPIKey; 

// todo: add wellcome page