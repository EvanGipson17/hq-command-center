// ------------------------------------------------------------------
// TOOLS — the single source of truth for every tool shown on the dashboard.
// ------------------------------------------------------------------
// HOW TO ADD A NEW TOOL:
//   1. Copy one of the objects below.
//   2. Paste it at the bottom of the TOOLS array.
//   3. Give it a new unique `id` (just increment the number).
//   4. Fill in name, description, icon (any emoji), category, status, href.
//
// Fields:
//   id          → unique number
//   name        → short tool name (shown as the card title)
//   description → one sentence describing what the tool does
//   icon        → any emoji, renders as the card icon
//   category    → must match one of the strings in ./categories.js
//   status      → "active" | "in-progress" | "coming-soon"
//   href        → URL the card links to. Use "#" for placeholders.
// ------------------------------------------------------------------

export const TOOLS = [
  {
    id: 1,
    name: 'Investment Scout',
    description: 'Scrape market data and surface investment opportunities with AI analysis.',
    icon: '📈',
    category: 'Finance',
    status: 'coming-soon',
    href: '#',
  },
  {
    id: 3,
    name: 'Market Pulse',
    description: 'Daily snapshot of trending stocks, crypto, and macro signals.',
    icon: '💹',
    category: 'Finance',
    status: 'coming-soon',
    href: '#',
  },
  {
    id: 4,
    name: 'Deal Alerts',
    description: 'Set price targets and get notified when deals hit your threshold.',
    icon: '🔔',
    category: 'Deals',
    status: 'coming-soon',
    href: '#',
  },
  {
    id: 5,
    name: 'Research Assistant',
    description: 'Deep-dive research on any topic with sourced summaries.',
    icon: '🔍',
    category: 'Research',
    status: 'coming-soon',
    href: '#',
  },
  {
    id: 6,
    name: 'Prompt Library',
    description: 'Your personal collection of high-performance AI prompts.',
    icon: '📚',
    category: 'Productivity',
    status: 'coming-soon',
    href: '#',
  },
  {
    id: 7,
    name: 'Form Router',
    description: 'Auto-responds to Google Forms intake with personalized setup steps. Runs on Manus as a scheduled cron every 3 days.',
    icon: '📬',
    category: 'Automation',
    status: 'active',
    href: '/form-router',
  },
];
