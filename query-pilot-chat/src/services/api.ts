import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface SearchResponse {
  results: Array<{
    id: string;
    content: string;
    type: string;
  }>;
}

export interface ExplanationResponse {
  content: string;
  problems: string;
  visuals: string;
  type: string;
}

export interface TutoringResponse {
  type: string;
  content: string;
  grammar: string;
  vocabulary: string;
  pronunciation: string;
  culture: string;
  dialogue: string;
}

export const tutorApi = {
  search: async (subject: string, query: string, language_code?: string): Promise<SearchResponse> => {
    try {
      console.log('[API Search] Subject:', subject);
      console.log('[API Search] Query:', query);
      console.log('[API Search] Language Code:', language_code);

      const payload = subject === 'language' 
        ? { query, language_code }
        : { query };
      
      console.log('[API Search] Request Payload:', payload);
      const response = await api.post(`/${subject}/search`, payload);
      console.log('[API Search] Response:', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error searching ${subject} concepts:`, error);
      throw error;
    }
  },

  explain: async (subject: string, query: string, language_code?: string): Promise<ExplanationResponse | TutoringResponse> => {
    try {
      console.log('[API Explain] Subject:', subject);
      console.log('[API Explain] Query:', query);
      console.log('[API Explain] Language Code:', language_code);

      const payload = subject === 'language'
        ? { query, language_code }
        : { query };
      
      console.log('[API Explain] Request Payload:', payload);
      const response = await api.post(`/${subject}/explain`, payload);
      console.log('[API Explain] Response:', response.data);
      return response.data;
    } catch (error) {
      console.error(`Error getting ${subject} concept explanation:`, error);
      throw error;
    }
  },

  streamExplain: async (subject: string, query: string, onData: (data: ExplanationResponse | TutoringResponse) => void, language_code?: string) => {
    try {
      console.log('[API Stream] Subject:', subject);
      console.log('[API Stream] Query:', query);
      console.log('[API Stream] Language Code:', language_code);

      const payload = subject === 'language'
        ? { query, language_code }
        : { query };

      console.log('[API Stream] Request Payload:', payload);
      
      const response = await fetch(`${API_BASE_URL}/${subject}/explain/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      console.log('[API Stream] Response Status:', response.status);
      console.log('[API Stream] Response Headers:', Object.fromEntries(response.headers.entries()));

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error('No reader available');

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n').filter(line => line.trim());

        for (const line of lines) {
          try {
            const data = subject === 'language' 
              ? (JSON.parse(line) as TutoringResponse)
              : (JSON.parse(line) as ExplanationResponse);
            
            console.log('[API Stream] Received Data Type:', subject === 'language' ? 'TutoringResponse' : 'ExplanationResponse');
            console.log('[API Stream] Received Data:', data);
            
            onData(data);
          } catch (e) {
            console.error('[API Stream] Error parsing stream data:', e);
          }
        }
      }
    } catch (error) {
      console.error(`Error streaming ${subject} explanation:`, error);
      throw error;
    }
  },

  // Add the createDialogue method
  createDialogue: async (topic: string, language_code: string) => {
    try {
      console.log('[API Dialogue] Topic:', topic);
      console.log('[API Dialogue] Language Code:', language_code);
      const response = await api.post('/language/dialogue', {
        topic: topic,
        language_code: language_code,
        agree: true
      });
      console.log('[API Dialogue] Response:', response.data);
      return response.data; // Expects { type: 'dialogue' | 'info' | 'error', content: string }
    } catch (error) {
      console.error('Error creating dialogue:', error);
      // Return an error structure consistent with other responses
      return {
        type: 'error',
        content: error.response?.data?.detail || error.message || 'Failed to create dialogue.'
      };
    }
  }
};