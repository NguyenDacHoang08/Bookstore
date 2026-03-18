export const views = [
  { id: 'login', label: 'Login' },
  { id: 'register', label: 'Register' },
  { id: 'shop', label: 'Shop' },
  { id: 'cart', label: 'Cart' },
  { id: 'orders', label: 'Checkout' },
  { id: 'ratings', label: 'Ratings' },
  { id: 'staff', label: 'Staff' },
  { id: 'catalog', label: 'Catalog' },
  { id: 'recommend', label: 'Recommend' },
  { id: 'ops', label: 'Ops' },
] as const

export type ViewId = (typeof views)[number]['id']

export const viewRoutes: Record<ViewId, string> = {
  login: '/login',
  register: '/register',
  shop: '/',
  cart: '/cart',
  orders: '/orders',
  ratings: '/ratings',
  staff: '/staff',
  catalog: '/catalog',
  recommend: '/recommend',
  ops: '/ops',
}

export const paymentMethods = [
  { value: 'cod', label: 'Cash on Delivery' },
  { value: 'card', label: 'Card' },
  { value: 'bank', label: 'Bank Transfer' },
] as const

export const shippingMethods = [
  { value: 'standard', label: 'Standard' },
  { value: 'express', label: 'Express' },
  { value: 'pickup', label: 'Store Pickup' },
] as const
