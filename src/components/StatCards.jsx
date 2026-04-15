// StatCards — three-up row showing summary counts derived from tools data.
// Takes { tools, categories } and computes counts on the fly, so the stats
// stay in sync automatically as you edit tools.js.
export default function StatCards({ tools, categories }) {
  const active = tools.filter((t) => t.status === 'active').length;
  const queued = tools.filter(
    (t) => t.status === 'in-progress' || t.status === 'coming-soon'
  ).length;
  // Exclude "All" from the category count — it's a filter, not a real category.
  const categoryCount = categories.filter((c) => c !== 'All').length;

  return (
    <div className="stats">
      <Stat label="Tools Active" value={active} accent />
      <Stat label="Tools In Queue" value={queued} />
      <Stat label="Categories" value={categoryCount} />
    </div>
  );
}

function Stat({ label, value, accent }) {
  return (
    <div className="stat">
      <div className="stat__label">{label}</div>
      <div className={`stat__value ${accent ? 'stat__value--accent' : ''}`}>
        {String(value).padStart(2, '0')}
      </div>
    </div>
  );
}
