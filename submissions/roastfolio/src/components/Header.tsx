// src/components/Header.tsx
import { ScanText } from "lucide-react"; // A more neutral icon

export const Header = () => {
  return (
    <header className="text-center mb-12 md:mb-16">
      {/* Optional: Small "Learn About" badge like Exa's */}
      {/* <div className="flex justify-center mb-4">
        <a href="#" className="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full hover:bg-blue-200 transition-colors">
          Learn About Portfolio Roaster AI ✨
        </a>
      </div> */}
      <div className="flex items-center justify-center gap-2.5 mb-3">
        {/* <ScanText className="w-8 h-8 text-blue-600" /> */}
        <h1 className="text-4xl md:text-5xl font-bold text-slate-800 tracking-tight">
          Your Portfolio <span className="text-blue-600">Roasted</span>
        </h1>
      </div>
      <p className="text-md md:text-lg text-slate-600 max-w-xl mx-auto">
        Our AI analyzes your portfolio and gives you a brutally honest (but fun) recap.
      </p>
    </header>
  );
};