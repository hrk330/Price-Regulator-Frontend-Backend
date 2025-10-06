'use client'

interface TopViolatingProductsProps {
  data?: Array<{
    regulated_product__name: string
    count: number
  }>
}

export function TopViolatingProducts({ data }: TopViolatingProductsProps) {
  if (!data || data.length === 0) {
    return (
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-gray-900">Top Violating Products</h3>
        </div>
        <div className="card-body">
          <p className="text-gray-500 text-center py-8">No data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="text-lg font-medium text-gray-900">Top Violating Products</h3>
      </div>
      <div className="card-body">
        <div className="space-y-4">
          {data.slice(0, 10).map((item, index) => (
            <div key={item.regulated_product__name} className="flex items-center justify-between">
              <div className="flex items-center">
                <div className="flex-shrink-0 w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                  <span className="text-xs font-medium text-primary-600">
                    {index + 1}
                  </span>
                </div>
                <span className="text-sm font-medium text-gray-900 truncate">
                  {item.regulated_product__name}
                </span>
              </div>
              <div className="flex items-center">
                <span className="text-sm text-gray-600 mr-2">{item.count}</span>
                <div className="w-16 bg-gray-200 rounded-full h-2">
                  <div 
                    className="bg-primary-600 h-2 rounded-full" 
                    style={{ 
                      width: `${(item.count / data[0].count) * 100}%` 
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
