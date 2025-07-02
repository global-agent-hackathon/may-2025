"use client"

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Badge } from '@/components/ui/badge'
import { Sparkles, Loader2, BarChart3, PieChart, TrendingUp, Activity, Plus } from 'lucide-react'
import { ChartDisplay } from './ChartDisplay'
import { toast } from '@/hooks/use-toast'

interface ChartSuggestion {
  title: string
  type: 'bar' | 'pie' | 'line' | 'area' | 'doughnut'
  config: any
  description: string
  confidence: number
}

interface AIChartCreatorProps {
  isOpen: boolean
  onOpenChange: (open: boolean) => void
  formId: string
  onChartCreated: () => void
}

export function AIChartCreator({ isOpen, onOpenChange, formId, onChartCreated }: AIChartCreatorProps) {
  const [prompt, setPrompt] = useState('')
  const [isGenerating, setIsGenerating] = useState(false)
  const [suggestions, setSuggestions] = useState<ChartSuggestion[]>([])
  const [isCreating, setIsCreating] = useState(false)

  // Reset state when dialog closes
  useEffect(() => {
    if (!isOpen) {
      setPrompt('')
      setSuggestions([])
      setIsGenerating(false)
      setIsCreating(false)
    }
  }, [isOpen])

  const generateSuggestions = async () => {
    setIsGenerating(true)
    try {
      // Call the Next.js API route instead of calling flux-agent directly
      const response = await fetch(`/api/forms/${formId}/generate-chart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          prompt: prompt || "Generate basic chart suggestions for this form data"
        }),
      })

      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.error || 'Failed to generate chart suggestions')
      }

      const data = await response.json()
      setSuggestions(data.suggestions || [])
      
      if (!data.suggestions || data.suggestions.length === 0) {
        toast({
          title: "No suggestions available",
          description: "Try adding more form responses or different field types.",
          variant: "destructive"
        })
      } else {
        toast({
          title: "Chart suggestions generated",
          description: `Found ${data.suggestions.length} chart suggestions for your form data.`,
        })
      }
    } catch (error) {
      console.error('Error generating suggestions:', error)
      toast({
        title: "Error generating suggestions",
        description: error instanceof Error ? error.message : "Please try again later.",
        variant: "destructive"
      })
    } finally {
      setIsGenerating(false)
    }
  }

  const createChart = async (suggestion: ChartSuggestion) => {
    setIsCreating(true)
    try {
      const title = suggestion.title
      
      // Call the actual chart creation API
      const response = await fetch(`/api/forms/${formId}/charts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          type: suggestion.type,
          config: suggestion.config
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || 'Failed to create chart')
      }

      const createdChart = await response.json()
      
      // Show success toast
      toast({
        title: "Chart created successfully",
        description: `"${title}" has been added to your analytics.`,
      })

      // Close popup first
      onOpenChange(false)
      
      // Then refresh charts after a short delay
      setTimeout(() => {
        onChartCreated()
      }, 200)
      
    } catch (error) {
      console.error('Error creating chart:', error)
      toast({
        title: "Error creating chart",
        description: error instanceof Error ? error.message : "Please try again later.",
        variant: "destructive"
      })
    } finally {
      setIsCreating(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-purple-600" />
            Create Charts with AI
          </DialogTitle>
        </DialogHeader>

        <div className="space-y-6">
          {/* AI Prompt Section */}
          <div className="space-y-4">
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe what you want to visualize (optional)..."
              className="min-h-[80px]"
            />
            
            <Button 
              onClick={generateSuggestions}
              disabled={isGenerating}
              className="w-full"
              size="lg"
            >
              {isGenerating ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Analyzing form data...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Chart
                </>
              )}
            </Button>
          </div>

          {/* Single Suggestion Display */}
          {suggestions.length > 0 && (
            <div className="space-y-4">
              {(() => {
                const suggestion = suggestions[0] // Just get the first (and only) suggestion
                return (
                  <div className="border rounded-lg overflow-hidden bg-white">
                    {/* Chart Title */}
                    <div className="p-4 border-b bg-gray-50">
                      <h3 className="text-lg font-medium text-gray-900">{suggestion.title}</h3>
                    </div>
                    
                    {/* Chart Preview */}
                    <div className="h-80">
                      <ChartDisplay
                        type={suggestion.type}
                        config={suggestion.config}
                        title={suggestion.title}
                        className="h-full border-none bg-transparent"
                        formId={formId}
                        isPreview={true}
                      />
                    </div>

                    {/* Action Button */}
                    <div className="p-4 border-t bg-gray-50">
                      <Button
                        onClick={() => createChart(suggestion)}
                        disabled={isCreating}
                        className="w-full"
                        size="lg"
                      >
                        {isCreating ? (
                          <>
                            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                            Saving to Dashboard...
                          </>
                        ) : (
                          <>
                            <Plus className="h-4 w-4 mr-2" />
                            Save to Dashboard
                          </>
                        )}
                      </Button>
                    </div>
                  </div>
                )
              })()}
            </div>
          )}

          {/* Empty State */}
          {suggestions.length === 0 && !isGenerating && (
            <div className="text-center py-12 text-gray-500">
              <BarChart3 className="h-12 w-12 mx-auto mb-4 text-gray-300" />
              <p className="text-sm">Generate chart to get started</p>
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  )
} 