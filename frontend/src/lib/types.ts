export interface ItemCreateUpdate {
  name: string | null
  description: string | null
  price: number | null
  brand_id: number | null
  category_id: number | null
}

export interface ItemQuantityUpdate {
  quantity: number
}

export interface Item {
  id: number
  name: string
  description: string
  price: number
  quantity: number
  category: Category
  brand: Brand
  cover: Cover | null
  images: Image[]
}

export interface Category {
  id: number
  name: string
}

export interface Brand {
  id: number
  name: string
}

export interface Cover {
  id: number
  name: string
}

export interface Image {
  id: number
  name: string
}

export interface PaginationData {
  total: number
  page: number
  limit: number
  pages: number
}

export enum Role {
  user,
  manager,
  admin,
}

export const roleNames = {
  admin: "Администратор",
  manager: "Менеджер",
  user: "Обычный пользователь",
}

export interface User {
  id: number
  username: string
  role: Role
}

export interface UserCreate {
  username: string
  password: string
  role: Role | undefined
}

export interface UserUpdate {
  role: Role | undefined
}
