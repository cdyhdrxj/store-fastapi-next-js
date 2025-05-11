"use client"

import type React from "react"

import { Inter } from "next/font/google"
import { ThemeProvider, createTheme } from "@mui/material/styles"
import CssBaseline from "@mui/material/CssBaseline"
import { SnackbarProvider } from "notistack"
import { WebSocketProvider } from '@/context/ws-context'
import { getCookie } from 'cookies-next/client'
import BaseLayout from "@/components/layout/BaseLayout"
import UserLayout from "@/components/layout/UserLayout"
import ManagerLayout from "@/components/layout/ManagerLayout"
import AdminLayout from "@/components/layout/AdminLayout"

const inter = Inter({ subsets: ["latin", "cyrillic"] })

const theme = createTheme({
  palette: {
    primary: {
      main: "#1976d2",
    },
    secondary: {
      main: "#f50057",
    },
  },
  typography: {
    fontFamily: inter.style.fontFamily,
  },
})

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const role = getCookie('user-role')

  return (
    <html lang="ru">
      <body>
        <ThemeProvider theme={theme}>
          <CssBaseline />
          <SnackbarProvider maxSnack={3}>
            <WebSocketProvider>
              {!role && <BaseLayout>{children}</BaseLayout>}
              {role === "user" && <UserLayout>{children}</UserLayout>}
              {role === "manager" && <ManagerLayout>{children}</ManagerLayout>}
              {role === "admin" && <AdminLayout>{children}</AdminLayout>}
            </WebSocketProvider>
          </SnackbarProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
