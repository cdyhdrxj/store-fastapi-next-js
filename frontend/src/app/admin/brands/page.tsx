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
import { brandsAPI } from "@/lib/api"
import type { Brand } from "@/lib/types"
import PageHeader from "@/components/common/PageHeader"
import ConfirmDialog from "@/components/common/ConfirmDialog"

export default function BrandsPage() {
  const { enqueueSnackbar } = useSnackbar()
  const [brands, setBrands] = useState<Brand[]>([])
  const [loading, setLoading] = useState(true)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [currentBrand, setCurrentBrand] = useState<Partial<Brand>>({
    name: "",
  })
  const [isEditing, setIsEditing] = useState(false)

  const fetchBrands = async () => {
    setLoading(true)
    try {
      const response = await brandsAPI.getBrands()
      setBrands(response)
    } catch (error) {
      enqueueSnackbar("Ошибка при загрузке данных", { variant: "error" })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchBrands()
  }, [])

  const handleAddBrand = () => {
    setCurrentBrand({ name: "" })
    setIsEditing(false)
    setDialogOpen(true)
  }

  const handleEditBrand = (brand: Brand) => {
    setCurrentBrand({ ...brand })
    setIsEditing(true)
    setDialogOpen(true)
  }

  const handleDeleteClick = (brand: Brand) => {
    setCurrentBrand(brand)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!currentBrand.id) return

    try {
      await brandsAPI.deleteBrand(currentBrand.id)
      enqueueSnackbar("Бренд успешно удален", { variant: "success" })
      fetchBrands()
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
    setCurrentBrand((prev) => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    try {
      if (isEditing && currentBrand.id) {
        await brandsAPI.updateBrand(currentBrand.id, currentBrand)
        enqueueSnackbar("Бренд успешно обновлен", { variant: "success" })
      } else {
        await brandsAPI.createBrand(currentBrand)
        enqueueSnackbar("Бренд успешно создан", { variant: "success" })
      }
      setDialogOpen(false)
      fetchBrands()
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  return (
    <>
      <PageHeader title="Бренды" buttonText="Добавить бренд" onButtonClick={handleAddBrand} />

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
              {brands.map((brand) => (
                <TableRow key={brand.id}>
                 <TableCell>{brand.name}</TableCell>
                  <TableCell align="right">
                    <IconButton color="primary" onClick={() => handleEditBrand(brand)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDeleteClick(brand)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {brands.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={4} align="center">
                    Бренды не найдены
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <form onSubmit={handleSubmit}>
          <DialogTitle>{isEditing ? "Редактировать бренд" : "Добавить бренд"}</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              name="name"
              label="Название бренда"
              type="text"
              fullWidth
              value={currentBrand.name}
              onChange={handleInputChange}
              required
              slotProps={{
                htmlInput: {
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
        title="Удаление бренда"
        message={`Вы уверены, что хотите удалить бренд "${currentBrand.name}"?`}
        onConfirm={handleDeleteConfirm}
        onCancel={() => setDeleteDialogOpen(false)}
      />
    </>
  )
}
