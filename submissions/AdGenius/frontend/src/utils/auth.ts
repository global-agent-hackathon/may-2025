/**
 * Authentication utilities for token management and redirect handling
 */

// Token constants
const TOKEN_KEY = 'adgenius_token';
const REDIRECT_KEY = 'adgenius_post_login_redirect';

// Token management
export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);

export const setToken = (token: string): void => {
  // Store token in localStorage
  localStorage.setItem(TOKEN_KEY, token);
  
  // Also set as cookie for EventSource requests
  document.cookie = `access_token=${token}; path=/; SameSite=Lax`;
};

export const removeToken = (): void => {
  // Remove from localStorage
  localStorage.removeItem(TOKEN_KEY);
  
  // Remove cookie
  document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Lax';
};

// Redirect path management
export const getRedirectPath = (): string | null => sessionStorage.getItem(REDIRECT_KEY);
export const setRedirectPath = (path: string): void => sessionStorage.setItem(REDIRECT_KEY, path);
export const removeRedirectPath = (): void => sessionStorage.removeItem(REDIRECT_KEY);

// Helper to determine the appropriate redirect path
export const getSafeRedirectPath = (currentPath: string): string => {
  // If current path is login page, redirect to home after authentication
  return currentPath.startsWith('/login') ? '/' : currentPath;
};

// Get both URL path and query params for more accurate redirects
export const getCurrentUrlPath = (): string => {
  return window.location.pathname + window.location.search;
};

// Sets a redirect path in session storage and sanitizes it
export const storeRedirectPath = (path?: string): void => {
  const redirectPath = path || getCurrentUrlPath();
  setRedirectPath(getSafeRedirectPath(redirectPath));
};

// Safely get and clear the redirect path
export const retrieveAndClearRedirectPath = (fallbackPath = '/'): string => {
  const redirectPath = getRedirectPath() || fallbackPath;
  removeRedirectPath();
  return redirectPath === '/login' ? '/' : redirectPath;
}; 