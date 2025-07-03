import React from 'react';
import { SavedWorkflow } from '../types/TestConfig';
import { Trash2, FileCode } from 'lucide-react';

interface SavedWorkflowsProps {
  workflows: SavedWorkflow[];
  onLoad: (workflow: SavedWorkflow) => void;
  onDelete: (id: string) => void;
}

const SavedWorkflows: React.FC<SavedWorkflowsProps> = ({ workflows, onLoad, onDelete }) => {
  if (workflows.length === 0) {
    return (
      <div className="text-center p-8 bg-primary-50 rounded-lg border-2 border-dashed border-primary-200">
        <FileCode className="mx-auto h-12 w-12 text-primary-400" />
        <p className="mt-4 text-sm text-primary-600">No saved workflows yet. Create and save a workflow to see it here.</p>
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {workflows.map((workflow) => (
        <div
          key={workflow.id}
          className="bg-white p-4 rounded-lg border border-primary-200 shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex justify-between items-start mb-2">
            <h3 className="font-medium text-primary-900">{workflow.name}</h3>
            <div className="flex space-x-2">
              <button
                onClick={() => onLoad(workflow)}
                className="text-primary-600 hover:text-primary-800 p-1 rounded transition-colors"
                title="Load workflow"
              >
                <FileCode size={18} />
              </button>
              <button
                onClick={() => onDelete(workflow.id)}
                className="text-red-500 hover:text-red-700 p-1 rounded transition-colors"
                title="Delete workflow"
              >
                <Trash2 size={18} />
              </button>
            </div>
          </div>
          <p className="text-sm text-gray-500 mb-2">
            Created: {new Date(workflow.created_at).toLocaleDateString()}
          </p>
          <p className="text-sm text-gray-600 truncate">{workflow.config.target_url}</p>
        </div>
      ))}
    </div>
  );
};

export default SavedWorkflows;