"use client"

import Typography from "@mui/material/Typography"
import Box from "@mui/material/Box"
import Button from "@mui/material/Button"
import AddIcon from "@mui/icons-material/Add"

interface PageHeaderProps {
  title: string
  buttonText?: string
  onButtonClick?: () => void
}

export default function PageHeader({ title, buttonText, onButtonClick }: PageHeaderProps) {
  return (
    <Box sx={{ display: "flex", justifyContent: "space-between", mb: 3 }}>
      <Typography component="h1" variant="h4">
        {title}
      </Typography>
      {buttonText && onButtonClick && (
        <Button variant="contained" color="primary" startIcon={<AddIcon />} onClick={onButtonClick}>
          {buttonText}
        </Button>
      )}
    </Box>
  )
}
