import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import WorkbenchPage from './pages/WorkbenchPage';
import MethodologyPage from './pages/MethodologyPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen flex flex-col font-sans">
        <Header />
        <div className="flex-1">
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/app" element={<WorkbenchPage />} />
            <Route path="/methodology" element={<MethodologyPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </div>
        <footer className="border-t-4 border-black bg-[#fffdf8] py-4 text-center text-xs font-black uppercase tracking-wider">
          RealEyes Engine v1.0.0 • Portfolio Grade System
        </footer>
      </div>
    </BrowserRouter>
  );
}