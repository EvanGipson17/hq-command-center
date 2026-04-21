// FormRouter — single-tool page at /form-router.
// Hub page for the eg-form-router Python script — shows links to the
// GitHub repo, the three Google Forms it ties into, and the current
// deployment location.
//
// Some URLs are stubbed with TODO markers. Replace them with the real
// URLs when you pull them from Google Drive.
import { Link } from 'react-router-dom';

// TODO: pull real URLs from Google Drive when you have time.
const LINKS = [
  {
    id: 'repo',
    icon: '📦',
    name: 'GitHub Repo',
    description: 'Source code, README, deployment docs.',
    href: 'https://github.com/EvanGipson17/eg-form-router',
    kind: 'ready',
  },
  {
    id: 'intake',
    icon: '📝',
    name: 'Live Intake Form',
    description: 'The short yes/no form clients fill out first.',
    href: null, // TODO: paste the public /viewform URL for the Intake form
    kind: 'todo',
  },
  {
    id: 'basic',
    icon: '🧾',
    name: 'Basic Plan Form',
    description: 'Entry point for the $150/mo Basic plan sign-up.',
    href: null, // TODO: paste the Basic Plan form URL
    kind: 'todo',
  },
  {
    id: 'full',
    icon: '🗂️',
    name: 'Full Setup Portal',
    description: 'Detailed form sent to clients after the intake router fires.',
    href: 'https://docs.google.com/forms/d/e/1FAIpQLSdEohGvs6ruK-zK7V_uZuwK3FFYk27MzguGZ-I-O2FDPXALLA/viewform',
    kind: 'ready',
  },
];

const DEPLOYMENT = 'Manus — scheduled cron, every 3 days';

const DESCRIPTION =
  'Automated Google Forms response router. When a client fills out the intake form, ' +
  'this Python script reads their answers and sends a personalized follow-up email ' +
  'with only the access-setup steps for the tools they actually use (Gmail delegation, ' +
  'Facebook admin, Google Sheets, etc). Uses Gmail SMTP with an App Password — fully ' +
  'headless, no OAuth prompts. State tracked in router_state.json to prevent duplicate sends.';

export default function FormRouter() {
  return (
    <div className="page">
      <div className="container">
        <header className="header">
          <div className="header__brand">
            <div className="header__logo">📬</div>
            <div>
              <div className="header__title">Form Router</div>
              <div className="header__subtitle">Google Forms → Personalized Onboarding Email</div>
            </div>
          </div>
          <Link to="/" className="status-pill">
            <span className="status-pill__dot" />
            ← Back to HQ
          </Link>
        </header>

        <div className="stats">
          <div className="stat">
            <div className="stat__label">Status</div>
            <div className="stat__value" style={{ fontSize: 16 }}>Active</div>
          </div>
          <div className="stat">
            <div className="stat__label">Deployment</div>
            <div className="stat__value" style={{ fontSize: 14 }}>{DEPLOYMENT}</div>
          </div>
          <div className="stat">
            <div className="stat__label">Repo</div>
            <div className="stat__value" style={{ fontSize: 14 }}>EvanGipson17/eg-form-router</div>
          </div>
        </div>

        <div
          className="empty"
          style={{
            marginBottom: 18,
            textAlign: 'left',
            whiteSpace: 'normal',
            lineHeight: 1.55,
          }}
        >
          {DESCRIPTION}
        </div>

        <div className="stat__label" style={{ margin: '28px 0 10px' }}>Links</div>
        <div className="grid">
          {LINKS.map((l) => <LinkCard key={l.id} link={l} />)}
        </div>
      </div>
    </div>
  );
}

function LinkCard({ link }) {
  const isTodo = link.kind === 'todo' || !link.href;
  const commonInner = (
    <>
      <div className="card__head">
        <div className="card__icon" aria-hidden="true">{link.icon}</div>
        <div className="card__category" style={{ color: isTodo ? '#eab308' : 'var(--accent)' }}>
          {isTodo ? 'TODO: paste URL' : 'Open in new tab'}
        </div>
      </div>
      <div className="card__name" style={{ fontSize: 14 }}>{link.name}</div>
      <div
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: 12,
          color: 'var(--text-dim)',
          lineHeight: 1.6,
          marginBottom: 10,
        }}
      >
        {link.description}
      </div>
      <div className="card__foot">
        <span className={`badge ${isTodo ? '' : 'badge--active'}`}>
          {!isTodo && <span className="badge__dot" />}
          {isTodo ? 'NEEDS URL' : 'READY'}
        </span>
        <span className="card__arrow">→</span>
      </div>
    </>
  );

  if (isTodo) {
    return (
      <div className="card" style={{ opacity: 0.75, cursor: 'not-allowed' }}>
        {commonInner}
      </div>
    );
  }

  return (
    <a className="card" href={link.href} target="_blank" rel="noopener noreferrer">
      {commonInner}
    </a>
  );
}
