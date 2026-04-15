// Header — top bar with the HQ logo, title, and "System Online" status pill.
export default function Header() {
  return (
    <header className="header">
      <div className="header__brand">
        <div className="header__logo">HQ</div>
        <div>
          <div className="header__title">Command Center</div>
          <div className="header__subtitle">Personal Operations Hub</div>
        </div>
      </div>

      <div className="status-pill">
        <span className="status-pill__dot" />
        System Online
      </div>
    </header>
  );
}
