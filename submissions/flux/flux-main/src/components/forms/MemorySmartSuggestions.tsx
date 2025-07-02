import React, { useState, useEffect } from 'react';
import { Brain, Lightbulb, TrendingUp, Target, Zap, Clock, CheckCircle, RefreshCw, Sparkles } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useUser } from '@clerk/clerk-react';
import { extractContextualKeywords, searchMemoriesWithContext, getEnhancedFormContext } from '@/lib/memory';

interface MemorySmartSuggestionsProps {
  prompt: string;
  onSuggestionApply: (suggestion: string) => void;
  className?: string;
}

interface SmartSuggestion {
  id: string;
  type: 'enhancement' | 'field' | 'structure' | 'optimization' | 'pattern';
  title: string;
  description: string;
  confidence: number;
  source: 'flux' | 'memory' | 'pattern' | 'ai';
  action?: string;
  enhancedPrompt?: string;
}

export function MemorySmartSuggestions({ prompt, onSuggestionApply, className }: MemorySmartSuggestionsProps) {
  const { user } = useUser();
  const [suggestions, setSuggestions] = useState<SmartSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [memoryStats, setMemoryStats] = useState<any>(null);
  const [memoryActivated, setMemoryActivated] = useState(false);
  const [enhancedPrompt, setEnhancedPrompt] = useState<string>('');

  const enhancePromptWithFlux = async () => {
    if (!user?.id || !prompt.trim()) return;
    
    setLoading(true);
    try {
      // Call the flux agent to enhance the prompt
      const response = await fetch('/api/ai/enhance-prompt', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt.trim(),
          userId: user.id
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to enhance prompt');
      }

      const data = await response.json();
      const enhanced = data.enhancedPrompt || '';
      
      if (enhanced && enhanced !== prompt) {
        setEnhancedPrompt(enhanced);
        setSuggestions([{
          id: 'flux-enhancement',
          type: 'enhancement',
          title: 'Enhanced with Flux',
          description: 'AI-powered prompt enhancement based on successful form patterns',
          confidence: 95,
          source: 'flux',
          enhancedPrompt: enhanced,
          action: enhanced
        }]);
      } else {
        // If no enhancement, provide contextual suggestions
        await generateContextualSuggestions();
      }
    } catch (error) {
      console.warn("Failed to enhance prompt with Flux:", error);
      // Fallback to contextual suggestions
      await generateContextualSuggestions();
    } finally {
      setLoading(false);
    }
  };

  const generateContextualSuggestions = async () => {
    if (!user?.id || !prompt.trim()) return;
    
    try {
      const keywords = extractContextualKeywords(prompt);
      console.log("🧠 Memory Analysis - Keywords:", keywords);

      // Get memory-based insights
      const memoryContext = await getEnhancedFormContext(user.id, prompt);
      const similarForms = await searchMemoriesWithContext(user.id, prompt, 5, "form_interaction");

      const newSuggestions: SmartSuggestion[] = [];

      // Analyze similar successful forms
      if (similarForms?.memories?.length) {
        const successfulForms = similarForms.memories.filter(m => 
          m.metadata?.ai_form_analytics?.success_score >= 7
        );

        if (successfulForms.length > 0) {
          // Field type suggestions based on memory
          const fieldTypes = successfulForms.flatMap(m => 
            m.metadata?.ai_form_analytics?.generated_field_types || []
          );
          const popularTypes = [...new Set(fieldTypes)].slice(0, 3);

          if (popularTypes.length > 0) {
            newSuggestions.push({
              id: 'memory-fields',
              type: 'field',
              title: 'Recommended Field Types',
              description: `Based on ${successfulForms.length} similar successful forms`,
              confidence: 85,
              source: 'memory',
              action: `Include these field types: ${popularTypes.join(', ')}`
            });
          }

          // Structure suggestions
          const avgFields = successfulForms.reduce((acc, m) => 
            acc + (m.metadata?.ai_form_analytics?.generated_field_count || 0), 0
          ) / successfulForms.length;

          newSuggestions.push({
            id: 'memory-structure',
            type: 'structure',
            title: 'Optimal Form Length',
            description: `Similar forms average ${Math.round(avgFields)} fields`,
            confidence: 80,
            source: 'memory',
            action: `Aim for ${Math.round(avgFields)} fields for best results`
          });
        }

        setMemoryStats({
          totalSimilar: similarForms.memories.length,
          successfulForms: successfulForms.length,
          avgRelevance: 85
        });
      }

      // Keyword-based pattern suggestions
      if (keywords.includes('feedback') || keywords.includes('survey')) {
        newSuggestions.push({
          id: 'pattern-feedback',
          type: 'pattern',
          title: 'Feedback Form Best Practices',
          description: 'Rating scales increase completion rates',
          confidence: 90,
          source: 'pattern',
          action: 'Add rating scale and open-ended comment fields'
        });
      }

      if (keywords.includes('application') || keywords.includes('job')) {
        newSuggestions.push({
          id: 'pattern-application',
          type: 'pattern',
          title: 'Application Form Optimization',
          description: 'Successful applications include structured experience fields',
          confidence: 88,
          source: 'pattern',
          action: 'Include file upload for documents and experience timeline'
        });
      }

      if (keywords.includes('registration') || keywords.includes('event')) {
        newSuggestions.push({
          id: 'pattern-registration',
          type: 'pattern',
          title: 'Registration Form Essentials',
          description: 'Event forms with clear date/time fields perform better',
          confidence: 85,
          source: 'pattern',
          action: 'Add date/time fields and contact information collection'
        });
      }

      // AI-powered optimization suggestions
      if (prompt.length < 50) {
        newSuggestions.push({
          id: 'ai-prompt-length',
          type: 'optimization',
          title: 'Prompt Optimization',
          description: 'Longer prompts (50+ chars) generally work better',
          confidence: 75,
          source: 'ai',
          action: 'Add more details about your form requirements'
        });
      }

      setSuggestions(newSuggestions);
    } catch (error) {
      console.warn("Failed to generate contextual suggestions:", error);
    }
  };

  const regenerateSuggestions = async () => {
    setSuggestions([]);
    setEnhancedPrompt('');
    await enhancePromptWithFlux();
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'enhancement': return <Sparkles className="h-4 w-4" />;
      case 'field': return <Target className="h-4 w-4" />;
      case 'structure': return <TrendingUp className="h-4 w-4" />;
      case 'optimization': return <Zap className="h-4 w-4" />;
      case 'pattern': return <CheckCircle className="h-4 w-4" />;
      default: return <Lightbulb className="h-4 w-4" />;
    }
  };

  const getSourceColor = (source: string) => {
    switch (source) {
      case 'flux': return 'bg-gradient-to-r from-purple-100 to-blue-100 text-purple-800';
      case 'memory': return 'bg-purple-100 text-purple-800';
      case 'pattern': return 'bg-blue-100 text-blue-800';
      case 'ai': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (!prompt || prompt.length < 10) {
    return (
      <Card className={className}>
        <CardContent className="p-6 text-center">
          <Brain className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
          <p className="text-sm text-muted-foreground">
            Start typing your form description to see smart suggestions
          </p>
        </CardContent>
      </Card>
    );
  }

  if (!memoryActivated) {
    return (
      <Card className={className}>
        <CardContent className="p-6 text-center">
          <Sparkles className="h-8 w-8 mx-auto text-purple-600 mb-4" />
          <p className="text-sm text-muted-foreground mb-4">
            Enhance your prompt with AI-powered suggestions based on successful form patterns
          </p>
          <Button
            onClick={() => {
              setMemoryActivated(true);
              enhancePromptWithFlux();
            }}
            variant="outline"
            size="sm"
            className="border-purple-200 text-purple-700 hover:bg-purple-50"
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Enhance with Flux
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-lg">
          <div className="flex items-center">
            <Sparkles className="h-5 w-5 mr-2 text-purple-600" />
            Enhance with Flux
            {loading && <div className="ml-2 h-4 w-4 animate-spin rounded-full border-2 border-purple-600 border-t-transparent" />}
          </div>
          <Button
            onClick={regenerateSuggestions}
            variant="ghost"
            size="sm"
            disabled={loading}
            className="h-8 w-8 p-0"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </Button>
        </CardTitle>
        <CardDescription>
          {memoryStats ? (
            <span>
              Analyzed {memoryStats.totalSimilar} similar forms • {memoryStats.successfulForms} successful patterns found
            </span>
          ) : (
            "AI analyzing your prompt with memory insights..."
          )}
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-3">
        {suggestions.length > 0 ? (
          suggestions.map((suggestion) => (
            <div key={suggestion.id} className="p-3 border rounded-lg hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1">
                  <div className="p-1 rounded-full bg-gray-100">
                    {getTypeIcon(suggestion.type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-medium text-sm">{suggestion.title}</h4>
                      <Badge variant="outline" className={`text-xs ${getSourceColor(suggestion.source)}`}>
                        {suggestion.source}
                      </Badge>
                      <Badge variant="outline" className="text-xs">
                        {suggestion.confidence}% confidence
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mb-2">
                      {suggestion.description}
                    </p>
                    {suggestion.enhancedPrompt && (
                      <div className="mb-2 p-2 bg-purple-50 rounded text-xs">
                        <p className="font-medium text-purple-800 mb-1">Enhanced Prompt:</p>
                        <p className="text-purple-700">{suggestion.enhancedPrompt}</p>
                      </div>
                    )}
                    {suggestion.action && (
                      <Button
                        size="sm"
                        variant="outline"
                        className="text-xs h-7"
                        onClick={() => onSuggestionApply(suggestion.action!)}
                      >
                        {suggestion.type === 'enhancement' ? 'Use Enhanced Prompt' : 'Apply Suggestion'}
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : loading ? (
          <div className="text-center py-4">
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2 mx-auto"></div>
            </div>
          </div>
        ) : (
          <div className="text-center py-4">
            <Clock className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
            <p className="text-sm text-muted-foreground">
              No specific suggestions found. Try adding more details to your prompt.
            </p>
          </div>
        )}

        {memoryStats && (
          <div className="mt-4 pt-3 border-t">
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <span>Memory Analysis Complete</span>
              <span>Relevance: {Math.round(memoryStats.avgRelevance || 0)}%</span>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
} 