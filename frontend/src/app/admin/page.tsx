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
import TablePagination from "@mui/material/TablePagination"
import IconButton from "@mui/material/IconButton"
import EditIcon from "@mui/icons-material/Edit"
import DeleteIcon from "@mui/icons-material/Delete"
import AddIcon from '@mui/icons-material/Add'
import Dialog from "@mui/material/Dialog"
import DialogActions from "@mui/material/DialogActions"
import DialogContent from "@mui/material/DialogContent"
import DialogTitle from "@mui/material/DialogTitle"
import TextField from "@mui/material/TextField"
import Button from "@mui/material/Button"
import InputAdornment from "@mui/material/InputAdornment"
import SearchIcon from "@mui/icons-material/Search"
import Box from "@mui/material/Box"
import { itemsAPI } from "@/lib/api"
import type { Item, ItemQuantityUpdate, PaginationData } from "@/lib/types"
import PageHeader from "@/components/common/PageHeader"
import ConfirmDialog from "@/components/common/ConfirmDialog"

export default function itemsPage() {
  const router = useRouter()
  const { enqueueSnackbar } = useSnackbar()
  const [items, setItems] = useState<Item[]>([])
  const [pagination, setPagination] = useState<PaginationData>({
    total: 0,
    page: 1,
    limit: 10,
    pages: 0,
  })
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [itemToDelete, setItemToDelete] = useState<number | null>(null)
  const [itemToUpdateQuantity, setItemToUpdateQuantity] = useState<number | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)
  const [currentItem, setCurrentItem] =
  useState<ItemQuantityUpdate>({
    quantity: 1,
  })

  const fetchItems = async (page = 1, limit = 10, searchTerm = "") => {
    setLoading(true)
    try {
      const response = await itemsAPI.getItems(page - 1, limit, searchTerm)
      setPagination(prev => ({
        ...prev,
        total: response.total,
        pages: response.pages,
      }))
      setItems(response.items)
    } catch (error) {
      enqueueSnackbar("Ошибка при загрузке данных", { variant: "error" })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchItems(pagination.page, pagination.limit, search)
  }, [pagination.page, pagination.limit, search])

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPagination(prev => ({
        ...prev,
        page: newPage + 1,
    }))
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    const newLimit = Number.parseInt(event.target.value, 10)
    setPagination(prev => ({
        ...prev,
        page: 1,
        limit: newLimit,
    }))
  }

  const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setSearch(event.target.value)
    setPagination(prev => ({
        ...prev,
        page: 1,
    }))
  }

  const handleSearchSubmit = (event: React.FormEvent) => {
    event.preventDefault()
  }

  const handleAddItem = () => {
    router.push("/admin/items/new")
  }

  const handleEditItem = (id: number) => {
    router.push(`/admin/items/${id}`)
  }

  const handleDeleteClick = (id: number) => {
    setItemToDelete(id)
    setDeleteDialogOpen(true)
  }

  const handleDeleteConfirm = async () => {
    if (!itemToDelete) return

    try {
      await itemsAPI.deleteItem(itemToDelete)
      enqueueSnackbar("Товар успешно удален", { variant: "success" })
      fetchItems(pagination.page, pagination.limit, search)
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    } finally {
      setDeleteDialogOpen(false)
      setItemToDelete(null)
    }
  }

  const handleDeleteCancel = () => {
    setDeleteDialogOpen(false)
    setItemToDelete(null)
  }

  const handleQuantityClick = (id: number) => {
    setItemToUpdateQuantity(id)
    setDialogOpen(true)
  }

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { value } = e.target
    setCurrentItem({quantity: parseInt(value)})
  }

  const handleUpdateQuantity = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!itemToUpdateQuantity) return

    try {
      await itemsAPI.updateQuantity(itemToUpdateQuantity, currentItem)
      enqueueSnackbar("Количество товара успешно обновлено", { variant: "success" })
      setDialogOpen(false)
      fetchItems()
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
  }

  return (
    <>
      <PageHeader title="Товары" buttonText="Добавить товар" onButtonClick={handleAddItem} />

      <Paper sx={{ width: "100%", mb: 2 }}>
        <Box component="form" onSubmit={handleSearchSubmit} sx={{ p: 2 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Поиск товаров..."
            value={search}
            onChange={handleSearchChange}
            slotProps={{
              input: {
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }
            }}
          />
        </Box>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Название</TableCell>
                <TableCell>Цена</TableCell>
                <TableCell>Количество</TableCell>
                <TableCell>Категория</TableCell>
                <TableCell>Бренд</TableCell>
                <TableCell align="right">Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {items.map((item) => (
                <TableRow key={item.id}>
                  <TableCell>{item.name}</TableCell>
                  <TableCell>{item.price} руб.</TableCell>
                  <TableCell>{item.quantity}</TableCell>
                  <TableCell>{item.category.name}</TableCell>
                  <TableCell>{item.brand.name}</TableCell>
                  <TableCell align="right">
                    <IconButton color="primary" onClick={() => handleQuantityClick(item.id)}>
                      <AddIcon />
                    </IconButton>
                    <IconButton color="primary" onClick={() => handleEditItem(item.id)}>
                      <EditIcon />
                    </IconButton>
                    <IconButton color="error" onClick={() => handleDeleteClick(item.id)}>
                      <DeleteIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              {items.length === 0 && !loading && (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    Товары не найдены
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[1, 5, 10, 25, 100]}
          component="div"
          count={pagination.total}
          rowsPerPage={pagination.limit}
          page={pagination.page - 1}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          labelRowsPerPage="Строк на странице:"
        />
      </Paper>

      <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <form onSubmit={handleUpdateQuantity}>
          <DialogTitle>Поступление товара</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              required
              margin="dense"
              name="delta"
              label="Изменение количества товара"
              type="number"
              fullWidth
              value={currentItem.quantity ?? ""}
              onChange={handleInputChange}
              sx={{ mb: 2 }}
              slotProps={{
                input: {
                  inputProps: { min: 1, step: 1, max: 10 ** 8 }
                }
              }}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={handleDialogClose}>Отмена</Button>
            <Button type="submit" variant="contained" color="primary">
              Добавить
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      <ConfirmDialog
        open={deleteDialogOpen}
        title="Удаление товара"
        message="Вы уверены, что хотите удалить этот товар?"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />
    </>
  )
}
