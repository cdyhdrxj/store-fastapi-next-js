"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useSnackbar } from "notistack"
import Paper from "@mui/material/Paper"
import Dialog from "@mui/material/Dialog"
import DialogActions from "@mui/material/DialogActions"
import DialogContent from "@mui/material/DialogContent"
import DialogTitle from "@mui/material/DialogTitle"
import TextField from "@mui/material/TextField"
import { Alert, CircularProgress, Grid, Pagination, Typography } from "@mui/material"
import Button from "@mui/material/Button"
import InputAdornment from "@mui/material/InputAdornment"
import SearchIcon from "@mui/icons-material/Search"
import Box from "@mui/material/Box"
import { itemsAPI } from "@/lib/api"
import type { Item, PaginationData } from "@/lib/types"
import ItemCard from "@/components/common/ItemCard"

export default function MainPage() {
  const { enqueueSnackbar } = useSnackbar()
  const [items, setItems] = useState<Item[]>([])
  const [pagination, setPagination] = useState<PaginationData>({
    total: 0,
    page: 1,
    limit: 20,
    pages: 0,
  })
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState("")
  const [itemToBuy, setItemToBuy] = useState<number | null>(null)
  const [dialogOpen, setDialogOpen] = useState(false)

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
        page: newPage,
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

  const handleClickBuy = (id: number) => {
    setItemToBuy(id)
    setDialogOpen(true)
  }

  const handleBuyItem = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!itemToBuy) return

    // try {
    //   await itemsAPI.updateQuantity(itemToUpdateQuantity, currentItem)
    //   enqueueSnackbar("Спасибо за покупку!", { variant: "success" })
    //   setDialogOpen(false)
    //   fetchItems()
    // } catch (error: any) {
    //   enqueueSnackbar(error.message, { variant: "error" })
    // }
  }

  const handleDialogClose = () => {
    setDialogOpen(false)
  }

  return (
    <>
      <Typography component="h1" variant="h4" gutterBottom>
        Каталог товаров
      </Typography>

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

        {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", my: 4, mx: 4 }}>
          <CircularProgress />
        </Box>
    //   ) : error ? (
    //     <Alert severity="error">{error}</Alert>
      ) : items.length === 0 ? (
        <Alert severity="info">Товары не найдены. Попробуйте изменить параметры поиска.</Alert>
      ) : (
        <>
          <Grid container spacing={3} p={3}>
            {items.map((item) => (
              <Grid key={item.id} size={{xs: 12, sm: 6, md: 4, lg: 3}}>
                <ItemCard item={item} />
              </Grid>
            ))}
          </Grid>

          <Box sx={{ display: "flex", justifyContent: "center", pb: 2 }}>
            <Pagination
              count={pagination.pages}
              page={pagination.page}
              onChange={handleChangePage}
              color="primary"
              size="large"
              showFirstButton
              showLastButton
            />
          </Box>
        </>
      )}

      </Paper>

      {/* <Dialog open={dialogOpen} onClose={handleDialogClose} maxWidth="sm" fullWidth>
        <form onSubmit={handleClickBuy}>
          <DialogTitle>Купить товар</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              required
              margin="dense"
              name="delta"
              label="Количество товара"
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
      </Dialog> */}
    </>
  )
}
