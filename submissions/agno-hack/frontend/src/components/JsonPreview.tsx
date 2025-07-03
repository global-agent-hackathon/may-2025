import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import { TestConfig } from '../types/TestConfig';
import toast from 'react-hot-toast';

interface JsonPreviewProps {
  testConfig: TestConfig;
}

const JsonPreview: React.FC<JsonPreviewProps> = ({ testConfig }) => {
  const [copied, setCopied] = useState(false);

  const formattedJson = JSON.stringify(testConfig, null, 4);

  const handleCopy = () => {
    navigator.clipboard.writeText(formattedJson);
    setCopied(true);
    toast.success('JSON copied to clipboard!');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-primary-800 rounded-xl shadow-sm p-6 text-white">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-semibold">JSON Output</h2>
        <button
          onClick={handleCopy}
          className="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-primary-700 hover:bg-primary-600 transition-colors focus:outline-none focus:ring-2 focus:ring-primary-500"
          aria-label="Copy JSON to clipboard"
        >
          {copied ? (
            <>
              <Check size={16} className="mr-1.5 text-green-400" />
              <span className="text-green-400">Copied!</span>
            </>
          ) : (
            <>
              <Copy size={16} className="mr-1.5" />
              <span>Copy</span>
            </>
          )}
        </button>
      </div>
      
      <div className="flex-1 overflow-auto bg-primary-900/50 rounded-md p-4">
        <pre className="text-sm font-mono text-primary-50 whitespace-pre-wrap break-words">
          {formattedJson}
        </pre>
      </div>
      
      <div className="mt-4 text-sm text-primary-200">
        <p>This JSON configuration can be used with compatible web testing frameworks.</p>
      </div>
    </div>
  );
};

export default JsonPreview