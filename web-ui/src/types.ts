export type Book = {
  id: number
  title: string
  author: string
  price: string | number
  stock: number
  rating_avg: number
  rating_count: number
}

export type CartItem = {
  id: number
  cart: number
  book_id: number
  quantity: number
}

export type CartItemWithBook = CartItem & { book?: Book }

export type Order = {
  id: number
  customer_id: number
  total_amount: string | number
  payment_method: string
  shipping_method: string
  payment_status: string
  shipping_status: string
  status: string
  shipping_address: string
  created_at: string
}

export type Rating = {
  id: number
  customer_id: number | null
  book_id: number
  rating: number
  comment: string
  created_at: string
}

export type Toast = {
  type: 'success' | 'error' | 'info'
  message: string
}

export type OrderForm = {
  payment_method: string
  shipping_method: string
  shipping_address: string
}

export type RegisterForm = {
  name: string
  email: string
}

export type LoginForm = {
  customerId: string
  email: string
}

export type BookDraft = {
  title: string
  author: string
  price: string
  stock: string
}
