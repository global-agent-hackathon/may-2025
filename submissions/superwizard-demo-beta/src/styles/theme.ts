import { extendTheme } from '@chakra-ui/react';
import { FONT_FAMILY } from './fonts';

// Create a custom theme to match our design
const theme = extendTheme({
  // Custom breakpoints with 'md' at 890px instead of default 768px
  breakpoints: {
    base: '0em',
    sm: '30em',
    md: '55.625em', // 890px
    lg: '62em',
    xl: '80em',
    '2xl': '96em',
  },
  config: {
    initialColorMode: 'light',
    useSystemColorMode: false,
  },
  fonts: {
    heading: FONT_FAMILY.sansSerif,
    body: FONT_FAMILY.sansSerif,
    mono: FONT_FAMILY.mono,
  },
  styles: {
    global: {
      body: {
        bg: 'white',
        color: 'gray.800',
        fontFamily: FONT_FAMILY.sansSerif,
        letterSpacing: '0.06em',
        overflowX: 'hidden',
        maxWidth: '100vw',
      },
    },
  },
  colors: {
    brand: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
  },
  components: {
    Button: {
      baseStyle: {
        fontWeight: 'medium',
        borderRadius: 'md',
        letterSpacing: '0.06em',
      },
      variants: {
        solid: {
          bg: 'gray.800',
          color: 'white',
          _hover: {
            bg: 'gray.700',
          },
        },
        ghost: {
          color: 'gray.600',
          _hover: {
            bg: 'gray.100',
          },
        },
      },
    },
    Avatar: {
      baseStyle: {
        container: {
          bg: 'gray.700',
          color: 'white',
        },
      },
    },
    Heading: {
      baseStyle: {
        fontWeight: '600',
        letterSpacing: '0.06em',
      },
    },
    Text: {
      baseStyle: {
        lineHeight: 'tall',
        letterSpacing: '0.06em',
      },
    },
    Textarea: {
      baseStyle: {
        fontFamily: FONT_FAMILY.sansSerif,
        letterSpacing: '0.06em',
      },
      variants: {
        outline: {
          border: '1px solid',
          borderColor: 'gray.200',
          _focus: {
            borderColor: 'gray.400',
            boxShadow: 'none',
          },
        },
      },
    },
    Box: {
      variants: {
        card: {
          bg: 'white',
          borderRadius: 'lg',
          boxShadow: 'none',
          p: 4,
        },
      },
    },
    Menu: {
      baseStyle: {
        list: {
          boxShadow: 'none',
          border: '1px solid',
          borderColor: 'gray.100',
        },
        item: {
          letterSpacing: '0.06em',
          _hover: {
            bg: 'gray.50',
          },
          _focus: {
            bg: 'gray.50',
          },
        },
      },
    },
  },
});

export default theme; 