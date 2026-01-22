'use client'
import React from 'react'
import { AlertTriangle, CheckCircle, Info, X } from 'lucide-react'

interface MessageModalProps {
  isOpen: boolean
  onClose: () => void
  onConfirm?: () => void
  title: string
  message: string
  type?: 'success' | 'error' | 'confirm' | 'info'
}

export function MessageModal({ isOpen, onClose, onConfirm, title, message, type = 'info' }: MessageModalProps) {
  if (!isOpen) return null

  const getIcon = () => {
    switch (type) {
      case 'success': return <CheckCircle className="w-12 h-12 text-green-500" />
      case 'error': return <AlertTriangle className="w-12 h-12 text-red-500" />
      case 'confirm': return <Info className="w-12 h-12 text-blue-500" />
      default: return <Info className="w-12 h-12 text-gray-500" />
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm overflow-hidden flex flex-col animate-in zoom-in-95 duration-200">
        <div className="p-6 flex flex-col items-center text-center gap-4">
          {getIcon()}
          
          <div className="space-y-2">
            <h3 className="text-xl font-bold text-gray-800">{title}</h3>
            <p className="text-gray-600 whitespace-pre-wrap">{message}</p>
          </div>
        </div>

        <div className="p-4 bg-gray-50 border-t flex gap-3 justify-center">
          {type === 'confirm' ? (
            <>
                <button 
                    onClick={onClose}
                    className="flex-1 py-3 rounded-xl font-semibold text-gray-700 hover:bg-gray-200 transition-colors"
                >
                    Cancelar
                </button>
                <button 
                    onClick={() => {
                        if (onConfirm) onConfirm()
                        onClose()
                    }}
                    className="flex-1 py-3 rounded-xl font-semibold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all active:scale-95"
                >
                    Confirmar
                </button>
            </>
          ) : (
            <button 
                onClick={onClose}
                className={`w-full py-3 rounded-xl font-semibold text-white shadow-lg transition-all active:scale-95 ${
                    type === 'error' ? 'bg-red-600 hover:bg-red-700 shadow-red-200' : 
                    type === 'success' ? 'bg-green-600 hover:bg-green-700 shadow-green-200' :
                    'bg-gray-800 hover:bg-gray-900'
                }`}
            >
                OK
            </button>
          )}
        </div>
      </div>
    </div>
  )
}