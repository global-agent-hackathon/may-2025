import React, { useState, useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Footer from './components/Footer';
import TestConfigForm from './components/TestConfigForm';
import { TestConfig } from './types/TestConfig';

interface TaskStatus {
  task_id: string;
  status: string;
  progress?: string;
  start_time?: string;
  end_time?: string;
  error?: string;
}

interface ExecutionStep {
  step_number: number;
  action: string;
  result: string;
  timestamp: string;
  screenshot_url?: string;
  screenshot?: string;
}

interface ExecutionResult {
  task_id: string;
  success: boolean;
  timestamp: string;
  task_details: any;
  execution_steps: ExecutionStep[];
  screenshots: string[];
  screenshot_urls: string[];
  full_conversation: any[];
  error?: string;
  log_file?: string;
  detailed_log_file?: string;
  stdout_log_file?: string;
  stderr_log_file?: string;
  agent_thoughts_file?: string;
}

interface AnalysisResult {
  task_id: string;
  analysis_content: string;
  timestamp: string;
}

const API_BASE_URL = 'http://localhost:8000';

// Agent Thoughts Display Component
const AgentThoughtsDisplay: React.FC<{ taskId: string }> = ({ taskId }) => {
  const [agentThoughts, setAgentThoughts] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchThoughts();
  }, [taskId]);

  const fetchThoughts = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await fetch(`${API_BASE_URL}/agent-thoughts/${taskId}`);
      if (response.ok) {
        const text = await response.text();
        setAgentThoughts(text);
      } else {
        setError('Unable to load agent thoughts');
      }
    } catch (err) {
      setError('Error fetching agent thoughts');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-4">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-blue-600">Loading agent thoughts...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-red-600 p-4 bg-red-50 rounded-lg">
        {error}
      </div>
    );
  }

  if (!agentThoughts.trim()) {
    return (
      <div className="text-gray-500 p-4 bg-gray-50 rounded-lg">
        No agent thoughts recorded for this task.
      </div>
    );
  }

  // Parse thoughts into structured format
  const thoughtLines = agentThoughts.split('\n').filter(line => line.trim());
  
  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      {thoughtLines.map((line, index) => {
        const timestampMatch = line.match(/^\[(.*?)\](.*)/);
        if (timestampMatch) {
          const [, timestamp, content] = timestampMatch;
          const actionType = content.includes('ACTION:') ? 'action' : 
                           content.includes('OBSERVATION:') ? 'observation' : 
                           content.includes('DECISION:') ? 'decision' : 'info';
          
          const iconMap = {
            action: '⚡',
            observation: '👁️',
            decision: '🧭',
            info: '💭'
          };
          
          const colorMap = {
            action: 'bg-green-50 border-green-200 text-green-800',
            observation: 'bg-blue-50 border-blue-200 text-blue-800',
            decision: 'bg-purple-50 border-purple-200 text-purple-800',
            info: 'bg-gray-50 border-gray-200 text-gray-800'
          };
          
          return (
            <div key={index} className={`p-3 rounded-lg border ${colorMap[actionType]}`}>
              <div className="flex items-start space-x-2">
                <span className="text-lg">{iconMap[actionType]}</span>
                <div className="flex-1">
                  <div className="text-xs font-medium opacity-75 mb-1">
                    {new Date(timestamp).toLocaleTimeString()}
                  </div>
                  <div className="text-sm">{content.trim()}</div>
                </div>
              </div>
            </div>
          );
        } else {
          return (
            <div key={index} className="p-2 bg-gray-50 rounded text-sm text-gray-700">
              {line}
            </div>
          );
        }
      })}
    </div>
  );
};

function App() {
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [taskStatus, setTaskStatus] = useState<TaskStatus | null>(null);
  const [executionResult, setExecutionResult] = useState<ExecutionResult | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [pollingInterval, setPollingInterval] = useState<number | null>(null);

  // Cleanup polling on unmount
  useEffect(() => {
    return () => {
      if (pollingInterval) {
        clearInterval(pollingInterval);
      }
    };
  }, [pollingInterval]);

  // Poll task status
  useEffect(() => {
    let interval: number;
    
    if (currentTaskId && isExecuting) {
      interval = setInterval(async () => {
        try {
          const response = await fetch(`${API_BASE_URL}/task-status/${currentTaskId}`);
          if (response.ok) {
            const status = await response.json();
            setTaskStatus(status);
            
            if (status.status === 'completed' || status.status === 'failed') {
              setIsExecuting(false);
              
              if (status.status === 'completed') {
                const resultsResponse = await fetch(`${API_BASE_URL}/task-results/${currentTaskId}`);
                if (resultsResponse.ok) {
                  const results = await resultsResponse.json();
                  setExecutionResult(results);
                }
              }
            }
          }
        } catch (error) {
          console.error('Error polling task status:', error);
          setIsExecuting(false);
        }
      }, 2000);
    }
    
    return () => clearInterval(interval);
  }, [currentTaskId, isExecuting]);

  const executeTest = async (testConfig: TestConfig) => {
    console.log('executeTest called with:', testConfig); // Debug log
    try {
      setIsExecuting(true);
      setTaskStatus(null);
      setExecutionResult(null);
      setAnalysisResult(null);
      
      console.log('Starting test execution with config:', testConfig);
      
      const response = await fetch(`${API_BASE_URL}/execute-test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testConfig),
      });

      console.log('API response status:', response.status); // Debug log

      if (response.ok) {
        const data = await response.json();
        console.log('API response data:', data); // Debug log
        setCurrentTaskId(data.task_id);
        setTaskStatus({ 
          task_id: data.task_id, 
          status: data.status,
          progress: 'Task queued for execution'
        });

        // Start polling for status updates
        const taskId = data.task_id;
        const interval = setInterval(async () => {
          try {
            const statusResponse = await fetch(`${API_BASE_URL}/task-status/${taskId}`);
            if (statusResponse.ok) {
              const status = await statusResponse.json();
              console.log('Task status update:', status);
              setTaskStatus(status);

              if (status.status === 'completed' || status.status === 'failed') {
                clearInterval(interval);
                setPollingInterval(null);
                setIsExecuting(false);

                if (status.status === 'completed') {
                  // Fetch execution results
                  const resultsResponse = await fetch(`${API_BASE_URL}/task-results/${taskId}`);
                  if (resultsResponse.ok) {
                    const executionResults = await resultsResponse.json();
                    console.log('Execution results:', executionResults);
                    setExecutionResult(executionResults);
                  }
                }
              }
            }
          } catch (error) {
            console.error('Error polling task status:', error);
          }
        }, 2000); // Poll every 2 seconds

        setPollingInterval(interval);
      } else {
        const errorText = await response.text();
        console.error('API error:', response.status, errorText);
        throw new Error(`Failed to start test execution: ${response.status}`);
      }
    } catch (error) {
      console.error('Error executing test:', error);
      setIsExecuting(false);
    }
  };

  const analyzeResults = async () => {
    if (!currentTaskId) return;

    try {
      setIsAnalyzing(true);
      const response = await fetch(`${API_BASE_URL}/analyze-results/${currentTaskId}`, {
        method: 'POST',
      });

      if (response.ok) {
        const analysis = await response.json();
        setAnalysisResult(analysis);
      } else {
        throw new Error('Failed to analyze results');
      }
    } catch (error) {
      console.error('Error analyzing results:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const fetchAgentThoughts = async (taskId: string) => {
    // This function triggers a refresh in the AgentThoughtsDisplay component
    // The actual fetching is handled by the component itself
    console.log(`Refreshing agent thoughts for task: ${taskId}`);
  };

  return (
    <div className="min-h-screen flex flex-col bg-primary-50">
      <Toaster position="top-right" />
      <Header />
      
      <main className="flex-grow flex-shrink-0 pb-16">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-primary-900 mb-2">AI Automated Web Testing</h1>
            <p className="text-lg text-primary-600 max-w-3xl mx-auto">
              Create and execute automated web testing scenarios powered by AI.
            </p>
          </div>
          
          <TestConfigForm 
            onExecuteTest={executeTest}
            isExecuting={isExecuting}
          />

          {/* Task Status */}
          {taskStatus && (
            <div className="max-w-7xl mx-auto mt-8 px-4 sm:px-6 lg:px-8">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-primary-200">
                <h3 className="text-lg font-semibold text-primary-900 mb-4">Execution Status</h3>
                <div className="space-y-2">
                  <p><span className="font-medium">Task ID:</span> {taskStatus.task_id}</p>
                  <p><span className="font-medium">Status:</span> 
                    <span className={`ml-2 px-2 py-1 rounded-full text-xs ${
                      taskStatus.status === 'completed' ? 'bg-green-100 text-green-800' :
                      taskStatus.status === 'failed' ? 'bg-red-100 text-red-800' :
                      taskStatus.status === 'running' ? 'bg-blue-100 text-blue-800' :
                      'bg-yellow-100 text-yellow-800'
                    }`}>
                      {taskStatus.status}
                    </span>
                  </p>
                  {taskStatus.progress && <p><span className="font-medium">Progress:</span> {taskStatus.progress}</p>}
                  {taskStatus.error && <p className="text-red-600"><span className="font-medium">Error:</span> {taskStatus.error}</p>}
                </div>
              </div>
            </div>
          )}

          {/* Execution Results */}
          {executionResult && (
            <div className="max-w-7xl mx-auto mt-8 px-4 sm:px-6 lg:px-8">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-primary-200">
                <div className="flex justify-between items-center mb-6">
                  <h3 className="text-lg font-semibold text-primary-900">📊 Execution Results</h3>
                  <button
                    onClick={analyzeResults}
                    disabled={isAnalyzing}
                    className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50 transition-colors"
                  >
                    {isAnalyzing ? '🔄 Analyzing...' : '🔍 Analyze Results'}
                  </button>
                </div>
                
                {/* Agent Thoughts & Reasoning - PROMINENT DISPLAY */}
                {executionResult.agent_thoughts_file && (
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-3">🧠 Agent Thoughts & Reasoning</h4>
                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-xl border-2 border-blue-200 shadow-sm">
                      <div className="flex items-center justify-between mb-4">
                        <div className="flex items-center space-x-2">
                          <span className="text-blue-600 text-lg">🤖</span>
                          <span className="text-sm font-medium text-blue-800">
                            AI Agent's Internal Reasoning Process
                          </span>
                        </div>
                        <button
                          onClick={() => fetchAgentThoughts(executionResult.task_id)}
                          className="text-xs bg-blue-100 hover:bg-blue-200 text-blue-700 px-3 py-1 rounded-full transition-colors"
                        >
                          Refresh
                        </button>
                      </div>
                      <AgentThoughtsDisplay taskId={executionResult.task_id} />
                    </div>
                  </div>
                )}

                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-primary-600 mb-1">
                      {executionResult.success ? '✅' : '❌'}
                    </div>
                    <div className="text-sm text-gray-600">Success</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-blue-600 mb-1">
                      {executionResult.execution_steps?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Steps</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-purple-600 mb-1">
                      {executionResult.screenshot_urls?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">Screenshots</div>
                  </div>
                  <div className="bg-gray-50 p-4 rounded-lg text-center">
                    <div className="text-2xl font-bold text-indigo-600 mb-1">
                      {executionResult.full_conversation?.length || 0}
                    </div>
                    <div className="text-sm text-gray-600">AI Messages</div>
                  </div>
                </div>

                {/* Screenshots Gallery */}
                {executionResult.screenshot_urls && executionResult.screenshot_urls.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-3">📸 Screenshots Captured</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {executionResult.screenshot_urls.map((screenshotUrl, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg overflow-hidden shadow-sm">
                          <img
                            src={`${API_BASE_URL}${screenshotUrl}`}
                            alt={`Screenshot ${index + 1}`}
                            className="w-full h-48 object-cover hover:scale-105 transition-transform cursor-pointer"
                            onClick={() => window.open(`${API_BASE_URL}${screenshotUrl}`, '_blank')}
                            onError={(e) => {
                              console.error('Failed to load screenshot:', screenshotUrl);
                              e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><text y="50" font-size="12">Screenshot unavailable</text></svg>';
                            }}
                          />
                          <div className="p-3 bg-gray-50">
                            <div className="text-sm font-medium text-gray-700">Step {index + 1}</div>
                            <div className="text-xs text-gray-500">Click to view full size</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Execution Steps */}
                {executionResult.execution_steps && executionResult.execution_steps.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-3">🔄 Execution Steps</h4>
                    <div className="space-y-3 max-h-96 overflow-y-auto">
                      {executionResult.execution_steps.map((step, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-sm font-semibold text-primary-700">Step {step.step_number}</span>
                            <span className="text-xs text-gray-500">
                              {new Date(step.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="space-y-2">
                            <div>
                              <span className="text-xs font-medium text-gray-600 block mb-1">Action:</span>
                              <div className="text-sm text-gray-800 bg-white p-2 rounded border max-h-20 overflow-y-auto">
                                {step.action}
                              </div>
                            </div>
                            <div>
                              <span className="text-xs font-medium text-gray-600 block mb-1">Result:</span>
                              <div className="text-sm text-gray-800 bg-white p-2 rounded border max-h-20 overflow-y-auto">
                                {step.result}
                              </div>
                            </div>
                            {step.screenshot_url && (
                              <div className="mt-2">
                                <span className="text-xs font-medium text-gray-600 block mb-1">Screenshot:</span>
                                <img
                                  src={`${API_BASE_URL}${step.screenshot_url}`}
                                  alt={`Step ${step.step_number} screenshot`}
                                  className="max-w-xs h-24 object-cover border rounded cursor-pointer hover:shadow-md transition-shadow"
                                  onClick={() => window.open(`${API_BASE_URL}${step.screenshot_url}`, '_blank')}
                                  onError={(e) => {
                                    e.currentTarget.style.display = 'none';
                                  }}
                                />
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Conversation */}
                {executionResult.full_conversation && executionResult.full_conversation.length > 0 && (
                  <div className="mb-6">
                    <h4 className="text-md font-semibold text-gray-900 mb-3">💬 AI Conversation</h4>
                    <div className="bg-gray-50 p-4 rounded-lg max-h-64 overflow-y-auto">
                      {executionResult.full_conversation.map((conv, index) => (
                        <div key={index} className="mb-2 p-2 bg-white rounded border">
                          <div className="flex justify-between items-start">
                            <span className="text-xs font-medium text-blue-600">Step {conv.step}</span>
                            <span className="text-xs text-gray-500">
                              {new Date(conv.timestamp).toLocaleTimeString()}
                            </span>
                          </div>
                          <div className="text-sm text-gray-800 mt-1">{conv.model_output}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Log File Links */}
                {(executionResult.log_file || executionResult.detailed_log_file || executionResult.stdout_log_file || executionResult.agent_thoughts_file) && (
                  <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <h4 className="text-sm font-medium text-blue-800 mb-2">📄 Generated Log Files</h4>
                    <div className="space-y-1 text-xs text-blue-700">
                      {executionResult.agent_thoughts_file && (
                        <div className="font-semibold">🤖 Agent thoughts & actions: {executionResult.agent_thoughts_file}</div>
                      )}
                      {executionResult.log_file && (
                        <div>• Execution results: {executionResult.log_file}</div>
                      )}
                      {executionResult.detailed_log_file && (
                        <div>• Detailed agent log: {executionResult.detailed_log_file}</div>
                      )}
                      {executionResult.stdout_log_file && (
                        <div>• Agent stdout: {executionResult.stdout_log_file}</div>
                      )}
                      {executionResult.stderr_log_file && (
                        <div>• Agent stderr: {executionResult.stderr_log_file}</div>
                      )}
                    </div>
                  </div>
                )}

                {/* Error Display */}
                {executionResult.error && (
                  <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <h4 className="text-sm font-medium text-red-800 mb-2">❌ Error Details</h4>
                    <p className="text-sm text-red-700">{executionResult.error}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Analysis Results */}
          {analysisResult && (
            <div className="max-w-7xl mx-auto mt-8 px-4 sm:px-6 lg:px-8">
              <div className="bg-white rounded-xl shadow-sm p-6 border border-primary-200">
                <h3 className="text-lg font-semibold text-primary-900 mb-4">AI Analysis Report</h3>
                <div className="bg-gray-50 p-4 rounded-lg max-h-96 overflow-y-auto">
                  <pre className="whitespace-pre-wrap text-sm">{analysisResult.analysis_content}</pre>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
      
      <Footer />
    </div>
  );
}

export default App