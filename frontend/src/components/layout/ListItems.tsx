"use client"

import { usePathname } from "next/navigation"
import Link from "next/link"
import ListItemButton from "@mui/material/ListItemButton"
import ListItemIcon from "@mui/material/ListItemIcon"
import ListItemText from "@mui/material/ListItemText"
import ShoppingCartIcon from "@mui/icons-material/ShoppingCart"
import CategoryIcon from "@mui/icons-material/Category"
import BrandingWatermarkIcon from "@mui/icons-material/BrandingWatermark"
import PeopleIcon from '@mui/icons-material/People';

export function MainListItems() {
  const pathname = usePathname()

  const managerMenuItems = [
    { text: "Товары", icon: <ShoppingCartIcon />, href: "/admin" },
    { text: "Категории", icon: <CategoryIcon />, href: "/admin/categories" },
    { text: "Бренды", icon: <BrandingWatermarkIcon />, href: "/admin/brands" },
  ]

  const adminMenuItems = managerMenuItems.concat(
    [{ text: "Пользователи", icon: <PeopleIcon />, href: "/admin/users" }]
  )

  return (
    <>
      {adminMenuItems.map((item) => (
        <Link key={item.href} href={item.href} style={{ textDecoration: "none", color: "inherit" }}>
          <ListItemButton selected={pathname === item.href}>
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItemButton>
        </Link>
      ))}
    </>
  )
}
