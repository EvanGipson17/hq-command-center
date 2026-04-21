// ToolCard — renders a single tool entry. Purely presentational;
// data comes from src/data/tools.js via the parent ToolGrid.
//
// href handling:
//   "#"           → non-clickable placeholder
//   "/something"  → internal route (uses react-router Link)
//   "https://..." → external link (opens in a new tab)
//
// Status badge mapping:
//   active       → green dot, "Live"
//   in-progress  → yellow dot, "In Progress"
//   coming-soon  → gray dot, "Coming Soon"
import { Link } from 'react-router-dom';

const STATUS_META = {
  active: { label: 'Live', className: 'badge--active' },
  'in-progress': { label: 'In Progress', className: 'badge--progress' },
  'coming-soon': { label: 'Coming Soon', className: 'badge--soon' },
};

function CardShell({ tool, children }) {
  const href = tool.href;

  if (!href || href === '#') {
    return <div className="card">{children}</div>;
  }
  if (href.startsWith('/')) {
    return <Link to={href} className="card">{children}</Link>;
  }
  return (
    <a className="card" href={href} target="_blank" rel="noopener noreferrer">
      {children}
    </a>
  );
}

export default function ToolCard({ tool }) {
  const status = STATUS_META[tool.status] ?? STATUS_META['coming-soon'];

  return (
    <CardShell tool={tool}>
      <div className="card__head">
        <div className="card__icon" aria-hidden="true">{tool.icon}</div>
        <div className="card__category">{tool.category}</div>
      </div>

      <div className="card__name">{tool.name}</div>
      <div className="card__desc">{tool.description}</div>

      <div className="card__foot">
        <span className={`badge ${status.className}`}>
          <span className="badge__dot" />
          {status.label}
        </span>
        <span className="card__arrow">→</span>
      </div>
    </CardShell>
  );
}
