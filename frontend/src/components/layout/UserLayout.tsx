"use client"

import type React from "react"

import Box from "@mui/material/Box"
import MuiAppBar from "@mui/material/AppBar"
import Toolbar from "@mui/material/Toolbar"
import Typography from "@mui/material/Typography"
import Container from "@mui/material/Container"
import { Button } from "@mui/material"
import Link from "next/link"
import { useRouter } from "next/navigation"

export default function UserLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter()

  const handleLogin = () => {
    router.push("/login")
  }

  return (
    <Box sx={{ display: "flex" }}>
      <MuiAppBar position="absolute">
        <Toolbar sx={{ pr: "24px" }}>
          <Typography component="h1" variant="h6" color="inherit" noWrap sx={{ flexGrow: 1 }}>
            <Link href="/" style={{ color: "inherit", textDecoration: "none" }}>
              Интернет-магазин
            </Link>
          </Typography>
          <Button variant="outlined" onClick={handleLogin} sx={{ color: "white" }}>Войти</Button>
        </Toolbar>
      </MuiAppBar>
      <Box
        component="main"
        sx={{
          backgroundColor: (theme) =>
            theme.palette.mode === "light" ? theme.palette.grey[100] : theme.palette.grey[900],
          flexGrow: 1,
          height: "100vh",
          overflow: "auto",
        }}
      >
        <Toolbar />
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
          {children}
        </Container>
      </Box>
    </Box>
  )
}
