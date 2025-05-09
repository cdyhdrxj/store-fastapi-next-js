// URL API
const API_URL = "http://localhost:8000"
// URL папки с изображениями
const IMG_URL = "http://localhost/img/"

// Возвращает URL изображения
export function getURL(filename: string) {
  return IMG_URL + filename
}

// Общая функция для выполнения запросов
async function fetchAPI(endpoint: string, options: RequestInit = {}, isImage: boolean = false) {
  const url = `${API_URL}${endpoint}`
  const headers = new Headers(options.headers)

  if (!isImage)
    headers.set("Content-Type", "application/json")

  const req = {
    method: "GET",
    headers: headers,
    ...options,
  }

  const response = await fetch(url, req)
  const data = await response.json()

  if (!response.ok) {
    throw new Error(data.detail[0].msg || data.detail || "Произошла ошибка при выполнении запроса")
  }

  return data
}

// API для работы с товарами
export const itemsAPI = {
  getItems: async (page = 1, limit = 10, search = "") => {
    const queryParams = new URLSearchParams({
      offset: page.toString(),
      limit: limit.toString(),
    })

    if (search) queryParams.append("search", search)

    return fetchAPI(`/items?${queryParams.toString()}`)
  },
  getItem: async (id: number) => {
    return fetchAPI(`/items/${id}`, {
      method: "GET",
    })
  },
  createItem: async (itemData: any) => {
    return fetchAPI("/items", {
      method: "POST",
      body: JSON.stringify(itemData),
    })
  },
  updateItem: async (id: number, itemData: any) => {
    return fetchAPI(`/items/${id}`, {
      method: "PATCH",
      body: JSON.stringify(itemData),
    })
  },
  deleteItem: async (id: number) => {
    return fetchAPI(`/items/${id}`, {
      method: "DELETE",
    })
  },
  updateQuantity: async (id: number, itemData: any) => {
    return fetchAPI(`/items/add/${id}`, {
      method: "PATCH",
      body: JSON.stringify(itemData),
    })
  }
}

// API для работы с обложками
export const coversAPI = {
  createCover: async (id: number, coverData: any) => {
    return fetchAPI(`/items/cover/${id}`, {
      method: "POST",
      body: coverData,
    }, true);
  },
  deleteCover: async (id: number) => {
    return fetchAPI(`/items/cover/${id}`, {
      method: "DELETE",
    }, true);
  },
}

// API для работы с изображениями
export const imagesAPI = {
  createImage: async (id: number, imageData: any) => {
    return fetchAPI(`/items/images/${id}`, {
      method: "POST",
      body: imageData,
    }, true);
  },
  deleteImage: async (id: number) => {
    return fetchAPI(`/items/images/${id}`, {
      method: "DELETE",
    }, true);
  },
}

// API для работы с категориями
export const categoriesAPI = {
  getCategories: async () => {
    return fetchAPI("/categories", {
      method: "GET",
    });
  },
  getCategory: async (id: number) => {
    return fetchAPI(`/categories/${id}`, {
      method: "GET",
    })
  },
  createCategory: async (categoryData: any) => {
    return fetchAPI("/categories", {
      method: "POST",
      body: JSON.stringify(categoryData),
    })
  },
  updateCategory: async (id: number, categoryData: any) => {
    return fetchAPI(`/categories/${id}`, {
      method: "PATCH",
      body: JSON.stringify(categoryData),
    })
  },
  deleteCategory: async (id: number) => {
    return fetchAPI(`/categories/${id}`, {
      method: "DELETE",
    })
  },
}

// API для работы с брендами
export const brandsAPI = {
  getBrands: async () => {
    return fetchAPI("/brands", {
      method: "GET",
    })
  },
  getBrand: async (id: number) => {
    return fetchAPI(`/brands/${id}`, {
      method: "GET",
    })
  },
  createBrand: async (brandData: any) => {
    return fetchAPI("/brands", {
      method: "POST",
      body: JSON.stringify(brandData),
    })
  },
  updateBrand: async (id: number, brandData: any) => {
    return fetchAPI(`/brands/${id}`, {
      method: "PATCH",
      body: JSON.stringify(brandData),
    })
  },
  deleteBrand: async (id: number) => {
    return fetchAPI(`/brands/${id}`, {
      method: "DELETE",
    })
  },
}

// API для работы с пользователями
export const usersAPI = {
  getUsers: async () => {
    return fetchAPI("/users", {
      method: "GET",
    })
  },
  getUser: async (id: number) => {
    return fetchAPI(`/users/${id}`, {
      method: "GET",
    })
  },
  createUser: async (userData: any) => {
    return fetchAPI("/users", {
      method: "POST",
      body: JSON.stringify(userData),
    })
  },
  updateUser: async (id: number, userData: any) => {
    return fetchAPI(`/users/${id}`, {
      method: "PATCH",
      body: JSON.stringify(userData),
    })
  },
  deleteUser: async (id: number) => {
    return fetchAPI(`/users/${id}`, {
      method: "DELETE",
    })
  },
}
