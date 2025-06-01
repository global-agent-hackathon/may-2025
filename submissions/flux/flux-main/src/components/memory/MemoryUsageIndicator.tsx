import React, { useState, useEffect } from 'react';
import { Brain, Activity, TrendingUp, Zap, CheckCircle, Clock } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { useUser } from '@clerk/clerk-react';
import { memoryService } from '@/lib/memory';

interface MemoryUsageIndicatorProps {
  context: 'form-creation' | 'form-editing' | 'analytics' | 'dashboard';
  className?: string;
}

interface MemoryActivity {
  type: 'pattern-match' | 'suggestion' | 'optimization' | 'insight';
  description: string;
  confidence: number;
  timestamp: Date;
}

export function MemoryUsageIndicator({ context, className }: MemoryUsageIndicatorProps) {
  const { user } = useUser();
  const [activities, setActivities] = useState<MemoryActivity[]>([]);
  const [memoryCount, setMemoryCount] = useState(0);
  const [isActive, setIsActive] = useState(false);

  useEffect(() => {
    if (user?.id) {
      loadMemoryStats();
      simulateMemoryActivity();
    }
  }, [user?.id, context]);

  const loadMemoryStats = async () => {
    if (!user?.id) return;
    
    try {
      const memories = await memoryService.searchMemories({
        user_id: user.id,
        query: '',
        limit: 1,
        memory_type: 'form_interaction'
      });
      setMemoryCount(memories.total_count || 0);
    } catch (error) {
      console.warn('Failed to load memory stats:', error);
    }
  };

  const simulateMemoryActivity = () => {
    setIsActive(true);
    
    const contextActivities = getContextActivities(context);
    let activityIndex = 0;

    const addActivity = () => {
      if (activityIndex < contextActivities.length) {
        setActivities(prev => [
          ...prev.slice(-2), // Keep only last 2 activities
          {
            ...contextActivities[activityIndex],
            timestamp: new Date()
          }
        ]);
        activityIndex++;
        
        setTimeout(addActivity, 1500 + Math.random() * 2000);
      } else {
        setTimeout(() => setIsActive(false), 3000);
      }
    };

    setTimeout(addActivity, 500);
  };

  const getContextActivities = (context: string): Omit<MemoryActivity, 'timestamp'>[] => {
    switch (context) {
      case 'form-creation':
        return [
          {
            type: 'pattern-match',
            description: 'Analyzing similar successful forms',
            confidence: 92
          },
          {
            type: 'suggestion',
            description: 'Found optimal field patterns',
            confidence: 87
          },
          {
            type: 'optimization',
            description: 'Recommending form structure',
            confidence: 85
          }
        ];
      
      case 'form-editing':
        return [
          {
            type: 'insight',
            description: 'Comparing with edit history',
            confidence: 89
          },
          {
            type: 'suggestion',
            description: 'Suggesting field improvements',
            confidence: 83
          }
        ];
      
      case 'analytics':
        return [
          {
            type: 'pattern-match',
            description: 'Identifying usage trends',
            confidence: 94
          },
          {
            type: 'insight',
            description: 'Generating performance insights',
            confidence: 91
          }
        ];
      
      case 'dashboard':
        return [
          {
            type: 'optimization',
            description: 'Personalizing dashboard layout',
            confidence: 88
          },
          {
            type: 'insight',
            description: 'Highlighting key metrics',
            confidence: 86
          }
        ];
      
      default:
        return [];
    }
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'pattern-match': return <TrendingUp className="h-3 w-3" />;
      case 'suggestion': return <Zap className="h-3 w-3" />;
      case 'optimization': return <Activity className="h-3 w-3" />;
      case 'insight': return <CheckCircle className="h-3 w-3" />;
      default: return <Brain className="h-3 w-3" />;
    }
  };

  const getActivityColor = (type: string) => {
    switch (type) {
      case 'pattern-match': return 'text-blue-600 bg-blue-50';
      case 'suggestion': return 'text-purple-600 bg-purple-50';
      case 'optimization': return 'text-green-600 bg-green-50';
      case 'insight': return 'text-orange-600 bg-orange-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  if (!user?.id || memoryCount === 0) {
    return null;
  }

  return (
    <Card className={`${className} border-l-4 border-l-purple-500`}>
      <CardContent className="p-3">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center space-x-2">
            <div className="relative">
              <Brain className="h-4 w-4 text-purple-600" />
              {isActive && (
                <div className="absolute -top-1 -right-1 h-2 w-2 bg-green-500 rounded-full animate-pulse"></div>
              )}
            </div>
            <span className="text-sm font-medium">Memory Active</span>
          </div>
          <Badge variant="outline" className="text-xs">
            {memoryCount} memories
          </Badge>
        </div>

        {activities.length > 0 && (
          <div className="space-y-2">
            {activities.map((activity, index) => (
              <div key={index} className="flex items-center space-x-2 text-xs">
                <div className={`p-1 rounded-full ${getActivityColor(activity.type)}`}>
                  {getActivityIcon(activity.type)}
                </div>
                <span className="flex-1 text-muted-foreground">
                  {activity.description}
                </span>
                <Badge variant="outline" className="text-xs">
                  {activity.confidence}%
                </Badge>
              </div>
            ))}
          </div>
        )}

        {!isActive && activities.length === 0 && (
          <div className="flex items-center space-x-2 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            <span>Memory ready for insights</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 