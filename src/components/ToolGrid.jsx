// ToolGrid — renders the filtered list of tool cards plus a trailing
// "Add Tool" placeholder card. The Dashboard does the filtering and
// passes the already-filtered tools in via props.
import ToolCard from './ToolCard.jsx';

export default function ToolGrid({ tools }) {
  return (
    <div className="grid">
      {tools.length === 0 ? (
        <div className="empty">No tools in this category yet.</div>
      ) : (
        tools.map((tool) => <ToolCard key={tool.id} tool={tool} />)
      )}

      {/* Placeholder card. Clicking does nothing — it's a visual cue that
          you add new tools by editing src/data/tools.js. */}
      <div className="card card--add" role="note">
        <div>
          <div className="card--add__plus">+</div>
          <div className="card--add__label">Add Tool</div>
        </div>
      </div>
    </div>
  );
}
