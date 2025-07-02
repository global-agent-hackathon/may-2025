import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, User, Menu, X, MessageSquare } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { theme } = useTheme();
  const isSquidGame = theme === 'squid-game';

  const handleSignOut = async () => {
    try {
      await signOut();
      navigate('/');
    } catch (error) {
      console.error('Error signing out:', error);
    }
  };

  return (
    <nav className="glass-panel fixed top-0 w-full z-50 px-4 py-3">
      <div className="container mx-auto flex items-center justify-between">
        <Link to="/" className={cn(
          "text-xl font-semibold",
          isSquidGame ? "text-[#ed1b76]" : "text-gradient"
        )}>
          SparkVest
        </Link>
        
        <div className="hidden md:flex items-center space-x-6">
          {user ? (
            <>
              <Link to="/dashboard" className={cn(
                "transition-colors",
                isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
              )}>
                Dashboard
              </Link>
              <Link to="/market" className={cn(
                "transition-colors",
                isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
              )}>
                Market
              </Link>
              <Link to="/chat" className={cn(
                "transition-colors",
                isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
              )}>
                AI Chat
              </Link>
              <Button variant="ghost" size="icon" onClick={() => navigate('/profile')}>
                <User className={cn("h-5 w-5", isSquidGame && "text-[#037a76]")} />
              </Button>
              <Button variant="destructive" onClick={handleSignOut}>
                Sign Out
              </Button>
            </>
          ) : (
            <>
              <Link to="/about" className={cn(
                "transition-colors",
                isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
              )}>
                About
              </Link>
              <Link to="/login">
                <Button variant="secondary">Sign In</Button>
              </Link>
              <Link to="/register">
                <Button>Get Started</Button>
              </Link>
            </>
          )}
        </div>

        <button className="md:hidden" onClick={() => setIsMenuOpen(!isMenuOpen)}>
          {isMenuOpen ? (
            <X className={cn("h-6 w-6", isSquidGame && "text-[#037a76]")} />
          ) : (
            <Menu className={cn("h-6 w-6", isSquidGame && "text-[#037a76]")} />
          )}
        </button>
      </div>

      {isMenuOpen && (
        <div className="md:hidden absolute top-full left-0 right-0 glass-effect py-4 animate-fade-in">
          <div className="flex flex-col space-y-4 px-4">
            {user ? (
              <>
                <Link
                  to="/dashboard"
                  className={cn(
                    "transition-colors",
                    isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Dashboard
                </Link>
                <Link
                  to="/market"
                  className={cn(
                    "transition-colors",
                    isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Market
                </Link>
                <Link
                  to="/chat"
                  className={cn(
                    "transition-colors",
                    isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  AI Chat
                </Link>
                <Link
                  to="/profile"
                  className={cn(
                    "transition-colors",
                    isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  Profile
                </Link>
                <Button variant="destructive" onClick={handleSignOut}>
                  Sign Out
                </Button>
              </>
            ) : (
              <>
                <Link
                  to="/about"
                  className={cn(
                    "transition-colors",
                    isSquidGame ? "text-[#037a76] hover:text-[#ed1b76]" : "text-gray-300 hover:text-white"
                  )}
                  onClick={() => setIsMenuOpen(false)}
                >
                  About
                </Link>
                <Link to="/login" onClick={() => setIsMenuOpen(false)}>
                  <Button variant="secondary" className="w-full">Sign In</Button>
                </Link>
                <Link to="/register" onClick={() => setIsMenuOpen(false)}>
                  <Button className="w-full">Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
