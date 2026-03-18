import { useEffect, useMemo, useRef, useState } from 'react'
import { Navigate, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import Header from './components/Header'
import Hero from './components/Hero'
import Toast from './components/Toast'
import ShopPanel from './components/ShopPanel'
import CartPanel from './components/CartPanel'
import OrdersPanel from './components/OrdersPanel'
import RatingsPanel from './components/RatingsPanel'
import StaffPanel from './components/StaffPanel'
import RegisterPanel from './components/RegisterPanel'
import LoginPanel from './components/LoginPanel'
import CatalogPanel from './components/CatalogPanel'
import RecommendPanel from './components/RecommendPanel'
import OpsPanel from './components/OpsPanel'
import { paymentMethods, shippingMethods, viewRoutes } from './constants'
import type { ViewId } from './constants'
import type {
  Book,
  BookDraft,
  CartItem,
  CartItemWithBook,
  LoginForm,
  Order,
  OrderForm,
  Rating,
  RegisterForm,
  Toast as ToastType,
} from './types'

const api = async <T,>(url: string, options: RequestInit = {}) => {
  const headers = new Headers(options.headers)
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json')
  }

  const response = await fetch(url, {
    ...options,
    headers,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `HTTP ${response.status}`)
  }

  if (response.status === 204) return null as T
  return (await response.json()) as T
}

const getViewFromPath = (pathname: string): ViewId => {
  const normalized = pathname.replace(/\/+$/, '') || '/'
  const entry = (Object.entries(viewRoutes) as [ViewId, string][]).find(
    ([, path]) => path === normalized
  )
  return entry ? entry[0] : 'shop'
}

export default function App() {
  const location = useLocation()
  const navigate = useNavigate()
  const view = getViewFromPath(location.pathname)
  const [books, setBooks] = useState<Book[]>([])
  const [cartItems, setCartItems] = useState<CartItem[]>([])
  const [orders, setOrders] = useState<Order[]>([])
  const [ratings, setRatings] = useState<Rating[]>([])
  const [search, setSearch] = useState('')
  const [selectedBookId, setSelectedBookId] = useState<number | null>(null)
  const [customerId, setCustomerId] = useState<string>(() => {
    return localStorage.getItem('customerId') || ''
  })
  const [toast, setToast] = useState<ToastType | null>(null)
  const [loadingBooks, setLoadingBooks] = useState(false)
  const [loadingCart, setLoadingCart] = useState(false)
  const [loadingOrders, setLoadingOrders] = useState(false)
  const [loadingRatings, setLoadingRatings] = useState(false)
  const [loginForm, setLoginForm] = useState<LoginForm>({
    customerId: '',
    email: '',
  })
  const [registerForm, setRegisterForm] = useState<RegisterForm>({
    name: '',
    email: '',
  })
  const [orderForm, setOrderForm] = useState<OrderForm>({
    payment_method: paymentMethods[0].value,
    shipping_method: shippingMethods[0].value,
    shipping_address: '',
  })
  const [newBook, setNewBook] = useState<BookDraft>({
    title: '',
    author: '',
    price: '',
    stock: '0',
  })
  const [editBookId, setEditBookId] = useState<number | null>(null)
  const [editBook, setEditBook] = useState<BookDraft>({
    title: '',
    author: '',
    price: '',
    stock: '0',
  })
  const toastTimer = useRef<number | null>(null)

  const bookMap = useMemo(() => {
    return Object.fromEntries(books.map((book) => [book.id, book]))
  }, [books])

  const cartWithBooks = useMemo<CartItemWithBook[]>(() => {
    return cartItems.map((item) => ({
      ...item,
      book: bookMap[item.book_id],
    }))
  }, [cartItems, bookMap])

  const cartTotal = useMemo(() => {
    return cartWithBooks.reduce((total, item) => {
      const price = Number(item.book?.price || 0)
      return total + price * item.quantity
    }, 0)
  }, [cartWithBooks])

  const notify = (message: string, type: ToastType['type'] = 'info') => {
    if (toastTimer.current) {
      window.clearTimeout(toastTimer.current)
    }
    setToast({ message, type })
    toastTimer.current = window.setTimeout(() => setToast(null), 3500)
  }

  const persistCustomer = (value: string) => {
    setCustomerId(value)
    if (value) {
      localStorage.setItem('customerId', value)
    } else {
      localStorage.removeItem('customerId')
    }
  }

  const loadBooks = async () => {
    setLoadingBooks(true)
    try {
      const data = await api<Book[]>('/api/book/books/')
      setBooks(data)
      if (!selectedBookId && data.length > 0) {
        setSelectedBookId(data[0].id)
      }
    } catch (error) {
      notify('Failed to load books', 'error')
    } finally {
      setLoadingBooks(false)
    }
  }

  const loadCart = async (id: string) => {
    if (!id) return
    setLoadingCart(true)
    try {
      const data = await api<CartItem[]>(`/api/cart/carts/${id}/`)
      setCartItems(data)
    } catch (error) {
      notify('Failed to load cart', 'error')
    } finally {
      setLoadingCart(false)
    }
  }

  const loadOrders = async (id: string) => {
    if (!id) return
    setLoadingOrders(true)
    try {
      const data = await api<Order[]>(`/api/order/orders/?customer_id=${id}`)
      setOrders(data)
    } catch (error) {
      notify('Failed to load orders', 'error')
    } finally {
      setLoadingOrders(false)
    }
  }

  const loadRatings = async (bookId: number | null) => {
    if (!bookId) return
    setLoadingRatings(true)
    try {
      const data = await api<Rating[]>(`/api/rate/ratings/?book_id=${bookId}`)
      setRatings(data)
    } catch (error) {
      notify('Failed to load ratings', 'error')
    } finally {
      setLoadingRatings(false)
    }
  }

  const addToCart = async (bookId: number, quantity: number) => {
    if (!customerId) {
      notify('Set a customer id first', 'error')
      navigate(viewRoutes.login)
      return
    }
    if (quantity <= 0) {
      notify('Quantity must be greater than 0', 'error')
      return
    }
    try {
      await api('/api/cart/cart-items/', {
        method: 'POST',
        body: JSON.stringify({
          customer_id: customerId,
          book_id: bookId,
          quantity,
        }),
      })
      notify('Added to cart', 'success')
      loadCart(customerId)
    } catch (error) {
      notify('Add to cart failed', 'error')
    }
  }

  const updateCartItem = async (itemId: number, quantity: number) => {
    try {
      await api(`/api/cart/cart-items/${itemId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ quantity }),
      })
      loadCart(customerId)
    } catch (error) {
      notify('Update failed', 'error')
    }
  }

  const removeCartItem = async (itemId: number) => {
    try {
      await api(`/api/cart/cart-items/${itemId}/`, {
        method: 'DELETE',
      })
      loadCart(customerId)
      notify('Item removed', 'success')
    } catch (error) {
      notify('Remove failed', 'error')
    }
  }

  const registerCustomer = async () => {
    if (!registerForm.name.trim() || !registerForm.email.trim()) {
      notify('Name and email are required', 'error')
      return
    }
    try {
      const data = await api<{ id: number; name: string; email: string }>(
        '/api/customer/customers/',
        {
          method: 'POST',
          body: JSON.stringify(registerForm),
        }
      )
      persistCustomer(String(data.id))
      setRegisterForm({ name: '', email: '' })
      notify('Customer created and cart initialized', 'success')
      loadCart(String(data.id))
      loadOrders(String(data.id))
      navigate(viewRoutes.shop)
    } catch (error) {
      notify('Registration failed', 'error')
    }
  }

  const loginCustomer = async () => {
    const idValue = loginForm.customerId.trim()
    const emailValue = loginForm.email.trim().toLowerCase()
    if (idValue) {
      persistCustomer(idValue)
      setLoginForm({ customerId: '', email: '' })
      notify('Logged in', 'success')
      navigate(viewRoutes.shop)
      return
    }

    if (!emailValue) {
      notify('Provide a customer id or email', 'error')
      return
    }

    try {
      const customers = await api<Array<{ id: number; email: string }>>(
        '/api/customer/customers/'
      )
      const match = customers.find(
        (customer) => customer.email.toLowerCase() === emailValue
      )
      if (!match) {
        notify('Customer not found', 'error')
        return
      }
      persistCustomer(String(match.id))
      setLoginForm({ customerId: '', email: '' })
      notify('Logged in', 'success')
      navigate(viewRoutes.shop)
    } catch (error) {
      notify('Login failed', 'error')
    }
  }

  const createOrder = async () => {
    if (!customerId) {
      notify('Set a customer id first', 'error')
      navigate(viewRoutes.login)
      return
    }
    if (!orderForm.shipping_address.trim()) {
      notify('Shipping address is required', 'error')
      return
    }
    try {
      const payload = {
        customer_id: customerId,
        payment_method: orderForm.payment_method,
        shipping_method: orderForm.shipping_method,
        shipping_address: orderForm.shipping_address,
      }
      await api('/api/order/orders/', {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      notify('Order placed successfully', 'success')
      setOrderForm({
        payment_method: paymentMethods[0].value,
        shipping_method: shippingMethods[0].value,
        shipping_address: '',
      })
      loadCart(customerId)
      loadOrders(customerId)
    } catch (error) {
      notify('Order failed', 'error')
    }
  }

  const rateBook = async (bookId: number, rating: number) => {
    if (rating < 1 || rating > 5) {
      notify('Rating must be between 1 and 5', 'error')
      return
    }
    const payload: { rating: number; customer_id?: string } = { rating }
    if (!customerId) {
      notify('Login required for rating', 'error')
      navigate(viewRoutes.login)
      return
    }
    payload.customer_id = customerId
    try {
      await api(`/api/rate/books/${bookId}/rate/`, {
        method: 'POST',
        body: JSON.stringify(payload),
      })
      notify('Thanks for rating', 'success')
      loadBooks()
      loadRatings(selectedBookId)
    } catch (error) {
      notify('Rating failed', 'error')
    }
  }

  const createBook = async () => {
    if (!newBook.title.trim() || !newBook.author.trim()) {
      notify('Title and author are required', 'error')
      return
    }
    try {
      await api('/api/staff/books/', {
        method: 'POST',
        body: JSON.stringify({
          title: newBook.title,
          author: newBook.author,
          price: newBook.price,
          stock: Number(newBook.stock || 0),
        }),
      })
      setNewBook({ title: '', author: '', price: '', stock: '0' })
      notify('Book created', 'success')
      loadBooks()
    } catch (error) {
      notify('Create book failed', 'error')
    }
  }

  const startEditBook = (book: Book) => {
    setEditBookId(book.id)
    setEditBook({
      title: book.title,
      author: book.author,
      price: String(book.price),
      stock: String(book.stock),
    })
  }

  const saveEditBook = async () => {
    if (!editBookId) return
    try {
      await api(`/api/staff/books/${editBookId}/`, {
        method: 'PATCH',
        body: JSON.stringify({
          title: editBook.title,
          author: editBook.author,
          price: editBook.price,
          stock: Number(editBook.stock || 0),
        }),
      })
      notify('Book updated', 'success')
      setEditBookId(null)
      loadBooks()
    } catch (error) {
      notify('Update failed', 'error')
    }
  }

  const deleteBook = async (bookId: number) => {
    try {
      await api(`/api/staff/books/${bookId}/`, { method: 'DELETE' })
      notify('Book removed', 'success')
      loadBooks()
    } catch (error) {
      notify('Delete failed', 'error')
    }
  }

  const handleViewChange = (nextView: ViewId) => {
    navigate(viewRoutes[nextView])
  }

  useEffect(() => {
    loadBooks()
  }, [])

  useEffect(() => {
    if (customerId) {
      loadCart(customerId)
      loadOrders(customerId)
    }
  }, [customerId])

  useEffect(() => {
    if (selectedBookId) {
      loadRatings(selectedBookId)
    }
  }, [selectedBookId])

  return (
    <div className="app">
      <Header
        view={view}
        onChange={handleViewChange}
      />

      <main>
        <Hero
          booksCount={books.length}
          cartItemsCount={cartItems.length}
          ordersCount={orders.length}
          customerId={customerId}
          onLogin={() => navigate(viewRoutes.login)}
          onRegister={() => navigate(viewRoutes.register)}
        />

        <Toast toast={toast} />

        <Routes>
          <Route
            path="/"
            element={
              <ShopPanel
                books={books}
                search={search}
                onSearchChange={setSearch}
                loading={loadingBooks}
                onRefresh={loadBooks}
                onAddToCart={addToCart}
                onRateBook={rateBook}
              />
            }
          />
          <Route
            path="/cart"
            element={
              <CartPanel
                loading={loadingCart}
                cartItems={cartWithBooks}
                cartTotal={cartTotal}
                onRefresh={() => loadCart(customerId)}
                onUpdateItem={updateCartItem}
                onRemoveItem={removeCartItem}
              />
            }
          />
          <Route
            path="/orders"
            element={
              <OrdersPanel
                orderForm={orderForm}
                setOrderForm={setOrderForm}
                onCreateOrder={createOrder}
                orders={orders}
                loadingOrders={loadingOrders}
                onRefreshOrders={() => loadOrders(customerId)}
              />
            }
          />
          <Route
            path="/ratings"
            element={
              <RatingsPanel
                books={books}
                ratings={ratings}
                selectedBookId={selectedBookId}
                onSelectBook={setSelectedBookId}
                loading={loadingRatings}
              />
            }
          />
          <Route
            path="/staff"
            element={
              <StaffPanel
                books={books}
                newBook={newBook}
                setNewBook={setNewBook}
                onCreateBook={createBook}
                onRefresh={loadBooks}
                onStartEdit={startEditBook}
                onDeleteBook={deleteBook}
                editBookId={editBookId}
                editBook={editBook}
                setEditBook={setEditBook}
                onSaveEdit={saveEditBook}
                onCloseEdit={() => setEditBookId(null)}
              />
            }
          />
          <Route
            path="/login"
            element={
              <LoginPanel
                loginForm={loginForm}
                setLoginForm={setLoginForm}
                onLogin={loginCustomer}
              />
            }
          />
          <Route
            path="/register"
            element={
              <RegisterPanel
                registerForm={registerForm}
                setRegisterForm={setRegisterForm}
                onRegister={registerCustomer}
              />
            }
          />
          <Route path="/catalog" element={<CatalogPanel />} />
          <Route path="/recommend" element={<RecommendPanel books={books} />} />
          <Route
            path="/ops"
            element={<OpsPanel orders={orders} books={books} cartItems={cartItems} />}
          />
          <Route path="*" element={<Navigate to={viewRoutes.shop} replace />} />
        </Routes>
      </main>
    </div>
  )
}
