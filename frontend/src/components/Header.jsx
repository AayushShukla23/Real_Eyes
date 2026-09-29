import { Link, useLocation } from 'react-router-dom';

export default function Header() {
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <header className="border-b-4 border-black bg-[#fffdf8] sticky top-0 z-50">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center border-4 border-black bg-[#e2a100] text-base font-black shadow-[3px_3px_0_#000]">
            RE
          </div>
          <div>
            <p className="text-xl font-black tracking-tight leading-none">RealEyes</p>
            <p className="text-[10px] font-bold uppercase tracking-[0.2em] text-[#5c564c] mt-0.5">
              Forensic ML Engine
            </p>
          </div>
        </Link>

        <nav className="flex items-center gap-1 sm:gap-2">
          <Link
            to="/"
            className={`border-2 border-black px-3 py-1.5 text-xs font-black uppercase tracking-wider transition ${
              isActive('/') ? 'bg-[#141414] text-white' : 'bg-white hover:bg-[#e2a100]'
            }`}
          >
            Home
          </Link>
          <Link
            to="/app"
            className={`border-2 border-black px-3 py-1.5 text-xs font-black uppercase tracking-wider transition ${
              isActive('/app') ? 'bg-[#e2a100] text-black shadow-[2px_2px_0_#000]' : 'bg-white hover:bg-[#e2a100]'
            }`}
          >
            Workbench
          </Link>
          <Link
            to="/methodology"
            className={`border-2 border-black px-3 py-1.5 text-xs font-black uppercase tracking-wider transition ${
              isActive('/methodology') ? 'bg-[#141414] text-white' : 'bg-white hover:bg-[#e2a100]'
            }`}
          >
            Architecture
          </Link>
          <Link
            to="/about"
            className={`border-2 border-black px-3 py-1.5 text-xs font-black uppercase tracking-wider transition ${
              isActive('/about') ? 'bg-[#141414] text-white' : 'bg-white hover:bg-[#e2a100]'
            }`}
          >
            About
          </Link>
        </nav>
      </div>
    </header>
  );
}