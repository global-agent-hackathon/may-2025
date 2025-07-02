import { ReactNode, useState, useEffect } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { Button } from '@/components/ui/button';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  const [theme, setTheme] = useState(() => 
    localStorage.getItem('theme') || 'default'
  );

  const toggleTheme = () => {
    const newTheme = theme === 'default' ? 'squid-game' : 'default';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    document.documentElement.setAttribute('data-theme', newTheme);
  };

  useEffect(() => {
    // Set initial theme
    document.documentElement.setAttribute('data-theme', theme);
  }, []);

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Navbar />
      <main className="flex-1 pt-16 container mx-auto px-4">
        {children}
      </main>
      {/* <Button 
        onClick={toggleTheme}
        className="theme-toggle"
        aria-label="Toggle theme"
      >
        {theme === 'default' ? '🦑' : '🌙'}
      </Button> */}
      <Footer />
    </div>
  );
};

export default Layout;
