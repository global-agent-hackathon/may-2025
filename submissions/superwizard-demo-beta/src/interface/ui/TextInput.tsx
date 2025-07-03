import { Textarea, TextareaProps } from '@chakra-ui/react';
import ResizeTextarea, { TextareaAutosizeProps } from 'react-textarea-autosize';
import React, { useEffect, useRef } from 'react';

// TextInput component for text input functionality
export const TextInput = React.forwardRef<HTMLTextAreaElement, TextareaProps & Pick<TextareaAutosizeProps, 'maxRows'>>(
  (props, ref) => {
    return (
      <Textarea
        minH="unset"
        overflow="auto"
        w="100%"
        resize="none"
        ref={ref}
        minRows={1}
        as={ResizeTextarea}
        {...props}
      />
    );
  }
); 