"use client"

import type React from "react"

import { useState, useEffect } from "react"
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
import Dialog from "@mui/material/Dialog"
import DialogActions from "@mui/material/DialogActions"
import DialogContent from "@mui/material/DialogContent"
import DialogTitle from "@mui/material/DialogTitle"
import TextField from "@mui/material/TextField"
import Button from "@mui/material/Button"
import { categoriesAPI } from "@/lib/api"
import type { Category } from "@/lib/types"
import PageHeader from "@/components/common/PageHeader"
import ConfirmDialog from "@/components/common/ConfirmDialog"

export default function CategoriesAdminPage() {
  const { enqueueSnackbar } = useSnackbar()
  const [categories, setCategories] = useState<Category[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [currentCategory, setCurrentCategory] = useState<Partial<Category>>({
    name: "",
  })
  const [isEditing, setIsEditing] = useState(false)

  const fetchCategories = async () => {
    setLoading(true)
    try {
      const response = await categoriesAPI.getCategories()
      setCategories(response)
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchCategories()
  }, [])

  const handleAddCategory = () => {
    setCurrentCategory({ name: "" })
    setIsEditing(false)
    setDialogOpen(true)
  }

  const handleEditCategory = (category: Category) => {
    setCurrentCategory({ ...category })
    setIsEditing(true)
    setDialogOpen(true)
  }

  const handleDeleteClick = (category: Category) => {
    setCurrentCategory(category)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!currentCategory.id) return

    try {
      await categoriesAPI.deleteCategory(currentCategory.id)
      enqueueSnackbar("Категория успешно удалена", { variant: "success" })
      fetchCategories()
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    } finally {
      setDeleteDialogOpen(false)
    }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target
    setCurrentCategory((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      if (isEditing && currentCategory.id) {
        await categoriesAPI.updateCategory(currentCategory.id, currentCategory)
        enqueueSnackbar("Категория успешно обновлена", { variant: "success" })
      } else {
        await categoriesAPI.createCategory(currentCategory)
        enqueueSnackbar("Категория успешно создана", { variant: "success" })
      }
      setDialogOpen(false)
      fetchCategories()
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  return (
    <>
      <PageHeader title="Категории" buttonText="Добавить категорию" onButtonClick={handleAddCategory} />

      <Paper sx={{ width: "100%", mb: 2 }}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Название</TableCell>
                <TableCell align="right">Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {!categories && !loading && (
                <TableRow>
                  <TableCell colSpan={3} align="center">
                    Категории не найдены
                  </TableCell>
                </TableRow>
              )}
              {categories && categories.length !== 0 && categories.map((category) => (
                <TableRow key={category.id}>
                  <TableCell>{category.name}</TableCell>
                  <TableCell align="right">
                    <IconButton color="primary" onClick={() => handleEditCategory(category)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDeleteClick(category)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
           </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>{isEditing ? "Редактировать категорию" : "Добавить категорию"}</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              name="name"
              label="Название категории"
              type="text"
              fullWidth
              value={currentCategory.name}
              onChange={handleInputChange}
              required
              slotProps={{
                htmlInput: {
                  minLength: 1,
                  maxLength: 50,
                }
              }}
              sx={{ mb: 2 }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose}>Отмена</Button>
            <Button type="submit" variant="contained" color="primary">
              Сохранить
            </Button>
          </DialogActions>
          </form>
      </Dialog>

      <ConfirmDialog
        open={deleteDialogOpen}
        title="Удаление категории"
        message={`Вы уверены, что хотите удалить категорию "${currentCategory.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteDialogOpen(false)}
      />
    </>
  )
}
