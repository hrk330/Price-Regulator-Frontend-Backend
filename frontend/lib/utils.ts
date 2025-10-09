import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(amount)
}

export function formatDate(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(date))
}

export function formatDateOnly(date: string | Date): string {
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  }).format(new Date(date))
}

export function getSeverityColor(severity: string): string {
  switch (severity) {
    case 'low':
      return 'badge-success'
    case 'medium':
      return 'badge-warning'
    case 'high':
      return 'badge-danger'
    case 'critical':
      return 'badge-danger'
    default:
      return 'badge-info'
  }
}

export function getStatusColor(status: string): string {
  switch (status) {
    case 'pending':
      return 'badge-warning'
    case 'confirmed':
      return 'badge-success'
    case 'dismissed':
      return 'badge-info'
    case 'open':
      return 'badge-warning'
    case 'in_progress':
      return 'badge-info'
    case 'closed':
      return 'badge-success'
    case 'resolved':
      return 'badge-success'
    default:
      return 'badge-info'
  }
}

export function getRoleColor(role: string): string {
  switch (role) {
    case 'admin':
      return 'badge-danger'
    case 'investigator':
      return 'badge-warning'
    case 'regulator':
      return 'badge-success'
    default:
      return 'badge-info'
  }
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}

export function generateId(): string {
  return Math.random().toString(36).substr(2, 9)
}

export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout
  return (...args: Parameters<T>) => {
    clearTimeout(timeout)
    timeout = setTimeout(() => func(...args), wait)
  }
}
