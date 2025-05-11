"use client"

import { useEffect } from "react"
import { Button } from "@mui/material"
import { useRouter } from "next/navigation"
import { loginAPI } from "@/lib/api"
import { enqueueSnackbar } from "notistack"
import { deleteCookie } from 'cookies-next/client'
import { useWebSocket } from "@/context/ws-context"

interface LogoutButtonProps {
  isManager: boolean
}

export function LogoutButton( { isManager } : LogoutButtonProps) {
  const router = useRouter()
  const { connect, disconnect, isConnected } = useWebSocket()
  
  const handleLogout = async () => {
    try {
      await loginAPI.logout()
      enqueueSnackbar("Вы успешно вышли из аккаунта", { variant: "success" })
      deleteCookie('user-role')
      if (isManager && isConnected)
        disconnect()
      router.push("/")
      router.refresh()
    }
    catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  if (isManager) {
    useEffect(() => {
      if (!isConnected) connect()
    }, [])
  }

  return (
    <Button variant="outlined" onClick={handleLogout} sx={{ color: "white" }}>
      Выйти
    </Button>
  )
}
