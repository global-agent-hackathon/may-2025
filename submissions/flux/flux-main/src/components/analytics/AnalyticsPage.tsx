"use client"

import React, { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { BarChart3, Plus, Sparkles, Trash2, Edit, MoreVertical, RefreshCw } from 'lucide-react'
import { ChartDisplay } from '@/components/charts/ChartDisplay'
import { AIChartCreator } from '@/components/charts/AIChartCreator'
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from '@/components/ui/dropdown-menu'
import { toast } from '@/hooks/use-toast'
import { trackFormInteraction } from "@/lib/memory"
import { useUser } from "@clerk/clerk-react"

interface Chart {
  id: string
  title: string
  type: 'bar' | 'pie' | 'line' | 'area' | 'doughnut'
  config: any
  createdAt: string
  updatedAt: string
}

interface AnalyticsPageProps {
  formId: string
  submissionCount?: number
}

export function AnalyticsPage({ formId, submissionCount = 0 }: AnalyticsPageProps) {
  const { user } = useUser()
  const [charts, setCharts] = useState<Chart[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [showAICreator, setShowAICreator] = useState(false)
  const [isDeleting, setIsDeleting] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const hasSubmissions = submissionCount > 0

  const fetchCharts = async (isRefresh = false) => {
    if (isRefresh) {
      setIsRefreshing(true)
    } else {
      setIsLoading(true)
    }
    
    try {
      const response = await fetch(`/api/forms/${formId}/charts`)
      if (response.ok) {
        const data = await response.json()
        setCharts(data)
      } else {
        console.error('Failed to fetch charts')
      }
    } catch (error) {
      console.error('Error fetching charts:', error)
    } finally {
      if (isRefresh) {
        setIsRefreshing(false)
      } else {
        setIsLoading(false)
      }
    }
  }

  useEffect(() => {
    fetchCharts()
    
    // Track analytics page view for admin insights
    if (user?.id) {
      trackFormInteraction(
        user.id,
        formId,
        "Analytics View",
        "viewed",
        {
          analytics_session: {
            view_timestamp: new Date().toISOString(),
            page_type: "analytics",
            user_role: "admin"
          }
        }
      ).catch(error => {
        console.warn("Failed to track analytics view:", error);
      });
    }
  }, [formId, user?.id])

  const handleChartCreated = () => {
    fetchCharts()
    
    // Track chart creation for admin insights
    if (user?.id) {
      trackFormInteraction(
        user.id,
        formId,
        "Chart Created",
        "created",
        {
          chart_analytics: {
            creation_timestamp: new Date().toISOString(),
            creation_method: "ai_generated",
            total_charts_after: charts.length + 1
          }
        }
      ).catch(error => {
        console.warn("Failed to track chart creation:", error);
      });
    }
  }

  const handleRefresh = () => {
    fetchCharts(true)
  }

  const handleOpenAICreator = () => {
    if (!hasSubmissions) {
      toast({
        title: "No submissions available",
        description: "You need form submissions before you can create charts.",
        variant: "destructive"
      });
      return;
    }
    setShowAICreator(true);
  }

  const deleteChart = async (chartId: string) => {
    setIsDeleting(chartId)
    try {
      const response = await fetch(`/api/forms/${formId}/charts/${chartId}`, {
        method: 'DELETE',
      })

      if (response.ok) {
        setCharts(charts.filter(chart => chart.id !== chartId))
        toast({
          title: "Chart deleted",
          description: "The chart has been removed from your analytics.",
        })
      } else {
        throw new Error('Failed to delete chart')
      }
    } catch (error) {
      console.error('Error deleting chart:', error)
      toast({
        title: "Error deleting chart",
        description: "Please try again later.",
        variant: "destructive"
      })
    } finally {
      setIsDeleting(null)
    }
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200/60 p-4 sm:p-8 h-full">
        <div className="animate-pulse space-y-6">
          <div className="flex justify-between items-center">
            <div className="h-6 w-32 bg-gray-200 rounded"></div>
            <div className="h-10 w-40 bg-gray-200 rounded"></div>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="h-80 bg-gray-100 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200/60 p-4 sm:p-8 h-full">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-gray-900">Analytics</h2>
          <p className="text-sm text-gray-600 mt-1">
            Visualize your form data with interactive charts
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button 
            onClick={handleRefresh}
            variant="outline"
            disabled={isRefreshing}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          
          <Button 
            onClick={handleOpenAICreator}
            className={`${hasSubmissions ? 'bg-purple-600 hover:bg-purple-700' : 'bg-gray-300 cursor-not-allowed'} text-white`}
            disabled={!hasSubmissions}
            title={hasSubmissions ? undefined : "You need form submissions before you can create charts"}
          >
            <Sparkles className="h-4 w-4 mr-2" />
            Create Charts with AI
          </Button>
        </div>
      </div>

      {charts.length === 0 ? (
        <div className="text-center py-12">
          <BarChart3 className="h-16 w-16 text-gray-300 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No charts yet</h3>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            {hasSubmissions 
              ? "Create your first chart to start visualizing your form data. Our AI can analyze your responses and suggest the best chart types."
              : "You need form submissions before you can create charts. Share your form to collect responses first."
            }
          </p>
          {hasSubmissions ? (
            <Button 
              onClick={handleOpenAICreator}
              className="bg-purple-600 hover:bg-purple-700 text-white"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Create Your First Chart
            </Button>
          ) : (
            <Button 
              disabled
              className="bg-gray-300 text-white cursor-not-allowed"
            >
              <Sparkles className="h-4 w-4 mr-2" />
              Need Submissions to Create Charts
            </Button>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {charts.map((chart) => (
            <div key={chart.id} className="relative group">
              <div className="absolute top-4 right-4 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm" className="h-8 w-8 p-0 bg-white/90 backdrop-blur-sm">
                      <MoreVertical className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem
                      onClick={() => deleteChart(chart.id)}
                      disabled={isDeleting === chart.id}
                      className="text-red-600 focus:text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      {isDeleting === chart.id ? 'Deleting...' : 'Delete'}
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
              
              <ChartDisplay
                type={chart.type}
                config={chart.config}
                title={chart.title}
                className="h-80"
                formId={formId}
              />
            </div>
          ))}
          
          {/* Add Chart Card */}
          <div 
            className={`h-80 border-2 border-dashed border-gray-300 rounded-lg flex flex-col items-center justify-center ${hasSubmissions ? 'cursor-pointer hover:border-purple-400 hover:bg-purple-50/50' : 'cursor-not-allowed opacity-60'} transition-colors`}
            onClick={hasSubmissions ? handleOpenAICreator : undefined}
            title={hasSubmissions ? undefined : "You need form submissions before you can create charts"}
          >
            <Plus className="h-12 w-12 text-gray-400 mb-3" />
            <h3 className="text-lg font-medium text-gray-600 mb-1">Add New Chart</h3>
            <p className="text-sm text-gray-500 text-center px-4">
              {hasSubmissions
                ? "Use AI to create charts from your form data"
                : "Need submissions to create charts"
              }
            </p>
          </div>
        </div>
      )}

      <AIChartCreator
        isOpen={showAICreator}
        onOpenChange={setShowAICreator}
        formId={formId}
        onChartCreated={handleChartCreated}
      />
    </div>
  )
} 