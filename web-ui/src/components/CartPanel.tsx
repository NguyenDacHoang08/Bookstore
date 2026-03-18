import type { CartItemWithBook } from '../types'
import { formatMoney } from '../utils/format'

type CartPanelProps = {
  loading: boolean
  cartItems: CartItemWithBook[]
  cartTotal: number
  onRefresh: () => void
  onUpdateItem: (itemId: number, quantity: number) => void
  onRemoveItem: (itemId: number) => void
}

export default function CartPanel({
  loading,
  cartItems,
  cartTotal,
  onRefresh,
  onUpdateItem,
  onRemoveItem,
}: CartPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Cart</h2>
          <p>Review and adjust cart items.</p>
        </div>
        <button className="ghost" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="empty">Loading cart...</div>
      ) : cartItems.length === 0 ? (
        <div className="empty">Cart is empty.</div>
      ) : (
        <div className="table">
          <div className="table-row table-header">
            <span>Book</span>
            <span>Price</span>
            <span>Qty</span>
            <span>Total</span>
            <span>Actions</span>
          </div>
          {cartItems.map((item) => (
            <div className="table-row" key={item.id}>
              <span>{item.book?.title || `Book #${item.book_id}`}</span>
              <span>{formatMoney(item.book?.price || 0)}</span>
              <span>
                <input
                  type="number"
                  min={1}
                  defaultValue={item.quantity}
                  className="qty"
                />
              </span>
              <span>
                {formatMoney(Number(item.book?.price || 0) * item.quantity)}
              </span>
              <span className="row-actions">
                <button
                  className="ghost"
                  type="button"
                  onClick={(event) => {
                    const input =
                      event.currentTarget
                        .closest('.table-row')
                        ?.querySelector('input')
                    const qty = Number(
                      (input as HTMLInputElement)?.value || 1
                    )
                    onUpdateItem(item.id, qty)
                  }}
                >
                  Update
                </button>
                <button
                  className="danger"
                  type="button"
                  onClick={() => onRemoveItem(item.id)}
                >
                  Remove
                </button>
              </span>
            </div>
          ))}
          <div className="table-row table-footer">
            <span>Total</span>
            <span></span>
            <span></span>
            <span>{formatMoney(cartTotal)}</span>
            <span></span>
          </div>
        </div>
      )}
    </section>
  )
}
