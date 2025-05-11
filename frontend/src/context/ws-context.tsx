'use client'
import { createContext, useContext, useEffect, useRef, useState, ReactNode, useCallback } from 'react'
import { useSnackbar } from 'notistack'
import { WS_URL } from '@/lib/api'

type WebSocketContextType = {
  connect: () => void
  disconnect: () => void
  isConnected: boolean
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

export function WebSocketProvider({ children }: { children: ReactNode }) {
  const { enqueueSnackbar } = useSnackbar()
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  const cleanupWebSocket = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.onopen = null
      wsRef.current.onclose = null
      wsRef.current.onerror = null
      wsRef.current.onmessage = null
      if (wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.close()
      }
      wsRef.current = null
    }
    setIsConnected(false)
  }, [])

  const connect = useCallback(() => {
    cleanupWebSocket()

    const ws = new WebSocket(WS_URL)
    wsRef.current = ws

    ws.onopen = () => {
      setIsConnected(true)
      enqueueSnackbar('WebSocket подключен', { variant: 'success' })
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      const message = `Пользователь ${data.username} приобрёл ${data.item} в количестве ${data.quantity} шт.`
      enqueueSnackbar(message, { variant: 'info' })
    }

    ws.onclose = () => {
      setIsConnected(false)
      enqueueSnackbar('WebSocket отключен', { variant: 'warning' })
    }

    ws.onerror = (error: Event) => {
      const errorEvent = error as ErrorEvent
      enqueueSnackbar(`Ошибка WebSocket: ${errorEvent.message || 'Unknown error'}`, { 
        variant: 'error' 
      })
      cleanupWebSocket()
    }
  }, [cleanupWebSocket, enqueueSnackbar])

  const disconnect = useCallback(() => {
    cleanupWebSocket()
    enqueueSnackbar('Соединение закрыто', { variant: 'info' })
  }, [cleanupWebSocket, enqueueSnackbar])

  useEffect(() => {
    return () => {
      cleanupWebSocket()
    }
  }, [cleanupWebSocket])

  return (
    <WebSocketContext.Provider value={{ connect, disconnect, isConnected }}>
      {children}
    </WebSocketContext.Provider>
  )
}

export function useWebSocket() {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocket must be used within WebSocketProvider')
  }
  return context
}
