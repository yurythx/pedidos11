import React from 'react'
import { ChevronLeft, ChevronRight } from 'lucide-react'

interface TableProps {
  children: React.ReactNode
}

interface TableHeaderProps {
  children: React.ReactNode
}

interface TableBodyProps {
  children: React.ReactNode
}

interface TableRowProps {
  children: React.ReactNode
  onClick?: () => void
  className?: string
}

interface TableHeadProps {
  children: React.ReactNode
  className?: string
}

interface TableCellProps extends React.TdHTMLAttributes<HTMLTableCellElement> {
  children: React.ReactNode
  className?: string
}

export function Table({ children }: TableProps) {
  return (
    <div className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          {children}
        </table>
      </div>
    </div>
  )
}

export function TableHeader({ children }: TableHeaderProps) {
  return (
    <thead className="bg-gray-50/50 border-b border-gray-100">
      {children}
    </thead>
  )
}

export function TableBody({ children }: TableBodyProps) {
  return (
    <tbody className="divide-y divide-gray-50">
      {children}
    </tbody>
  )
}

export function TableRow({ children, onClick, className = '' }: TableRowProps) {
  return (
    <tr 
      onClick={onClick}
      className={`
        hover:bg-gray-50/50 transition-colors duration-150
        ${onClick ? 'cursor-pointer' : ''}
        ${className}
      `}
    >
      {children}
    </tr>
  )
}

export function TableHead({ children, className = '' }: TableHeadProps) {
  return (
    <th className={`px-6 py-4 text-xs font-semibold text-gray-500 uppercase tracking-wider ${className}`}>
      {children}
    </th>
  )
}

export function TableCell({ children, className = '', ...props }: TableCellProps) {
  return (
    <td className={`px-6 py-4 text-sm text-gray-700 ${className}`} {...props}>
      {children}
    </td>
  )
}

interface PaginationProps {
  page: number
  pageSize: number
  totalItems?: number
  onPageChange: (page: number) => void
  onPageSizeChange?: (size: number) => void
  hasMore?: boolean
}

export function TablePagination({ 
  page, 
  pageSize, 
  onPageChange, 
  onPageSizeChange,
  hasMore = true
}: PaginationProps) {
  return (
    <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100 bg-white">
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-500">Linhas por página:</span>
        <select
          value={pageSize}
          onChange={(e) => onPageSizeChange?.(Number(e.target.value))}
          className="text-sm border border-gray-200 rounded-lg px-2 py-1 focus:ring-2 focus:ring-primary/20 outline-none"
        >
          <option value={10}>10</option>
          <option value={20}>20</option>
          <option value={50}>50</option>
          <option value={100}>100</option>
        </select>
      </div>

      <div className="flex items-center gap-2">
        <button
          onClick={() => onPageChange(page - 1)}
          disabled={page <= 1}
          className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronLeft className="w-5 h-5 text-gray-600" />
        </button>
        <span className="text-sm font-medium text-gray-700">
          Página {page}
        </span>
        <button
          onClick={() => onPageChange(page + 1)}
          disabled={!hasMore}
          className="p-2 rounded-lg hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <ChevronRight className="w-5 h-5 text-gray-600" />
        </button>
      </div>
    </div>
  )
}
