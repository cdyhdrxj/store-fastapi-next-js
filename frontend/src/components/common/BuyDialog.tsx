"use client"

import { useState } from "react"
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  IconButton,
  Typography,
  Box,
  Paper,
} from "@mui/material"
import { useSnackbar } from "notistack"
import { Add as AddIcon, Remove as RemoveIcon } from "@mui/icons-material"
import { buyAPI } from "@/lib/api"

const MAX_QUANTITY = 10 ** 8

interface BuyDialogProps {
  id: number | null
  open: boolean
  setOpen: (open: boolean) => void
  updatePage: () => void
}

export default function BuyDialog({ id, open, setOpen, updatePage }: BuyDialogProps) {
  const { enqueueSnackbar } = useSnackbar()
  const [quantity, setQuantity] = useState(1)

  const handleIncrease = () => {
    setQuantity((prev) => (prev >= MAX_QUANTITY ? prev : prev + 1))
  }

  const handleDecrease = () => {
    setQuantity((prev) => (prev > 1 ? prev - 1 : 1))
  }

  const handleBuy = async () => {
    if (!id) return
    try {
      await buyAPI.buyItem(id, { quantity: quantity })
      enqueueSnackbar("Спасибо за покупку!", { variant: "success" })
      handleBack()
      updatePage()
    }
    catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  const handleBack = () => {
    setOpen(false)
    setQuantity(1)
  }

  return (
    <Dialog open={open} onClose={handleBack} maxWidth="sm" fullWidth>
      <DialogTitle>Покупка товара</DialogTitle>

      <DialogContent>
        <Box>
          <Paper
            elevation={0}
            sx={{
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              p: 2,
              border: "1px solid #e0e0e0",
            }}
          >
            <IconButton
              onClick={handleDecrease}
              disabled={quantity <= 1}
              sx={{ color: "primary.main" }}
            >
              <RemoveIcon />
            </IconButton>

            <Typography
              variant="h6"
              component="div"
              sx={{
                minWidth: "40px",
                textAlign: "center",
                fontWeight: "medium",
              }}
            >
              {quantity}
            </Typography>

            <IconButton
              onClick={handleIncrease}
              disabled={quantity >= MAX_QUANTITY}
              sx={{ color: "primary.main" }}
            >
              <AddIcon />
            </IconButton>
          </Paper>
        </Box>
      </DialogContent>

      <DialogActions>
        <Button onClick={handleBack}>
          Отмена
        </Button>
        <Button onClick={handleBuy} variant="contained">
          Купить
        </Button>
      </DialogActions>
    </Dialog>
  )
}
