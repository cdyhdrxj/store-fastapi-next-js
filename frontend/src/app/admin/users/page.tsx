"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSnackbar } from "notistack"
import Paper from "@mui/material/Paper"
import Table from "@mui/material/Table"
import TableBody from "@mui/material/TableBody"
import TableCell from "@mui/material/TableCell"
import TableContainer from "@mui/material/TableContainer"
import TableHead from "@mui/material/TableHead"
import TableRow from "@mui/material/TableRow"
import IconButton from "@mui/material/IconButton"
import EditIcon from "@mui/icons-material/Edit"
import DeleteIcon from "@mui/icons-material/Delete"
import { usersAPI } from "@/lib/api"
import type { User } from "@/lib/types"
import { roleNames } from "@/lib/types"
import PageHeader from "@/components/common/PageHeader"
import ConfirmDialog from "@/components/common/ConfirmDialog"

export default function UsersAdminPage() {
  const router = useRouter()
  const { enqueueSnackbar } = useSnackbar()
  const [users, setUsers] = useState<User[]>([])
  const [loading, setLoading] = useState(true)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [userToDelete, setUserToDelete] = useState<number | null>(null)

  type UserRole = keyof typeof roleNames;

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await usersAPI.getUsers()
      setUsers(response)
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [])

  const handleAddUser = () => {
    router.push("/admin/users/new")
  }

  const handleEditUser = (id: number) => {
    router.push(`/admin/users/${id}`)
  }

  const handleDeleteClick = (id: number) => {
    setUserToDelete(id)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!userToDelete) return

    try {
      await usersAPI.deleteUser(userToDelete)
      enqueueSnackbar("Пользователь успешно удален", { variant: "success" })
      fetchUsers()
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    } finally {
      setDeleteDialogOpen(false)
      setUserToDelete(null)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
    setUserToDelete(null)
  }

  return (
    <>
      <PageHeader title="Пользователи" buttonText="Добавить пользователя" onButtonClick={handleAddUser} />

      <Paper sx={{ width: "100%", mb: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Логин</TableCell>
                <TableCell>Роль</TableCell>
                <TableCell align="right">Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user) => (
                <TableRow key={user.id}>
                  <TableCell>{user.username}</TableCell>
                  <TableCell>{roleNames[user.role as unknown as UserRole]}</TableCell>
                  <TableCell align="right">
                    <IconButton color="primary" onClick={() => handleEditUser(user.id)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDeleteClick(user.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {users.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={3} align="center">
                    Пользователи не найдены
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
     </Paper>

      <ConfirmDialog
        open={deleteDialogOpen}
        title="Удаление пользователя"
        message="Вы уверены, что хотите удалить этого пользователя?"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </>
  )
}
