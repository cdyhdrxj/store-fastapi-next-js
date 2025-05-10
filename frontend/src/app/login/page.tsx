"use client"

import type React from "react"
import { useState } from "react"
import { Box, Button, Container, Paper, TextField, Typography } from "@mui/material"
import { useRouter } from "next/navigation"

export default function LoginPage() {
  const router = useRouter()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault()
    console.log("Логин:", username)
    console.log("Пароль:", password)
    // Здесь будет логика авторизации
    router.back()
  }

  return (
    <Container component="main" maxWidth="sm">
      <Box sx={{ mt: 8 }}>
        <Paper
          elevation={3}
          sx={{
            padding: 3,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
          }}
        >
          <Typography component="h1" variant="h4">
            Вход
          </Typography>
          <Box component="form" onSubmit={handleSubmit}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Логин"
              name="username"
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              slotProps={{
                htmlInput: {
                  minLength: 3,
                  maxLength: 64,
                }
              }}
            />
            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Пароль"
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              slotProps={{
                htmlInput: {
                  minLength: 8,
                  maxLength: 64,
                  pattern: "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$",
                  title: "Нет пробелов, минимум 1 буква и 1 цифра"
                }
              }}
            />
            <Button type="submit" variant="contained" sx={{ my: 2 }} fullWidth>
              Войти
            </Button>
          </Box>
        </Paper>
      </Box>
    </Container>
  )
}
