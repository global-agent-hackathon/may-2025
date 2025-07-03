import React from 'react';
import { WorkflowStep, WorkflowStatus } from '../../types/index';
import { CheckCircle, Clock, Loader, AlertCircle } from 'lucide-react';

interface WorkflowProgressProps {
  steps: WorkflowStep[];
}

const WorkflowProgress: React.FC<WorkflowProgressProps> = ({ steps }) => {
  const getStatusIcon = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.Completed:
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case WorkflowStatus.InProgress:
        return <Loader className="h-5 w-5 text-primary-500 animate-spin" />;
      case WorkflowStatus.Pending:
        return <Clock className="h-5 w-5 text-gray-400" />;
      case WorkflowStatus.Failed:
        return <AlertCircle className="h-5 w-5 text-red-500" />;
      default:
        return <Clock className="h-5 w-5 text-gray-400" />;
    }
  };

  const getStatusClass = (status: WorkflowStatus) => {
    switch (status) {
      case WorkflowStatus.Completed:
        return 'bg-green-50 border-green-100 text-green-700';
      case WorkflowStatus.InProgress:
        return 'bg-primary-50 border-primary-100 text-primary-700';
      case WorkflowStatus.Pending:
        return 'bg-gray-50 border-gray-100 text-gray-600';
      case WorkflowStatus.Failed:
        return 'bg-red-50 border-red-100 text-red-700';
      default:
        return 'bg-gray-50 border-gray-100 text-gray-600';
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="relative mt-2">
        {/* Horizontal lines */}
        <div className="absolute left-0 right-0 top-6 h-0.5 flex items-center">
          {steps.map((step, idx) => (
            <React.Fragment key={`line-${idx}`}>
              {idx > 0 && (
                <div 
                  className={`h-0.5 flex-1 ${
                    steps[idx-1].status === WorkflowStatus.Completed ? 'bg-primary-500' : 'bg-gray-100'
                  }`}
                />
              )}
              <div className="w-12 h-12 flex-shrink-0" />
            </React.Fragment>
          ))}
        </div>
        
        {/* Step circles */}
        <div className="flex justify-between relative z-10">
          {steps.map((step) => (
            <div key={step.id} className="flex flex-col items-center">
              <div 
                className={`flex items-center justify-center w-12 h-12 rounded-full border-2 shadow-soft bg-white ${getStatusClass(step.status)}`}
              >
                {getStatusIcon(step.status)}
              </div>
              <div className="mt-3 text-sm font-medium text-center">
                {step.name}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default WorkflowProgress;