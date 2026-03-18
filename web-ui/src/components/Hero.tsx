type HeroProps = {
  booksCount: number
  cartItemsCount: number
  ordersCount: number
  customerId: string
  onLogin: () => void
  onRegister: () => void
}

export default function Hero({
  booksCount,
  cartItemsCount,
  ordersCount,
  customerId,
  onLogin,
  onRegister,
}: HeroProps) {
  return (
    <section className="hero">
      <div>
        <p className="eyebrow">Bookstore orchestration</p>
        <h1>Everything your bookstore needs, in one cockpit.</h1>
        <p className="hero-copy">
          Manage catalogs, carts, orders, and customer experience across services
          without leaving the dashboard.
        </p>
        <div className="hero-actions">
          <button className="primary" onClick={onLogin}>
            Login
          </button>
          <button className="ghost" onClick={onRegister}>
            Create customer
          </button>
        </div>
      </div>
      <div className="hero-card">
        <div className="hero-stat">
          <span>Books</span>
          <strong>{booksCount}</strong>
        </div>
        <div className="hero-stat">
          <span>Cart items</span>
          <strong>{cartItemsCount}</strong>
        </div>
        <div className="hero-stat">
          <span>Orders</span>
          <strong>{ordersCount}</strong>
        </div>
        <div className="hero-stat">
          <span>Active customer</span>
          <strong>{customerId || 'Unset'}</strong>
        </div>
      </div>
    </section>
  )
}
