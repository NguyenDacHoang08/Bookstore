export default function CatalogPanel() {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Catalog view</h2>
          <p>Curated shelves for fast discovery.</p>
        </div>
      </div>
      <div className="catalog-grid">
        {['New arrivals', 'Top rated', 'Staff picks', 'Seasonal', 'Indie'].map(
          (category) => (
            <div className="card" key={category}>
              <h3>{category}</h3>
              <p className="muted">
                Highlight a focused list from the catalog service.
              </p>
              <button className="ghost">Configure shelf</button>
            </div>
          )
        )}
      </div>
    </section>
  )
}
