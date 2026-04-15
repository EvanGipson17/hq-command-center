// ToolCard — renders a single tool entry. Purely presentational;
// data comes from src/data/tools.js via the parent ToolGrid.
//
// Status badge mapping:
//   active       → green dot, "Live"
//   in-progress  → yellow dot, "In Progress"
//   coming-soon  → gray dot, "Coming Soon"

const STATUS_META = {
  active: { label: 'Live', className: 'badge--active' },
  'in-progress': { label: 'In Progress', className: 'badge--progress' },
  'coming-soon': { label: 'Coming Soon', className: 'badge--soon' },
};

export default function ToolCard({ tool }) {
  const status = STATUS_META[tool.status] ?? STATUS_META['coming-soon'];
  // If the tool is just a placeholder (#), render a non-navigating card.
  const isPlaceholder = !tool.href || tool.href === '#';
  const Tag = isPlaceholder ? 'div' : 'a';

  return (
    <Tag
      className="card"
      href={isPlaceholder ? undefined : tool.href}
      target={isPlaceholder ? undefined : '_blank'}
      rel={isPlaceholder ? undefined : 'noopener noreferrer'}
    >
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
    </Tag>
  );
}
