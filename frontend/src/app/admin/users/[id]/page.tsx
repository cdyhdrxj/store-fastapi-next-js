"use client"

import type React from "react"

import { use, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSnackbar } from "notistack"
import Paper from "@mui/material/Paper"
import TextField from "@mui/material/TextField"
import Button from "@mui/material/Button"
import Grid from "@mui/material/Grid"
import FormControl from "@mui/material/FormControl"
import InputLabel from "@mui/material/InputLabel"
import Select from "@mui/material/Select"
import MenuItem from "@mui/material/MenuItem"
import Typography from "@mui/material/Typography"
import Box from "@mui/material/Box"
import IconButton from "@mui/material/IconButton"
import ArrowBackIcon from "@mui/icons-material/ArrowBack"
import { usersAPI } from "@/lib/api"
import type { UserCreate, UserUpdate } from "@/lib/types"
import { roleNames } from "@/lib/types"
import PageHeader from "@/components/common/PageHeader"

interface ItemFormProps {
  params: Promise<{
    id: string,
  }>;
}

export default function UserAdminForm({ params }: ItemFormProps) {
  const router = useRouter()
  const { enqueueSnackbar } = useSnackbar()
  const { id } = use(params);
  const isNew = id === "new"
  const [loading, setLoading] = useState(!isNew)

  const [user, setUser] = useState<Partial<UserCreate>>({
    username: "",
    password: "",
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        if (!isNew) {
          const userRes = await usersAPI.getUser(parseInt(id))
          setUser({
            ...userRes,
          })
        }
      } catch (error: any) {
        enqueueSnackbar(error.message, { variant: "error" })
        router.push("/admin/users")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id, isNew, enqueueSnackbar])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setUser((prev) => ({ ...prev, [name]: value }))
  }

  const handleRoleChange = (e: any) => {
    const { name, value } = e.target
    setUser((prev) => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      if (isNew) {
        await usersAPI.createUser(user)
        enqueueSnackbar("Пользователь успешно создан", { variant: "success" })
      } else {
        const newUser: UserUpdate = {
          role: user.role
        }
        await usersAPI.updateUser(parseInt(id), newUser)
        enqueueSnackbar("Пользователь успешно обновлен", { variant: "success" })
      }
      router.push("/admin/users")
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  const handleBack = () => {
    router.push("/admin/users")
  }

  if (loading) {
    return <Typography>Загрузка...</Typography>
  }

  return (
    <>
      <Box sx={{ mb: 1, display: "flex", alignItems: "flex-start" }}>
        <IconButton onClick={handleBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <PageHeader title={isNew ? "Новый пользователь" : "Редактирование пользователя"} />
      </Box>

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} sx={{ display: "flex", flexDirection: "column" }}>
            <Grid size={{ xs: 6 }}>
              <TextField
                required
                fullWidth
                label="Логин"
                name="username"
                value={user.username}
                onChange={handleChange}
                disabled={id !== "new"}
                slotProps={{
                  htmlInput: {
                    minLength: 3,
                    maxLength: 64,
                  }
                }}
              />
            </Grid>
            {isNew &&
              <Grid size={{ xs: 6 }}>
                <TextField
                  required
                  fullWidth
                  label="Пароль"
                  name="password"
                  value={user.password}
                  onChange={handleChange}
                  slotProps={{
                    htmlInput: {
                      minLength: 8,
                      maxLength: 64,
                      pattern: "^(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d]{8,}$",
                      title: "Нет пробелов, минимум 1 буква и 1 цифра"
                    }
                  }}
                />
              </Grid>
            }
            <Grid size={{ xs: 6 }}>
              <FormControl fullWidth required>
                <InputLabel>Роль</InputLabel>
                <Select name="role" value={user.role ?? ""} onChange={handleRoleChange} label="Роль">
                {Object.entries(roleNames).map(([value, label]) => (
                  <MenuItem key={value} value={value}>{label}</MenuItem>
                ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Box sx={{ display: "flex", justifyContent: "flex-end", mt: 2 }}>
                <Button type="submit" variant="contained" color="primary">
                  {isNew ? "Создать" : "Сохранить"}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </form>
      </Paper>
    </>
  )
}