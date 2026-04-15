// Dashboard — the only page in V1. Composes Header, StatCards, FilterBar,
// and ToolGrid. Owns the `activeCategory` state used to filter tools.
import { useMemo, useState } from 'react';
import Header from '../components/Header.jsx';
import StatCards from '../components/StatCards.jsx';
import FilterBar from '../components/FilterBar.jsx';
import ToolGrid from '../components/ToolGrid.jsx';
import { TOOLS } from '../data/tools.js';
import { CATEGORIES } from '../data/categories.js';

export default function Dashboard() {
  const [activeCategory, setActiveCategory] = useState('All');

  // Filter tools whenever the active category changes.
  const filteredTools = useMemo(() => {
    if (activeCategory === 'All') return TOOLS;
    return TOOLS.filter((t) => t.category === activeCategory);
  }, [activeCategory]);

  return (
    <div className="page">
      <div className="container">
        <Header />
        <StatCards tools={TOOLS} categories={CATEGORIES} />
        <FilterBar
          categories={CATEGORIES}
          active={activeCategory}
          onChange={setActiveCategory}
        />
        <ToolGrid tools={filteredTools} />
      </div>
    </div>
  );
}
