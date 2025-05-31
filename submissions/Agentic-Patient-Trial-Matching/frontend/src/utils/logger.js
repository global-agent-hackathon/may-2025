import log from 'loglevel';

// Set the logging level based on environment
const logLevel = import.meta.env.PROD
    ? log.levels.INFO 
    : (import.meta.env.VITE_LOG_LEVEL === 'DEBUG' 
        ? log.levels.DEBUG 
        : log.levels.INFO);

// Configure the logger
log.setLevel(logLevel);

// Add timestamps to log messages
const originalFactory = log.methodFactory;
log.methodFactory = function (methodName, logLevel, loggerName) {
    const rawMethod = originalFactory(methodName, logLevel, loggerName);
    
    return function (message) {
        const timestamp = new Date().toISOString();
        rawMethod(`[${timestamp}] ${message}`);
    };
};

log.setLevel(log.getLevel()); // Apply format changes

export const logger = {
    debug: log.debug,
    info: log.info,
    warn: log.warn,
    error: log.error,
    
    // Utility method to set log level at runtime
    setLogLevel: (level) => {
        const levels = {
            'DEBUG': log.levels.DEBUG,
            'INFO': log.levels.INFO,
            'WARN': log.levels.WARN,
            'ERROR': log.levels.ERROR
        };
        
        if (levels[level]) {
            log.setLevel(levels[level]);
            logger.info(`Log level set to: ${level}`);
        } else {
            logger.warn(`Invalid log level: ${level}. Using default.`);
        }
    }
};

export default logger;