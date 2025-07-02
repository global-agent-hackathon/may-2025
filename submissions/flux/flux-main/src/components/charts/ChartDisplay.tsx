"use client"

import React, { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  AreaChart,
  Area,
  ResponsiveContainer
} from 'recharts'

interface DataPoint {
  name: string;
  value: number;
}

interface ChartConfig {
  field_id?: string
  field_label?: string
  sql_query?: string
  data_transform?: string
  x_axis_label?: string
  y_axis_label?: string
  filters?: any
  fieldId?: string
  fieldLabel?: string
  data?: Array<{
    name: string
    value: number
    date?: string
  }>
  xAxis?: string
  yAxis?: string
}

interface ChartDisplayProps {
  type: 'bar' | 'pie' | 'line' | 'area' | 'doughnut'
  config: ChartConfig
  title: string
  className?: string
  formId?: string
  isPreview?: boolean
}

const COLORS = [
  '#8884d8', '#82ca9d', '#ffc658', '#ff7300', '#00ff00',
  '#ff00ff', '#00ffff', '#ff0000', '#0000ff', '#ffff00'
]

export function ChartDisplay({ type, config, title, className = '', formId, isPreview = false }: ChartDisplayProps) {
  const [chartData, setChartData] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchChartData = async () => {
    if (!formId || !config.sql_query) {
      // No SQL query available, use sample data
      console.log('ChartDisplay: No formId or sql_query, using sample data', { formId, sql_query: config.sql_query })
      setChartData(getSampleData())
      return
    }

    console.log('ChartDisplay: Fetching chart data', { formId, config })
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`/api/forms/${formId}/execute-chart`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          form_id: formId,
          chartConfig: config
        }),
      })

      console.log('ChartDisplay: Response status:', response.status)

      if (!response.ok) {
        const errorText = await response.text()
        console.error('ChartDisplay: Response not ok:', errorText)
        throw new Error(`Failed to fetch chart data: ${response.status} ${errorText}`)
      }

      const result = await response.json()
      
      // Log the response for debugging
      console.log('Chart data response:', result)
      
      if (!result.success) {
        console.error('ChartDisplay: Result not successful:', result)
        throw new Error(result.message || 'Failed to load chart data')
      }
      
      if (!result.data_points || !Array.isArray(result.data_points)) {
        console.error('Invalid data_points format:', result)
        throw new Error('Invalid chart data format')
      }
      
      // Validate data points
      const validDataPoints = result.data_points.filter((point: unknown): point is DataPoint => 
        point !== null &&
        typeof point === 'object' &&
        point !== null &&
        'name' in point &&
        'value' in point &&
        typeof (point as any).name === 'string' &&
        typeof (point as any).value === 'number'
      )
      
      console.log('ChartDisplay: Valid data points:', validDataPoints)
      
      if (validDataPoints.length === 0) {
        console.warn('No valid data points found, using sample data. Original data_points:', result.data_points)
        setChartData(getSampleData())
        return
      }
      
      setChartData(validDataPoints)
    } catch (err) {
      console.error('Error fetching chart data:', err)
      setError('Failed to load chart data')
      // Fallback to sample data on error
      setChartData(getSampleData())
    } finally {
      setIsLoading(false)
    }
  }

  const getSampleData = () => {
    const fieldLabel = config.field_label || config.fieldLabel || 'Category'
    
    switch (type) {
      case 'pie':
      case 'doughnut':
        if (fieldLabel.toLowerCase().includes('skill')) {
          return [
            { name: 'Programming', value: 8 },
            { name: 'Design', value: 5 },
            { name: 'Analysis', value: 6 },
            { name: 'Management', value: 3 }
          ]
        }
        return [
          { name: 'Option A', value: 30 },
          { name: 'Option B', value: 45 },
          { name: 'Option C', value: 25 }
        ]
      case 'line':
      case 'area':
        return [
          { name: 'Jan', value: 20 },
          { name: 'Feb', value: 35 },
          { name: 'Mar', value: 45 },
          { name: 'Apr', value: 30 }
        ]
      default:
        return [
          { name: 'Category 1', value: 40 },
          { name: 'Category 2', value: 30 },
          { name: 'Category 3', value: 35 }
        ]
    }
  }

  useEffect(() => {
    fetchChartData()
  }, [formId, config.sql_query])

  const renderChart = () => {
    if (isLoading) {
      return (
        <div className="w-full h-full animate-pulse">
          {type === 'pie' || type === 'doughnut' ? (
            // Pie chart shimmer
            <div className="flex items-center justify-center h-full">
              <div className="relative">
                <div className="w-48 h-48 rounded-full bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] animate-[shimmer_2s_infinite]"></div>
                {type === 'doughnut' && (
                  <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-20 h-20 rounded-full bg-white"></div>
                  </div>
                )}
              </div>
            </div>
          ) : (
            // Bar/Line/Area chart shimmer
            <div className="h-full p-4 space-y-4">
              {/* Chart area */}
              <div className="h-full bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] animate-[shimmer_2s_infinite] rounded-lg"></div>
              
              {/* X-axis labels */}
              <div className="flex justify-between space-x-4">
                {[1, 2, 3, 4].map((i) => (
                  <div key={i} className="h-3 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 bg-[length:200%_100%] animate-[shimmer_2s_infinite] rounded flex-1"></div>
                ))}
              </div>
            </div>
          )}
        </div>
      )
    }

    if (error && !isPreview) {
      return (
        <div className="w-full h-full flex items-center justify-center">
          <div className="text-center">
            <div className="text-2xl mb-2">⚠️</div>
            <div className="text-sm text-red-600">{error}</div>
            <div className="text-xs text-gray-500 mt-1">Showing sample data</div>
          </div>
        </div>
      )
    }

    // Only show "No data available" if we're not loading and actually have no data
    if (!isLoading && (!chartData || chartData.length === 0)) {
      return (
        <div className="w-full h-full flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-2xl mb-2">📊</div>
            <div className="text-sm">No data available for this chart</div>
          </div>
        </div>
      )
    }

    switch (type) {
      case 'pie':
      case 'doughnut':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                outerRadius="80%"
                innerRadius={type === 'doughnut' ? "40%" : 0}
                fill="#8884d8"
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        )
      
      case 'bar':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="value" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        )
      
      case 'line':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="value" stroke="#8884d8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        )
      
      case 'area':
        return (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="value" stroke="#8884d8" fill="#8884d8" />
            </AreaChart>
          </ResponsiveContainer>
        )
      
      default:
        return (
          <div className="w-full h-full bg-gray-100 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <div className="text-2xl mb-2">📊</div>
              <div className="text-sm text-gray-600">Unsupported chart type: {type}</div>
            </div>
          </div>
        )
    }
  }

  return (
    <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className} group relative`}>
      {!isPreview && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold text-gray-900 truncate">{title}</h3>
        </div>
      )}
      <div className={`w-full ${isPreview ? 'h-full' : 'h-64 min-h-[16rem]'} overflow-hidden`}>
        {renderChart()}
      </div>
    </div>
  )
} 