import type { Dispatch, SetStateAction } from 'react'
import type { Book, BookDraft } from '../types'
import { formatMoney } from '../utils/format'

type StaffPanelProps = {
  books: Book[]
  newBook: BookDraft
  setNewBook: Dispatch<SetStateAction<BookDraft>>
  onCreateBook: () => void
  onRefresh: () => void
  onStartEdit: (book: Book) => void
  onDeleteBook: (bookId: number) => void
  editBookId: number | null
  editBook: BookDraft
  setEditBook: Dispatch<SetStateAction<BookDraft>>
  onSaveEdit: () => void
  onCloseEdit: () => void
}

export default function StaffPanel({
  books,
  newBook,
  setNewBook,
  onCreateBook,
  onRefresh,
  onStartEdit,
  onDeleteBook,
  editBookId,
  editBook,
  setEditBook,
  onSaveEdit,
  onCloseEdit,
}: StaffPanelProps) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Staff console</h2>
          <p>Create, update, and remove books.</p>
        </div>
        <button className="ghost" onClick={onRefresh}>
          Refresh
        </button>
      </div>

      <div className="split">
        <div className="card">
          <h3>Add new book</h3>
          <label>
            Title
            <input
              value={newBook.title}
              onChange={(event) =>
                setNewBook((current) => ({
                  ...current,
                  title: event.target.value,
                }))
              }
            />
          </label>
          <label>
            Author
            <input
              value={newBook.author}
              onChange={(event) =>
                setNewBook((current) => ({
                  ...current,
                  author: event.target.value,
                }))
              }
            />
          </label>
          <label>
            Price
            <input
              type="number"
              value={newBook.price}
              onChange={(event) =>
                setNewBook((current) => ({
                  ...current,
                  price: event.target.value,
                }))
              }
            />
          </label>
          <label>
            Stock
            <input
              type="number"
              value={newBook.stock}
              onChange={(event) =>
                setNewBook((current) => ({
                  ...current,
                  stock: event.target.value,
                }))
              }
            />
          </label>
          <button className="primary" onClick={onCreateBook}>
            Create book
          </button>
        </div>
        <div className="card">
          <h3>Inventory actions</h3>
          <div className="stack">
            {books.map((book) => (
              <div className="stack-item" key={book.id}>
                <div>
                  <strong>{book.title}</strong>
                  <p className="muted">{book.author}</p>
                </div>
                <div className="badge-group">
                  <span className="pill neutral">{formatMoney(book.price)}</span>
                  <span className={`pill ${book.stock > 0 ? 'good' : 'bad'}`}>
                    Stock {book.stock}
                  </span>
                </div>
                <div className="row-actions">
                  <button className="ghost" onClick={() => onStartEdit(book)}>
                    Edit
                  </button>
                  <button className="danger" onClick={() => onDeleteBook(book.id)}>
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {editBookId && (
        <div className="modal">
          <div className="modal-card">
            <div className="modal-header">
              <h3>Edit book</h3>
              <button className="ghost" onClick={onCloseEdit}>
                Close
              </button>
            </div>
            <div className="modal-grid">
              <label>
                Title
                <input
                  value={editBook.title}
                  onChange={(event) =>
                    setEditBook((current) => ({
                      ...current,
                      title: event.target.value,
                    }))
                  }
                />
              </label>
              <label>
                Author
                <input
                  value={editBook.author}
                  onChange={(event) =>
                    setEditBook((current) => ({
                      ...current,
                      author: event.target.value,
                    }))
                  }
                />
              </label>
              <label>
                Price
                <input
                  type="number"
                  value={editBook.price}
                  onChange={(event) =>
                    setEditBook((current) => ({
                      ...current,
                      price: event.target.value,
                    }))
                  }
                />
              </label>
              <label>
                Stock
                <input
                  type="number"
                  value={editBook.stock}
                  onChange={(event) =>
                    setEditBook((current) => ({
                      ...current,
                      stock: event.target.value,
                    }))
                  }
                />
              </label>
            </div>
            <div className="modal-actions">
              <button className="primary" onClick={onSaveEdit}>
                Save changes
              </button>
            </div>
          </div>
        </div>
      )}
    </section>
  )
}
