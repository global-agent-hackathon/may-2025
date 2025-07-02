import React from 'react';
import type { ConnectionStatus } from '../../types/Company';

interface ConnectionStatusBadgeProps {
  status: ConnectionStatus;
}

const statusMap: Record<ConnectionStatus, { icon: string; text: string; color: string }> = {
  private: { icon: '🔒', text: 'Private', color: 'bg-gray-500' },
  connected: { icon: '🟢', text: 'Connected', color: 'bg-green-500' },
  pending: { icon: '⏳', text: 'Pending', color: 'bg-yellow-500' },
  public: { icon: '👁️', text: 'Public', color: 'bg-blue-500' },
};

const ConnectionStatusBadge: React.FC<ConnectionStatusBadgeProps> = ({ status }) => {
  const { icon, text, color } = statusMap[status];

  return (
    <div className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium text-white ${color}`}>
      <span className="mr-1">{icon}</span>
      {text}
    </div>
  );
};

export default ConnectionStatusBadge; 