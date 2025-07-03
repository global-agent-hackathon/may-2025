import React, { useState, useEffect } from 'react';
import { PlusCircle, Save } from 'lucide-react';
import toast from 'react-hot-toast';
import ScreenshotInstructionField from './ScreenshotInstructionField';
import JsonPreview from './JsonPreview';
import SavedWorkflows from './SavedWorkflows';
import { TestConfig, ScreenshotInstruction, SavedWorkflow } from '../types/TestConfig';

const initialScreenshotInstruction: ScreenshotInstruction = {
  step_description: '',
  filename: ''
};

const initialTestConfig: TestConfig = {
  target_url: '',
  task_description: '',
  screenshot_instructions: [{ ...initialScreenshotInstruction }]
};

interface TestConfigFormProps {
  onExecuteTest?: (testConfig: TestConfig) => void;
  isExecuting?: boolean;
}

const TestConfigForm: React.FC<TestConfigFormProps> = ({ onExecuteTest, isExecuting = false }) => {
  const [testConfig, setTestConfig] = useState<TestConfig>(initialTestConfig);
  const [workflowName, setWorkflowName] = useState('');
  const [isFormValid, setIsFormValid] = useState(false);
  const [formTouched, setFormTouched] = useState(false);
  const [savedWorkflows, setSavedWorkflows] = useState<SavedWorkflow[]>(() => {
    const saved = localStorage.getItem('savedWorkflows');
    return saved ? JSON.parse(saved) : [];
  });

  useEffect(() => {
    const validateForm = () => {
      const { target_url, task_description, screenshot_instructions } = testConfig;
      
      const basicFieldsValid = target_url.trim() !== '' && task_description.trim() !== '';
      
      // Only validate screenshot instructions that have some content
      // Filter out completely empty ones and only validate the ones with content
      const filledScreenshots = screenshot_instructions.filter(
        instruction => 
          instruction.step_description.trim() !== '' || 
          instruction.filename.trim() !== ''
      );
      
      const screenshotsValid = filledScreenshots.every(
        instruction => 
          instruction.step_description.trim() !== '' && 
          instruction.filename.trim() !== ''
      );
      
      // Debug logging
      console.log('Form validation:', {
        target_url: target_url.trim(),
        task_description: task_description.trim(),
        basicFieldsValid,
        totalScreenshots: screenshot_instructions.length,
        filledScreenshots: filledScreenshots.length,
        screenshotsValid,
        overall: basicFieldsValid && screenshotsValid
      });
      
      return basicFieldsValid && screenshotsValid;
    };
    
    setIsFormValid(validateForm());
  }, [testConfig]);

  const handleBasicFieldChange = (field: keyof Omit<TestConfig, 'screenshot_instructions'>, value: string) => {
    setTestConfig(prev => ({ ...prev, [field]: value }));
    if (!formTouched) setFormTouched(true);
  };

  const handleScreenshotChange = (index: number, field: keyof ScreenshotInstruction, value: string) => {
    setTestConfig(prev => {
      const updatedInstructions = [...prev.screenshot_instructions];
      updatedInstructions[index] = { ...updatedInstructions[index], [field]: value };
      return { ...prev, screenshot_instructions: updatedInstructions };
    });
    if (!formTouched) setFormTouched(true);
  };

  const addScreenshotInstruction = () => {
    setTestConfig(prev => ({
      ...prev,
      screenshot_instructions: [...prev.screenshot_instructions, { ...initialScreenshotInstruction }]
    }));
  };

  const removeScreenshotInstruction = (index: number) => {
    setTestConfig(prev => {
      const updatedInstructions = [...prev.screenshot_instructions];
      updatedInstructions.splice(index, 1);
      return { ...prev, screenshot_instructions: updatedInstructions };
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isFormValid && onExecuteTest) {
      onExecuteTest(testConfig);
      toast.success('Test execution started!');
    }
  };

  const handleSave = () => {
    if (!workflowName.trim()) {
      toast.error('Please enter a workflow name');
      return;
    }

    const newWorkflow: SavedWorkflow = {
      id: crypto.randomUUID(),
      name: workflowName,
      config: {
        ...testConfig,
        created_at: new Date().toISOString()
      },
      created_at: new Date().toISOString()
    };

    const updatedWorkflows = [...savedWorkflows, newWorkflow];
    setSavedWorkflows(updatedWorkflows);
    localStorage.setItem('savedWorkflows', JSON.stringify(updatedWorkflows));
    setWorkflowName('');
    toast.success('Workflow saved successfully!');
  };

  const loadWorkflow = (workflow: SavedWorkflow) => {
    setTestConfig(workflow.config);
    setWorkflowName(workflow.name);
    toast.success('Workflow loaded successfully!');
  };

  const deleteWorkflow = (id: string) => {
    const updatedWorkflows = savedWorkflows.filter(w => w.id !== id);
    setSavedWorkflows(updatedWorkflows);
    localStorage.setItem('savedWorkflows', JSON.stringify(updatedWorkflows));
    toast.success('Workflow deleted successfully!');
  };

  const handleReset = () => {
    setTestConfig(initialTestConfig);
    setWorkflowName('');
    setFormTouched(false);
  };

  return (
    <div className="w-full max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-xl shadow-sm p-6 border border-primary-200">
          <h2 className="text-xl font-semibold text-primary-900 mb-6">Test Configuration</h2>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="workflow-name" className="block text-sm font-medium text-gray-700 mb-1">
                Workflow Name
              </label>
              <input
                type="text"
                id="workflow-name"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                className="w-full px-3 py-2 border border-primary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                placeholder="My Test Workflow"
              />
            </div>

            <div>
              <label htmlFor="target-url" className="block text-sm font-medium text-gray-700 mb-1">
                Target URL
              </label>
              <input
                type="url"
                id="target-url"
                value={testConfig.target_url}
                onChange={(e) => handleBasicFieldChange('target_url', e.target.value)}
                className="w-full px-3 py-2 border border-primary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                placeholder="https://example.com (try: httpbin.org, duckduckgo.com, or github.com)"
                required
              />
            </div>
            
            <div>
              <label htmlFor="task-description" className="block text-sm font-medium text-gray-700 mb-1">
                Task Description
              </label>
              <textarea
                id="task-description"
                value={testConfig.task_description}
                onChange={(e) => handleBasicFieldChange('task_description', e.target.value)}
                className="w-full px-3 py-2 border border-primary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-colors"
                rows={5}
                placeholder="Describe the testing task in steps..."
                required
              />
            </div>
            
            <div>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-sm font-medium text-gray-700">Screenshot Instructions</h3>
                <button
                  type="button"
                  onClick={addScreenshotInstruction}
                  className="inline-flex items-center text-sm font-medium text-primary-600 hover:text-primary-800 transition-colors"
                >
                  <PlusCircle size={16} className="mr-1" />
                  Add Screenshot
                </button>
              </div>
              
              {testConfig.screenshot_instructions.map((instruction, index) => (
                <ScreenshotInstructionField
                  key={index}
                  instruction={instruction}
                  index={index}
                  onChange={handleScreenshotChange}
                  onRemove={removeScreenshotInstruction}
                />
              ))}
              
              {testConfig.screenshot_instructions.length === 0 && (
                <p className="text-sm text-gray-500 italic">
                  No screenshot instructions added. Click "Add Screenshot" to add one.
                </p>
              )}
            </div>
            
            <div className="flex justify-end space-x-3 pt-4">
              {/* Debug info */}
              <div className="text-xs text-gray-500 mr-auto">
                Form valid: {isFormValid ? '✅' : '❌'} | Executing: {isExecuting ? '⏳' : '⭕'}
              </div>
              
              <button
                type="button"
                onClick={handleReset}
                className="px-4 py-2 border border-primary-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-primary-50 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-colors"
              >
                Reset
              </button>
              <button
                type="button"
                onClick={handleSave}
                disabled={!isFormValid || !workflowName}
                className={`px-4 py-2 rounded-md text-sm font-medium text-white ${
                  isFormValid && workflowName
                    ? 'bg-primary-600 hover:bg-primary-700 focus:ring-primary-500'
                    : 'bg-primary-400 cursor-not-allowed'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors inline-flex items-center`}
              >
                <Save size={16} className="mr-1" />
                Save Workflow
              </button>
              <button
                type="submit"
                disabled={!isFormValid || isExecuting}
                className={`px-4 py-2 rounded-md text-sm font-medium text-white ${
                  isFormValid && !isExecuting
                    ? 'bg-green-600 hover:bg-green-700 focus:ring-green-500'
                    : 'bg-green-400 cursor-not-allowed'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors`}
              >
                {isExecuting ? 'Executing...' : 'Execute Test'}
              </button>
            </div>
          </form>
        </div>
        
        <div className="space-y-8">
          <JsonPreview testConfig={testConfig} />
          <div className="bg-white rounded-xl shadow-sm p-6 border border-primary-200">
            <h2 className="text-xl font-semibold text-primary-900 mb-6">Saved Workflows</h2>
            <SavedWorkflows
              workflows={savedWorkflows}
              onLoad={loadWorkflow}
              onDelete={deleteWorkflow}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestConfigForm;