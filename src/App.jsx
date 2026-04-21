// Root component — sets up client-side routing.
// Add new pages by adding routes here and dropping a component in src/pages/.
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard.jsx';
import FormRouter from './pages/FormRouter.jsx';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/form-router" element={<FormRouter />} />
      </Routes>
    </BrowserRouter>
  );
}
