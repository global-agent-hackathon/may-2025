// API base URL from environment variables - use a local backend URL for development if not provided
const API_BASE_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8080';

console.log('Using API base URL:', API_BASE_URL);

/**
 * Generic API client for making requests to the backend
 */
export const apiClient = {
  /**
   * Make a GET request to the API
   */
  async get<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('token');
    console.log(`Making GET request to: ${API_BASE_URL}${endpoint}`);
    
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
          ...options.headers
        },
        ...options
      });

      console.log(`Response status: ${response.status}`);
      
      if (!response.ok) {
        // Try to get more error details from the response
        let errorDetails = '';
        try {
          const errorData = await response.json();
          errorDetails = JSON.stringify(errorData);
        } catch (e) {
          // If we can't parse JSON, just use text
          errorDetails = await response.text();
        }
        
        console.error(`API error (${response.status}): ${errorDetails}`);
        throw new Error(`API error: ${response.status} - ${errorDetails}`);
      }

      const data = await response.json();
      console.log('Response data sample:', JSON.stringify(data).substring(0, 200) + '...');
      return data;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  },

  /**
   * Make a POST request to the API
   */
  async post<T>(endpoint: string, data: any, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
      },
      body: JSON.stringify(data),
      ...options
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Make a DELETE request to the API
   */
  async delete<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const token = localStorage.getItem('token');
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Accept': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }

    return response.json();
  },

  /**
   * Upload files to the API
   */
  async uploadFiles<T>(files: File[], companyName: string, options: { threadId?: string } = {}): Promise<T> {
    const token = localStorage.getItem('token');
    const formData = new FormData();
    files.forEach(file => {
      formData.append('file', file);
    });
    // Also append the array of files as 'files' (if required by backend)
    files.forEach(file => {
      formData.append('files', file);
    });
    if (options.threadId) {
      formData.append('threadId', options.threadId);
    }
    const response = await fetch(`${API_BASE_URL}/files/upload/${encodeURIComponent(companyName)}`, {
      method: 'POST',
      headers: {
        ...(token ? { 'Authorization': `Bearer ${token}` } : {})
      },
      body: formData
    });
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    return response.json();
  }
}; 