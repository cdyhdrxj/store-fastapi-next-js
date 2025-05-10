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
import Card from "@mui/material/Card"
import CardMedia from "@mui/material/CardMedia"
import CardActions from "@mui/material/CardActions"
import IconButton from "@mui/material/IconButton"
import DeleteIcon from "@mui/icons-material/Delete"
import ArrowBackIcon from "@mui/icons-material/ArrowBack"
import { itemsAPI, categoriesAPI, brandsAPI, coversAPI, imagesAPI, getURL } from "@/lib/api"
import type { Item, ItemCreateUpdate, Category, Brand } from "@/lib/types"
import PageHeader from "@/components/common/PageHeader"
import ImageUploader from "@/components/common/ImageUploader"
import ConfirmDialog from "@/components/common/ConfirmDialog"

interface ItemFormProps {
  params: Promise<{
    id: string;
  }>;
}

export default function ItemAdminForm({ params }: ItemFormProps) {
  const router = useRouter()
  const { enqueueSnackbar } = useSnackbar()
  const { id } = use(params);
  const isNew = id === "new"
  const [loading, setLoading] = useState(!isNew)
  const [categories, setCategories] = useState<Category[]>([])
  const [brands, setBrands] = useState<Brand[]>([])
  const [deleteImageDialogOpen, setDeleteImageDialogOpen] = useState(false)
  const [imageToDelete, setImageToDelete] = useState<number>()
  const [isCoverImage, setIsCoverImage] = useState<boolean>(false)

  const [item, setItem] = useState<Partial<Item>>({
    name: "",
    description: "",
    price: 1,
    cover: null,
    images: [],
  })

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [categoriesRes, brandsRes] = await Promise.all([categoriesAPI.getCategories(), brandsAPI.getBrands()])

        setCategories(categoriesRes)
        setBrands(brandsRes)

        if (!isNew) {
          const itemRes = await itemsAPI.getItem(parseInt(id))
          setItem({
            ...itemRes,
          })
        }
      } catch (error: any) {
        enqueueSnackbar(error.message, { variant: "error" })
        router.push("/admin")
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [id, isNew, enqueueSnackbar])

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setItem((prev) => ({ ...prev, [name]: name === "price" ? parseInt(value) : value }))
  }

  const handleSelectChange = (e: any) => {
    const { name, value } = e.target

    setItem((prev) => ({
      ...prev,
      [name]: {
        id: value,
      }
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    const newItem: ItemCreateUpdate = {
      name: item.name ?? null,
      description: item.description ?? null,
      brand_id: item.brand ? item.brand.id : null,
      category_id: item.category ? item.category.id : null,
      price: item.price ?? null,
    }

    try {
      if (isNew) {
        const savedItem = await itemsAPI.createItem(newItem)
        enqueueSnackbar("Товар успешно создан", { variant: "success" })
        router.push(`/admin/items/${savedItem.id}`)
      } else {
        await itemsAPI.updateItem(parseInt(id), newItem)
        enqueueSnackbar("Товар успешно обновлен", { variant: "success" })
        router.push("/admin")
      }
    } catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
  }

  const handleDeleteImageClick = (isCover: boolean, imageId?: number) => {
    setIsCoverImage(isCover)
    if (!isCover) {
      setImageToDelete(imageId)
    }
    setDeleteImageDialogOpen(true)
  }

  const handleDeleteImageConfirm = async () => {
    if (isNew) return

    try {
        if (isCoverImage) {
          if (!id) return
          await coversAPI.deleteCover(parseInt(id))
          setItem((prev) => ({
            ...prev,
            cover: null,
          }))
        }
        else {
          if (!imageToDelete) return
          await imagesAPI.deleteImage(imageToDelete)
          setItem((prev) => ({
            ...prev,
            images: (prev.images || []).filter((img) => img.id !== imageToDelete),
          }))
        }
        enqueueSnackbar("Изображение удалено", { variant: "success" })
      } catch (error: any) {
        enqueueSnackbar(error.message, { variant: "error" })
      } finally {
        setDeleteImageDialogOpen(false)
        setImageToDelete(undefined)
      }
  }

  const handleDeleteImageCancel = () => {
    setDeleteImageDialogOpen(false)
    setImageToDelete(undefined)
  }

  const handleBack = () => {
    router.push("/admin")
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
        <PageHeader title={isNew ? "Новый товар" : "Редактирование товара"} />
      </Box>

      <Paper sx={{ p: 3 }}>
        <form onSubmit={handleSubmit}>
          <Grid container spacing={3} sx={{ display: "flex", flexDirection: "column"}}>
            <Grid size={{ xs: 12 }}>
              <TextField
                required
                fullWidth
                label="Название товара"
                name="name"
                value={item.name}
                onChange={handleChange}
                slotProps={{
                  htmlInput: {
                    maxLength: 200,
                  }
                }}
              />
            </Grid>
            <Grid container spacing={2}>
              <Grid size={{ xs: 4 }}>
                <FormControl fullWidth required>
                  <InputLabel>Категория</InputLabel>
                  <Select name="category" value={item.category ? item.category.id : ""} onChange={handleSelectChange} label="Категория">
                    {categories.map((category) => (
                      <MenuItem value={category.id}>{category.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 4 }}>
                <FormControl fullWidth required>
                  <InputLabel>Бренд</InputLabel>
                  <Select name="brand" value={item.brand ? item.brand.id : ""} onChange={handleSelectChange} label="Бренд">
                    {brands.map((brand) => (
                      <MenuItem value={brand.id}>{brand.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid size={{ xs: 4 }}>
                <TextField
                  required
                  fullWidth
                  type="number"
                  label="Цена"
                  name="price"
                  value={item.price ?? ""}
                  onChange={handleChange}
                  slotProps={{
                    input: {
                     inputProps: { min: 1, step: 1, max: 10 ** 8 }
                    },
                  }}
                />
              </Grid>
            </Grid>
            <Grid size={{ xs: 12 }}>
              <TextField
                required
                fullWidth
                multiline
                rows={4}
                label="Описание"
                name="description"
                value={item.description}
                onChange={handleChange}
                slotProps={{
                  htmlInput: {
                    maxLength: 1000,
                  }
                }}
              />
            </Grid>
            <Grid size={{ xs: 12 }}>
              <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 3 }}>
                <Button type="submit" variant="contained" color="primary">
                  Сохранить
                </Button>
              </Box>
            </Grid>
 
            {!isNew && (
              <>
                <Grid size={{ xs: 12 }}>
                  {item.cover ? (
                    <>
                      <Typography component="h1" variant="h5" sx={{ mb: 3 }}>
                        Обложка
                      </Typography>
                      <Grid size={{xs: 6, sm: 4, md: 3 }}>
                        <Card>
                          <CardMedia component="img" height="256" image={getURL(item.cover.name)} alt="Обложка" sx={{ objectFit: "contain" }} />
                          <CardActions>
                            <IconButton color="error" onClick={() => handleDeleteImageClick(true)}>
                              <DeleteIcon />
                            </IconButton>
                          </CardActions>
                        </Card>
                      </Grid>
                    </>
                  ) : (
                    <Grid size={{ xs: 12 }}>
                    <ImageUploader title="Обложка" isCover={true} itemId={parseInt(id)} setItem={setItem}/>
                      <Typography color="text.secondary">Нет обложки</Typography>
                    </Grid>
                  )}
                </Grid>
                <Grid size={{ xs: 12 }}>
                  <ImageUploader title="Изображения" isCover={false} itemId={parseInt(id)} setItem={setItem}/>
                  <Grid container spacing={2}>
                    {item.images && item.images.length > 0 ? (
                      item.images.map((img, index) => (
                        <Grid size={{xs: 6, sm: 4, md: 3 }} key={index}>
                          <Card>
                            <CardMedia component="img" height="256" image={getURL(img.name)} alt={`Изображение ${index + 1}`} sx={{ objectFit: "contain" }} />
                            <CardActions>
                              <IconButton color="error" onClick={() => handleDeleteImageClick(false, img.id)}>
                                <DeleteIcon />
                              </IconButton>
                            </CardActions>
                          </Card>
                        </Grid>
                      ))
                    ) : (
                      <Grid size={{ xs: 12 }}>
                        <Typography color="text.secondary">Нет изображений</Typography>
                      </Grid>
                    )}
                  </Grid>
                </Grid>
              </>
            )}
         </Grid>
        </form>
      </Paper>

      <ConfirmDialog
        open={deleteImageDialogOpen}
        title="Удаление изображения"
        message="Вы уверены, что хотите удалить это изображение?"
        onConfirm={handleDeleteImageConfirm}
        onCancel={handleDeleteImageCancel}
      />
    </>
  )
}
