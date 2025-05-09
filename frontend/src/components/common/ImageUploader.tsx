"use client"

import type React from "react"
import { useState, useRef } from "react"
import { Box, Button, Typography } from "@mui/material"
import { CloudUpload } from "@mui/icons-material"
import { useSnackbar } from "notistack"
import { imagesAPI, coversAPI } from "@/lib/api"

interface ImageUploaderProps {
  title: string
  isCover: boolean
  itemId: number
  setItem: any
}

const MAX_FILE_SIZE = 5 * 1024 * 1024

export default function ImageUploader( { title, isCover, itemId, setItem } : ImageUploaderProps) {
  const { enqueueSnackbar } = useSnackbar()
  const [loading, setLoading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleButtonClick = () => {
    fileInputRef.current?.click()
  }

  const validateFile = (file: File): boolean => {
    if (file.size > MAX_FILE_SIZE) {
      enqueueSnackbar("Размер файла не должен превышать 5 МБ", { variant: "error" })
      return false
    }
    return true
  }

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files || files.length === 0) return
    const file = files[0]

    if (!validateFile(file)) {
      event.target.value = ""
      return
    }

    setLoading(true)
    const formData = new FormData()
    formData.append("file", file)
   
    try {
      if (isCover) {
        const newItem = await coversAPI.createCover(itemId, formData) 
        enqueueSnackbar("Обложка добавлена", { variant: "success" })
        setItem(newItem)
      }
      else {
        const newItem = await imagesAPI.createImage(itemId, formData) 
        enqueueSnackbar("Изображение добавлено", { variant: "success" })
        setItem(newItem)
      }
    }
    catch (error: any) {
      enqueueSnackbar(error.message, { variant: "error" })
    }
    finally {
      setLoading(false)
      event.target.value = ""
    }
  }

  return (
    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
      <Typography component="h1" variant="h5">
        {title}
      </Typography>
      <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          style={{ display: "none" }}
        />

        <Button
          variant="contained"
          color="primary"
          onClick={handleButtonClick}
          startIcon={<CloudUpload />}
          disabled={loading}
        >
          Загрузить
        </Button>
      </Box>
    </Box>
  )
}
