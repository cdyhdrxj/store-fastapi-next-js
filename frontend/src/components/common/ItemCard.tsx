"use client"

import type React from "react"
import Card from "@mui/material/Card"
import CardContent from "@mui/material/CardContent"
import CardMedia from "@mui/material/CardMedia"
import Typography from "@mui/material/Typography"
import Box from "@mui/material/Box"
import Chip from "@mui/material/Chip"
import type { Item } from "@/lib/types"
import { getURL } from "@/lib/api"
import Button from "@mui/material/Button"
import CardActionArea from "@mui/material/CardActionArea"

interface ItemCardProps {
  item: Item
}

export default function ItemCard({ item } : ItemCardProps) {
  const { id, name, price, cover, quantity } = item
  const isOutOfStock = quantity === 0

  return (
    <Card
      sx={{
        height: "100%",
        display: "flex",
        flexDirection: "column",
        textDecoration: "none",
        transition: "transform 0.2s",
        "&:hover": {
          transform: "translateY(-5px)",
          boxShadow: 3,
        },
      }}
    >
      <CardActionArea href={`/${id}`}>
        <Box sx={{ position: "relative" }}>
          <CardMedia
          component="img"
          height="200"
          image={getURL(cover ? cover.name : "")}
          alt={name}
          sx={{
              objectFit: "contain",
              bgcolor: "grey.100",
              filter: isOutOfStock ? "grayscale(1)" : "none",
          }}
          />
          {isOutOfStock && (
          <Chip
              label="Нет в наличии"
              color="error"
              sx={{
              position: "absolute",
              top: 10,
              right: 10,
              }}
          />
          )}
      </Box>
      </CardActionArea>
        <CardContent sx={{ flexGrow: 1, display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
          <Typography gutterBottom variant="body1" component="div" sx={{ fontWeight: 500 }}>
            {name}
          </Typography>
          <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mt: 2 }}>
            <Typography variant="h6" color="primary" sx={{ fontWeight: "bold" }}>
                {price} руб.
            </Typography>
            {!isOutOfStock && (<Button variant="contained">Купить</Button>)}
          </Box>
        </CardContent>
    </Card>
  )
}
