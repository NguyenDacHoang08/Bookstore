import type { Book, Rating } from '../types'
import { formatDate } from '../utils/format'

type RatingsPanelProps = {
  books: Book[]
  ratings: Rating[]
  selectedBookId: number | null
  onSelectBook: (bookId: number) => void
  loading: boolean
}

export default function RatingsPanel({
  books,
  ratings,
  selectedBookId,
  onSelectBook,
  loading,
}: RatingsPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Ratings</h2>
          <p>Track feedback per book.</p>
        </div>
        <select
          value={selectedBookId ?? ''}
          onChange={(event) => onSelectBook(Number(event.target.value))}
        >
          {books.map((book) => (
            <option key={book.id} value={book.id}>
              {book.title}
            </option>
          ))}
        </select>
      </div>
      {loading ? (
        <div className="empty">Loading ratings...</div>
      ) : ratings.length === 0 ? (
        <div className="empty">No ratings yet.</div>
      ) : (
        <div className="stack">
          {ratings.map((rating) => (
            <div className="stack-item" key={rating.id}>
              <div>
                <strong>Rating {rating.rating}/5</strong>
                <p className="muted">
                  Customer {rating.customer_id ?? 'Anonymous'}
                </p>
              </div>
              <span className="pill neutral">Book #{rating.book_id}</span>
              <span className="muted">{formatDate(rating.created_at)}</span>
            </div>
          ))}
        </div>
      )}
    </section>
  )
}
