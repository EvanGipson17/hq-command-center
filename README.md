# HQ — Command Center

A clean, minimal personal dashboard for organizing productivity and money-making tools. Built with Vite + React, deployed on Vercel.

---

## Run locally

```bash
npm install
npm run dev
```

Then open the URL Vite prints (usually http://localhost:5173).

To build for production:

```bash
npm run build
npm run preview
```

---

## Deploy to Vercel

**Option A — via the Vercel dashboard**

1. Push this repo to GitHub.
2. Go to [vercel.com/new](https://vercel.com/new) and import the repo.
3. Vercel auto-detects Vite. Keep the defaults and click **Deploy**.

**Option B — via the CLI**

```bash
npm install -g vercel
vercel            # first-time setup
vercel --prod     # deploy to production
```

`vercel.json` is already configured — no manual settings needed.

---

## Add a new tool

Open [`src/data/tools.js`](src/data/tools.js) and append a new object to the `TOOLS` array:

```js
{
  id: 7,                                  // unique number
  name: 'My New Tool',
  description: 'What this tool does.',
  icon: '🚀',                             // any emoji
  category: 'Productivity',               // must match categories.js
  status: 'coming-soon',                  // 'active' | 'in-progress' | 'coming-soon'
  href: '#',                              // URL or '#'
}
```

Save the file — the dashboard updates automatically.

### Status values

| status         | Badge         |
| -------------- | ------------- |
| `active`       | Live (green)  |
| `in-progress`  | In Progress (yellow) |
| `coming-soon`  | Coming Soon (gray)   |

---

## Add a new category

Open [`src/data/categories.js`](src/data/categories.js) and add the category name to the array:

```js
export const CATEGORIES = ['All', 'Finance', 'Deals', 'Research', 'Productivity', 'Health'];
```

Then reference the same string in any tool's `category` field.

---

## Project structure

```
src/
  components/
    Header.jsx       top bar with logo + status pill
    StatCards.jsx    three-up summary row
    ToolGrid.jsx     grid of tool cards + add placeholder
    ToolCard.jsx     individual tool card
    FilterBar.jsx    category filter pills
  data/
    tools.js         ← edit here to add/edit tools
    categories.js    ← edit here to add/edit categories
  pages/
    Dashboard.jsx    composes everything
  App.jsx
  main.jsx
  index.css          design tokens + all styles
```

---

## Customize the design

All design tokens live at the top of [`src/index.css`](src/index.css) under `:root`. To swap the accent from emerald to gold, change:

```css
--accent: #10b981;   /* → #d4af37 for gold */
```

Everything else updates automatically.
