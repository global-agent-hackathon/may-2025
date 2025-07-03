import getAnnotatedDOM, {
  getUniqueElementSelectorId,
} from '../../pages/Content/getAnnotatedDOM';
import { sleep } from '../utils/utils';

export const rpcMethods = {
  getAnnotatedDOM,
  getUniqueElementSelectorId,
} as const;

export type RPCMethods = typeof rpcMethods;
type MethodName = keyof RPCMethods;
type Payload<T extends MethodName> = Parameters<RPCMethods[T]>;
type MethodRT<T extends MethodName> = ReturnType<RPCMethods[T]>;

// Call this function from the content script
export const callRPC = async <T extends MethodName>(
  type: keyof typeof rpcMethods,
  payload?: Payload<T>,
  maxTries = 1
): Promise<MethodRT<T>> => {
  let queryOptions = { active: true, currentWindow: true };
  let activeTab = (await chrome.tabs.query(queryOptions))[0];

  // If the active tab is a chrome-extension:// page, then we need to get some random other tab for testing
  if (activeTab.url?.startsWith('chrome')) {
    queryOptions = { active: false, currentWindow: true };
    activeTab = (await chrome.tabs.query(queryOptions))[0];
  }

  if (!activeTab?.id) throw new Error('No active tab found');

  let err: any;
  for (let i = 0; i < maxTries; i++) {
    try {
      const response = await chrome.tabs.sendMessage(activeTab.id, {
        type,
        payload: payload || [],
      });
      return response;
    } catch (e) {
      if (i === maxTries - 1) {
        // Last try, throw the error
        err = e;
      } else {
        // Content script may not have loaded, retry
        console.error(e);
        await sleep(300);
      }
    }
  }
  throw err;
};

const isKnownMethodName = (type: string): type is MethodName => {
  return type in rpcMethods;
};

// This function should run in the content script
export const watchForRPCRequests = () => {
  chrome.runtime.onMessage.addListener(
    (message, sender, sendResponse): true | undefined => {
      const type = message.type;
      if (isKnownMethodName(type)) {
        try {
          // @ts-expect-error we need to type payload
          const resp = rpcMethods[type](...message.payload);
          
          // Check if resp is promise-like
          if (resp !== null && 
              typeof resp === 'object' && 
              'then' in resp && 
              typeof (resp as any).then === 'function') {
            // Handle as promise
            (resp as Promise<unknown>).then(
              (resolvedResp) => sendResponse(resolvedResp),
              (error) => sendResponse({ error: String(error) })
            );
            return true; // Keep the message channel open for async response
          } else {
            // Handle as synchronous response
            sendResponse(resp);
          }
        } catch (error) {
          sendResponse({ error: String(error) });
        }
      }
    }
  );
}; 