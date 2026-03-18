import type { Book, CartItem, Order } from '../types'
import { formatMoney } from '../utils/format'

type OpsPanelProps = {
  orders: Order[]
  books: Book[]
  cartItems: CartItem[]
}

export default function OpsPanel({ orders, books, cartItems }: OpsPanelProps) {
  const revenue = orders.reduce(
    (sum, order) => sum + Number(order.total_amount || 0),
    0
  )

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Operations pulse</h2>
          <p>Quick metrics for the manager dashboard.</p>
        </div>
      </div>
      <div className="grid">
        <div className="card">
          <h3>Revenue</h3>
          <p className="muted">Sum of recent orders</p>
          <strong className="mega">{formatMoney(revenue)}</strong>
        </div>
        <div className="card">
          <h3>Inventory coverage</h3>
          <p className="muted">Books in stock</p>
          <strong className="mega">{books.filter((book) => book.stock > 0).length}</strong>
        </div>
        <div className="card">
          <h3>Customer activity</h3>
          <p className="muted">Total cart items</p>
          <strong className="mega">{cartItems.length}</strong>
        </div>
      </div>
    </section>
  )
}
