import type { Book } from '../types'
import { formatMoney } from '../utils/format'

type RecommendPanelProps = {
  books: Book[]
}

export default function RecommendPanel({ books }: RecommendPanelProps) {
  const topBooks = [...books]
    .sort((a, b) => b.rating_avg - a.rating_avg)
    .slice(0, 3)

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Recommendations</h2>
          <p>AI-inspired suggestions based on ratings.</p>
        </div>
      </div>
      <div className="grid">
        {topBooks.map((book) => (
          <div className="card" key={book.id}>
            <span className="pill good">Top pick</span>
            <h3>{book.title}</h3>
            <p className="muted">{book.author}</p>
            <div className="price-row">
              <strong>{formatMoney(book.price)}</strong>
              <span className="rating">{book.rating_avg.toFixed(1)} / 5</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  )
}
