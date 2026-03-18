import type { Dispatch, SetStateAction } from 'react'
import { paymentMethods, shippingMethods } from '../constants'
import type { Order, OrderForm } from '../types'
import { formatDate, formatMoney } from '../utils/format'

type OrdersPanelProps = {
  orderForm: OrderForm
  setOrderForm: Dispatch<SetStateAction<OrderForm>>
  onCreateOrder: () => void
  orders: Order[]
  loadingOrders: boolean
  onRefreshOrders: () => void
}

export default function OrdersPanel({
  orderForm,
  setOrderForm,
  onCreateOrder,
  orders,
  loadingOrders,
  onRefreshOrders,
}: OrdersPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Checkout</h2>
          <p>Choose payment and shipping, then place order.</p>
        </div>
      </div>
      <div className="split">
        <div className="card">
          <h3>Place an order</h3>
          <label>
            Payment method
            <select
              value={orderForm.payment_method}
              onChange={(event) =>
                setOrderForm((current) => ({
                  ...current,
                  payment_method: event.target.value,
                }))
              }
            >
              {paymentMethods.map((method) => (
                <option key={method.value} value={method.value}>
                  {method.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Shipping method
            <select
              value={orderForm.shipping_method}
              onChange={(event) =>
                setOrderForm((current) => ({
                  ...current,
                  shipping_method: event.target.value,
                }))
              }
            >
              {shippingMethods.map((method) => (
                <option key={method.value} value={method.value}>
                  {method.label}
                </option>
              ))}
            </select>
          </label>
          <label>
            Shipping address
            <textarea
              rows={3}
              value={orderForm.shipping_address}
              onChange={(event) =>
                setOrderForm((current) => ({
                  ...current,
                  shipping_address: event.target.value,
                }))
              }
            />
          </label>
          <button className="primary" onClick={onCreateOrder}>
            Place order
          </button>
        </div>
        <div className="card">
          <div className="card-top">
            <h3>Recent orders</h3>
            <button className="ghost" onClick={onRefreshOrders}>
              Refresh
            </button>
          </div>
          {loadingOrders ? (
            <div className="empty">Loading orders...</div>
          ) : orders.length === 0 ? (
            <div className="empty">No orders yet.</div>
          ) : (
            <div className="stack">
              {orders.map((order) => (
                <div key={order.id} className="stack-item">
                  <div>
                    <strong>Order #{order.id}</strong>
                    <p className="muted">{formatDate(order.created_at)}</p>
                  </div>
                  <div className="badge-group">
                    <span className="pill neutral">{order.status}</span>
                    <span className="pill good">{order.payment_status}</span>
                    <span className="pill neutral">{order.shipping_status}</span>
                  </div>
                  <div className="muted">{formatMoney(order.total_amount)}</div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </section>
  )
}
