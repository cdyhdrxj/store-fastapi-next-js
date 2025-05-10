"use client"

import type React from "react"

import { useState, useEffect } from "react"
import { useSnackbar } from "notistack"
import Paper from "@mui/material/Paper"
import TextField from "@mui/material/TextField"
import { Alert, CircularProgress, Grid, Pagination, Typography } from "@mui/material"
import InputAdornment from "@mui/material/InputAdornment"
import SearchIcon from "@mui/icons-material/Search"
import Box from "@mui/material/Box"
import { itemsAPI } from "@/lib/api"
import type { Item, PaginationData } from "@/lib/types"
import ItemCard from "@/components/common/ItemCard"
import BuyDialog from "@/components/common/BuyDialog"

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
      ) : items.length === 0 ? (
        <Alert severity="info">Товары не найдены</Alert>
      ) : (
        <>
          <Grid container spacing={3} p={3}>
            {items.map((item) => (
              <Grid key={item.id} size={{xs: 12, sm: 6, md: 4, lg: 3}}>
                <ItemCard item={item} setId={setItemToBuy} setDialogOpen={setDialogOpen}/>
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
      <BuyDialog id={itemToBuy} open={dialogOpen} setOpen={setDialogOpen} updatePage={fetchItems}/>
    </>
  )
}
