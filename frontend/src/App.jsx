import './styles.css';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';

export default function App() {
  return (
    <div className="app">
      <Sidebar />
      <Dashboard />
    </div>
  );
}
