import React from 'react';
import { Box, Select, Text, Radio, RadioGroup, Stack, Divider } from '@chakra-ui/react';
import { useAppState } from '../../state/store';
import { getConfiguredProviders, getAvailableModels, getFriendlyModelName, PROVIDERS } from '../../general/providers/config';

interface ModelDropdownProps {
  inMenu?: boolean;
}

const ModelDropdown = ({ inMenu = false }: ModelDropdownProps) => {
  const { selectedModel, apiKeys, updateSettings } = useAppState((state) => ({
    selectedModel: state.settings.selectedModel,
    apiKeys: state.settings.apiKeys,
    updateSettings: state.settings.actions.update,
  }));

  const configuredProviders = getConfiguredProviders(apiKeys);
  const availableModels = getAvailableModels(apiKeys);

  if (configuredProviders.length === 0) return null;

  const handleModelChange = (value: string) => {
    updateSettings({ selectedModel: value });
  };

  // When in a menu, use RadioGroup instead of Select
  if (inMenu) {
    return (
      <Box width="100%" p={1}>
        <Text fontSize="sm" fontWeight="medium" mb={2}>Select Model</Text>
        <RadioGroup onChange={handleModelChange} value={selectedModel || ''}>
          <Stack direction="column" spacing={1}>
            {configuredProviders.map((provider, index) => (
              <React.Fragment key={provider.id}>
                {index > 0 && <Divider my={1} />}
                <Text fontSize="xs" fontWeight="bold" color="gray.500" mt={1}>
                  {provider.displayName}
                </Text>
                {availableModels[provider.id]?.map((modelId) => (
                  <Radio key={modelId} value={modelId} size="sm">
                    <Text fontWeight="medium">{getFriendlyModelName(modelId)}</Text>
                  </Radio>
                ))}
              </React.Fragment>
            ))}
          </Stack>
        </RadioGroup>
      </Box>
    );
  }

  // Default Select dropdown for non-menu contexts
  return (
    <Select
      value={selectedModel || ''}
      onChange={(e) => updateSettings({ selectedModel: e.target.value })}
      size="sm"
      bg="white"
      borderColor="gray.300"
      _hover={{ borderColor: 'gray.400' }}
      _focus={{ borderColor: 'blue.500', boxShadow: 'none' }}
    >
      {configuredProviders.map((provider) => (
        <optgroup key={provider.id} label={provider.displayName}>
          {availableModels[provider.id]?.map((modelId) => (
            <option key={modelId} value={modelId}>
              {getFriendlyModelName(modelId)}
            </option>
          ))}
        </optgroup>
      ))}
    </Select>
  );
};

export default ModelDropdown; 