import { useMemo } from 'react'
import type { Book } from '../types'
import { formatMoney } from '../utils/format'

type ShopPanelProps = {
  books: Book[]
  search: string
  onSearchChange: (value: string) => void
  loading: boolean
  onRefresh: () => void
  onAddToCart: (bookId: number, quantity: number) => void
  onRateBook: (bookId: number, rating: number) => void
}

export default function ShopPanel({
  books,
  search,
  onSearchChange,
  loading,
  onRefresh,
  onAddToCart,
  onRateBook,
}: ShopPanelProps) {
  const filteredBooks = useMemo(() => {
    const term = search.trim().toLowerCase()
    if (!term) return books
    return books.filter((book) => {
      return (
        book.title.toLowerCase().includes(term) ||
        book.author.toLowerCase().includes(term)
      )
    })
  }, [books, search])

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Book inventory</h2>
          <p>Browse and add books to the cart.</p>
        </div>
        <div className="panel-actions">
          <input
            className="search"
            placeholder="Search by title or author"
            value={search}
            onChange={(event) => onSearchChange(event.target.value)}
          />
          <button className="ghost" onClick={onRefresh}>
            Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="empty">Loading books...</div>
      ) : (
        <div className="grid">
          {filteredBooks.map((book) => (
            <div className="card" key={book.id}>
              <div className="card-top">
                <span className={`pill ${book.stock > 0 ? 'good' : 'bad'}`}>
                  {book.stock > 0 ? 'In stock' : 'Out of stock'}
                </span>
                <span className="pill neutral">#{book.id}</span>
              </div>
              <h3>{book.title}</h3>
              <p className="muted">{book.author}</p>
              <div className="price-row">
                <strong>{formatMoney(book.price)}</strong>
                <span className="rating">
                  {book.rating_avg.toFixed(1)} / 5 ({book.rating_count})
                </span>
              </div>
              <div className="card-actions">
                <input
                  type="number"
                  min={1}
                  defaultValue={1}
                  className="qty"
                />
                <button
                  className="primary"
                  type="button"
                  onClick={(event) => {
                    const input =
                      event.currentTarget.parentElement?.querySelector('input')
                    const quantity = Number(
                      (input as HTMLInputElement)?.value || 1
                    )
                    onAddToCart(book.id, quantity)
                  }}
                >
                  Add to cart
                </button>
              </div>
              <div className="rate-row">
                <select defaultValue="5">
                  {[1, 2, 3, 4, 5].map((value) => (
                    <option key={value} value={value}>
                      Rate {value}
                    </option>
                  ))}
                </select>
                <button
                  className="ghost"
                  type="button"
                  onClick={(event) => {
                    const select =
                      event.currentTarget.parentElement?.querySelector('select')
                    const rating = Number(
                      (select as HTMLSelectElement)?.value || 5
                    )
                    onRateBook(book.id, rating)
                  }}
                >
                  Submit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
