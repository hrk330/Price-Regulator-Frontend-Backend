'use client'

import { useQuery } from '@tanstack/react-query'
import { violationsApi, casesApi } from '@/lib/api'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { RecentViolations } from '@/components/investigator/RecentViolations'
import { MyCases } from '@/components/investigator/MyCases'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'
import { AlertTriangle, FileText, CheckCircle, Clock } from 'lucide-react'

export default function InvestigatorDashboard() {
  const { data: violationStats, isLoading: violationsLoading } = useQuery({
    queryKey: ['violation-stats'],
    queryFn: violationsApi.stats,
  })

  const { data: caseStats, isLoading: casesLoading } = useQuery({
    queryKey: ['case-stats'],
    queryFn: casesApi.stats,
  })

  if (violationsLoading || casesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }

  return (
    <div>
      {/* Page description */}
      <div className="mb-2">
        <p className="text-gray-600">
          Review violations and manage investigation cases
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
        <StatsCard
          title="Pending Violations"
          value={violationStats?.pending_violations || 0}
          icon={Clock}
          color="yellow"
        />
        <StatsCard
          title="My Open Cases"
          value={caseStats?.open_cases || 0}
          icon={FileText}
          color="blue"
        />
        <StatsCard
          title="Confirmed Today"
          value={violationStats?.recent_violations || 0}
          icon={CheckCircle}
          color="green"
        />
        <StatsCard
          title="Total Violations"
          value={violationStats?.total_violations || 0}
          icon={AlertTriangle}
          color="red"
        />
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RecentViolations />
        <MyCases />
      </div>
    </div>
  )
}
