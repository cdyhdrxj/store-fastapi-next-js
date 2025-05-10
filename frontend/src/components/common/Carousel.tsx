"use client"

import React from "react"

import { useState, type ReactNode } from "react"
import { Box, IconButton } from "@mui/material"
import { ChevronLeft, ChevronRight } from "@mui/icons-material"

interface CarouselProps {
  children: ReactNode
  height?: string | number
}

export default function Carousel({ children, height = 400 }: CarouselProps) {
  const [activeIndex, setActiveIndex] = useState(0)
  const slides = React.Children.toArray(children)

  const handleNext = () => {
    setActiveIndex((prevIndex) => (prevIndex + 1) % slides.length)
  }

  const handlePrev = () => {
    setActiveIndex((prevIndex) => (prevIndex - 1 + slides.length) % slides.length)
  }

  return (
    <Box
      sx={{
        position: "relative",
        width: "100%",
        overflow: "hidden",
        borderRadius: 2,
      }}
    >
      <Box
        sx={{
          display: "flex",
          transition: "transform 0.5s ease",
          transform: `translateX(-${activeIndex * 100}%)`,
          height: "100%",
        }}
      >
        {slides.map((slide, index) => (
          <Box
            key={index}
            sx={{
              minWidth: "100%",
              height: "100%",
            }}
          >
            {slide}
          </Box>
        ))}
      </Box>

      {slides.length > 1 && (
        <>
          <IconButton
            onClick={handlePrev}
            sx={{
              position: "absolute",
              left: 16,
              top: "50%",
              transform: "translateY(-50%)",
              bgcolor: "rgba(255, 255, 255, 0.8)",
              "&:hover": {
                bgcolor: "rgba(255, 255, 255, 0.9)",
              },
              zIndex: 2,
            }}
          >
            <ChevronLeft />
          </IconButton>

          <IconButton
            onClick={handleNext}
            sx={{
              position: "absolute",
              right: 16,
              top: "50%",
              transform: "translateY(-50%)",
              bgcolor: "rgba(255, 255, 255, 0.8)",
              "&:hover": {
                bgcolor: "rgba(255, 255, 255, 0.9)",
              },
              zIndex: 2,
            }}
          >
            <ChevronRight />
          </IconButton>
        </>
      )}
    </Box>
  )
}
