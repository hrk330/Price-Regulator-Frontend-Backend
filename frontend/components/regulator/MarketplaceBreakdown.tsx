'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

interface MarketplaceBreakdownProps {
  data?: Record<string, number>
}

const COLORS = ['#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6']

export function MarketplaceBreakdown({ data }: MarketplaceBreakdownProps) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Violations by Marketplace</h3>
        </div>
        <div className="card-body">
          <p className="text-gray-500 text-center py-8">No data available</p>
        </div>
      </div>
    )
  }

  const chartData = Object.entries(data).map(([marketplace, count], index) => ({
    name: marketplace.charAt(0).toUpperCase() + marketplace.slice(1),
    value: count,
    color: COLORS[index % COLORS.length]
  }))

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Violations by Marketplace</h3>
      </div>
      <div className="card-body">
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  )
}
