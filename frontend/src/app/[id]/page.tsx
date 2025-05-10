"use client"

import type React from "react"

import { use, useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { useSnackbar } from "notistack"
import Paper from "@mui/material/Paper"
import Typography from "@mui/material/Typography"
import Box from "@mui/material/Box"
import IconButton from "@mui/material/IconButton"
import ArrowBackIcon from "@mui/icons-material/ArrowBack"
import { itemsAPI, getURL } from "@/lib/api"
import PageHeader from "@/components/common/PageHeader"
import { Item, Image } from "@/lib/types"
import { Button, Card, CardMedia, Chip, Divider, Grid } from "@mui/material"
import Carousel from "@/components/common/Carousel"

interface ItemFormProps {
  params: Promise<{
    id: number;
  }>;
}

export default function ItemPage({ params }: ItemFormProps) {
  const router = useRouter()
  const { enqueueSnackbar } = useSnackbar()
  const { id } = use(params);
  const [loading, setLoading] = useState(true)
  const [item, setItem] = useState<Item>()
  const [images, setImages] = useState<Image[]>()
  const [isOutOfStock, setIsOutOfStock] = useState<boolean>()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const itemRes = await itemsAPI.getItem(id)

        let imageList: Image[] = []
        if (itemRes.cover)
          imageList = imageList.concat([{id: itemRes.cover.id, name: itemRes.cover.name}])
        if (itemRes.images.length > 0)
          imageList = imageList.concat(itemRes.images)

        setItem(itemRes)
        setImages(imageList)
        setIsOutOfStock(itemRes.quantity === 0)
      } catch (error: any) {
        enqueueSnackbar(error.message, { variant: "error" })
        router.push("/")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id, enqueueSnackbar])

  const handleBack = () => {
    router.push("/")
  }

  if (loading) {
    return <Typography>Загрузка...</Typography>
  }

  return (item && <>
      <Box sx={{ mb: 1, display: "flex", alignItems: "flex-start" }}>
        <IconButton onClick={handleBack} sx={{ mr: 1 }}>
          <ArrowBackIcon />
        </IconButton>
        <PageHeader title={item.name} />
      </Box>

      <Paper sx={{ p: 3 }}>
        <Grid container size={{ xs: 12}}>
          <Grid size={{ xs: 6}} px={2}>
            <Carousel>
              {images && images.length > 0 && (
                images.map((image, i) =>
                  <Card elevation={0}>
                    <CardMedia
                      component="img"
                      height="300"
                      image={getURL(image.name)}
                      alt={`${i}`}
                      sx={{ objectFit: "contain" }}/>
                  </Card>
                )
              )}
            </Carousel>
          </Grid>
          <Grid size={{ xs: 6}}>
            <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 2 }}>
              <Typography variant="h5" color="primary" sx={{ fontWeight: "bold" }}>
                Цена: {item.price} руб.
              </Typography>

              {isOutOfStock ? (
                <Chip label="Нет в наличии" color="error" sx={{ fontSize: "0.875rem" }} />
              ) : (
                <Button variant="contained">Купить</Button>
              )}
            </Box>

            <Divider sx={{ my: 2 }} />

            <Typography variant="h6" gutterBottom fontWeight="medium">
              Описание:
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {item.description}
            </Typography>
          </Grid>
        </Grid>
      </Paper>
    </>
  )
}