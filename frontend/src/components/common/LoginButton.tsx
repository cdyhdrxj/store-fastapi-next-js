"use client"
import { Button } from "@mui/material"
import { useRouter } from "next/navigation"

export function LoginButton() {
  const router = useRouter()

  const handleLogin = () => {
    router.push("/login")
  }

  return (
    <Button variant="outlined" onClick={handleLogin} sx={{ color: "white" }}>
      Войти
    </Button>
  )
}
