// FilterBar — horizontal row of category pills. Clicking one sets the
// active filter in the parent (Dashboard). Driven entirely by the
// CATEGORIES array in src/data/categories.js.
export default function FilterBar({ categories, active, onChange }) {
  return (
    <div className="filterbar">
      {categories.map((cat) => (
        <button
          key={cat}
          className={`filter ${active === cat ? 'filter--active' : ''}`}
          onClick={() => onChange(cat)}
        >
          {cat}
        </button>
      ))}
    </div>
  );
}
