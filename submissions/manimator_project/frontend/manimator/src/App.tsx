import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import ChatPage from './ChatPage';
import ManimatorPage from './LandingPage';

// Default export for the App component
export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<ManimatorPage />} />
        <Route path="/chat/:sessionId" element={<ChatPage />} />
      </Routes>
    </Router>
  );
}
