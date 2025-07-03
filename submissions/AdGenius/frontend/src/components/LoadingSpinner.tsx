import React from 'react';

interface LoadingSpinnerProps {
  fullScreen?: boolean;
  size?: 'sm' | 'md' | 'lg';
  color?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  fullScreen = false,
  size = 'md',
  color = 'primary'
}) => {
  // Map sizes to width/height classes
  const sizeClasses = {
    sm: 'h-8 w-8',
    md: 'h-12 w-12',
    lg: 'h-16 w-16'
  };

  // Spinner element
  const spinner = (
    <div 
      className={`animate-spin rounded-full ${sizeClasses[size]} border-t-2 border-b-2 border-${color}`}
      role="status"
      aria-label="Loading"
    />
  );

  // Return either a full-screen spinner or just the spinner element
  return fullScreen ? (
    <div className="h-screen flex items-center justify-center bg-gray-50">
      {spinner}
    </div>
  ) : spinner;
};

export default LoadingSpinner; 