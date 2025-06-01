// Increase Node.js EventEmitter limit to prevent MaxListenersExceededWarning
import { EventEmitter } from 'events';

// Setting the max listeners to a higher value to avoid the warning
// "Possible EventEmitter memory leak detected. 11 unhandledRejection listeners added to [process]"
EventEmitter.defaultMaxListeners = 15; 