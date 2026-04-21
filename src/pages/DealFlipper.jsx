// DealFlipper — single-tool page at /deal-flipper.
// Reads scan results from /deal-flipper-results.json (or the local
// Flask API if it's running) and triggers manual scans.
import { useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';

const API = 'http://localhost:5001';

// Python scheduler fires at 07:45 and 18:45 local time.
const SCHEDULE_HOURS = [[7, 45], [18, 45]];

function nextScheduledRun() {
  const now = new Date();
  const candidates = [];
  for (const dayOffset of [0, 1]) {
    for (const [h, m] of SCHEDULE_HOURS) {
      const d = new Date(now);
      d.setDate(d.getDate() + dayOffset);
      d.setHours(h, m, 0, 0);
      if (d > now) candidates.push(d);
    }
  }
  candidates.sort((a, b) => a - b);
  return candidates[0];
}

function fmt(unixSec) {
  if (!unixSec) return '—';
  return new Date(unixSec * 1000).toLocaleString(undefined, {
    dateStyle: 'medium',
    timeStyle: 'short',
  });
}

export default function DealFlipper() {
  const [data, setData] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState(null);

  async function refresh() {
    try {
      const res = await fetch(`${API}/api/results`, { cache: 'no-store' });
      if (!res.ok) throw new Error();
      setData(await res.json());
      return;
    } catch { /* fall through to static */ }
    try {
      const res = await fetch('/deal-flipper-results.json', { cache: 'no-store' });
      setData(await res.json());
    } catch {
      setError('Could not load results.');
    }
  }

  useEffect(() => { refresh(); }, []);

  async function triggerScan() {
    setError(null);
    setScanning(true);
    try {
      const res = await fetch(`${API}/api/scan`, { method: 'POST' });
      if (!res.ok && res.status !== 409) throw new Error();
      const deadline = Date.now() + 5 * 60 * 1000;
      while (Date.now() < deadline) {
        await new Promise((r) => setTimeout(r, 5000));
        const h = await fetch(`${API}/api/health`).then((r) => r.json()).catch(() => null);
        if (h && !h.scan_running) break;
      }
      await refresh();
    } catch {
      setError(
        'Local scan server not reachable. Start it with:\n  cd src/tools/deal-flipper\n  python server.py'
      );
    } finally {
      setScanning(false);
    }
  }

  const next = useMemo(() => nextScheduledRun(), []);
  const local = (data?.deals ?? []).filter((d) => d.is_local);
  const shipped = (data?.deals ?? []).filter((d) => !d.is_local);

  return (
    <div className="page">
      <div className="container">
        <header className="header">
          <div className="header__brand">
            <div className="header__logo">🔄</div>
            <div>
              <div className="header__title">Deal Flipper</div>
              <div className="header__subtitle">Multi-Source Arbitrage Scanner</div>
            </div>
          </div>
          <Link to="/" className="status-pill">
            <span className="status-pill__dot" />
            ← Back to HQ
          </Link>
        </header>

        <div className="stats">
          <div className="stat">
            <div className="stat__label">Flips Found</div>
            <div className="stat__value stat__value--accent">
              {String(data?.deal_count ?? 0).padStart(2, '0')}
            </div>
          </div>
          <div className="stat">
            <div className="stat__label">Last Scan</div>
            <div className="stat__value" style={{ fontSize: 16 }}>{fmt(data?.scanned_at)}</div>
          </div>
          <div className="stat">
            <div className="stat__label">Next Scan</div>
            <div className="stat__value" style={{ fontSize: 16 }}>
              {next.toLocaleString(undefined, { weekday: 'short', hour: 'numeric', minute: '2-digit' })}
            </div>
          </div>
        </div>

        <div className="filterbar">
          <button
            className={`filter ${scanning ? '' : 'filter--active'}`}
            onClick={triggerScan}
            disabled={scanning}
          >
            {scanning ? 'Scanning…' : 'Run Manual Scan'}
          </button>
          <button className="filter" onClick={refresh} disabled={scanning}>
            Refresh
          </button>
        </div>

        {error && (
          <div className="empty" style={{ marginBottom: 14, whiteSpace: 'pre-wrap' }}>{error}</div>
        )}

        {local.length > 0 && <SectionHeader>Austin Local Pickup</SectionHeader>}
        <div className="grid">
          {local.map((d, i) => <DealCard key={`l-${i}`} deal={d} />)}
        </div>

        {shipped.length > 0 && <SectionHeader>Shipped Nationwide</SectionHeader>}
        <div className="grid">
          {shipped.map((d, i) => <DealCard key={`s-${i}`} deal={d} />)}
        </div>

        {(!data || data.deals.length === 0) && (
          <div className="empty">
            {data?.scanned_at
              ? 'No confident flips found in the last scan.'
              : 'No scan has run yet. Click “Run Manual Scan.”'}
          </div>
        )}

        {data?.site_status && Object.keys(data.site_status).length > 0 && (
          <>
            <SectionHeader>Source Status</SectionHeader>
            <SourceStatusTable status={data.site_status} />
          </>
        )}
      </div>
    </div>
  );
}

function SectionHeader({ children }) {
  return (
    <div className="stat__label" style={{ margin: '28px 0 10px' }}>{children}</div>
  );
}

function DealCard({ deal }) {
  const confColor = deal.confidence === 'HIGH' ? 'var(--accent)' : '#eab308';
  return (
    <a className="card" href={deal.buy_url} target="_blank" rel="noopener noreferrer">
      <div className="card__head">
        <div className="card__icon" aria-hidden="true">
          {deal.kind === 'bundle' ? '📦' : '💰'}
        </div>
        <div className="card__category" style={{ color: confColor }}>
          {deal.source} · {deal.confidence}
        </div>
      </div>

      <div className="card__name" style={{ fontSize: 14 }}>{deal.title}</div>

      <div style={{ fontFamily: 'var(--font-mono)', fontSize: 12,
                    color: 'var(--text-dim)', lineHeight: 1.8, marginBottom: 10 }}>
        <div>Buy: <span style={{ color: 'var(--text)' }}>${deal.buy_price.toFixed(2)}</span></div>
        <div>Sell: <span style={{ color: 'var(--text)' }}>${deal.sell_price.toFixed(2)}</span></div>
        <div>Profit:{' '}
          <span style={{ color: 'var(--accent)', fontWeight: 600 }}>
            ${deal.profit.toFixed(2)} ({deal.margin_pct.toFixed(0)}%)
          </span>
        </div>
        <div style={{ color: 'var(--text-muted)' }}>
          {deal.sold_samples} sold comps · match {Math.round(deal.match_score * 100)}%
        </div>
        {deal.note && <div style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>{deal.note}</div>}
      </div>

      <div className="card__foot">
        <span className="badge badge--active">
          <span className="badge__dot" />
          {deal.is_local ? 'LOCAL PICKUP — AUSTIN' : 'Ships'}
        </span>
        <span className="card__arrow">→</span>
      </div>
    </a>
  );
}

function SourceStatusTable({ status }) {
  return (
    <div style={{ border: '1px solid var(--border)', borderRadius: 10,
                  background: 'var(--bg-card)', padding: 8 }}>
      {Object.entries(status).map(([name, info]) => (
        <div key={name} style={{ display: 'flex', justifyContent: 'space-between',
                                  padding: '8px 12px', fontSize: 12,
                                  fontFamily: 'var(--font-mono)',
                                  borderBottom: '1px solid var(--border)' }}>
          <span>{name}</span>
          <span style={{ color: info.status === 'ok' ? 'var(--accent)' : 'var(--text-muted)' }}>
            {info.status} · {info.candidates} listings
          </span>
        </div>
      ))}
    </div>
  );
}
