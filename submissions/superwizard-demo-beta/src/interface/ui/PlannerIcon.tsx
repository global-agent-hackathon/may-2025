import React from 'react';
import { Box, Flex, Icon } from '@chakra-ui/react';

interface PlannerIconProps {
  boxSize?: string;
  color?: string;
}

export const PlannerIcon: React.FC<PlannerIconProps> = (props) => {
  return (
    <Flex
      width="40px"
      height="40px"
      borderRadius="full"
      bg="orange.400"
      alignItems="center"
      justifyContent="center"
      color="white"
    >
      <Icon viewBox="0 0 24 24" boxSize={5}>
        <path
          fill="currentColor"
          d="M19,3H14.82C14.4,1.84 13.3,1 12,1C10.7,1 9.6,1.84 9.18,3H5C3.9,3 3,3.9 3,5V19C3,20.1 3.9,21 5,21H19C20.1,21 21,20.1 21,19V5C21,3.9 20.1,3 19,3M12,3C12.55,3 13,3.45 13,4C13,4.55 12.55,5 12,5C11.45,5 11,4.55 11,4C11,3.45 11.45,3 12,3M7,7H17V5H19V19H5V5H7V7M12,17V15H17V17H12M12,11V9H17V11H12M8,9V11H7V9H8M8,15V17H7V15H8Z"
        />
      </Icon>
    </Flex>
  );
}; 