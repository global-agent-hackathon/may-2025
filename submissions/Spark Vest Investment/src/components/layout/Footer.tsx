import { Link } from 'react-router-dom';
import { Github, Twitter, Linkedin } from 'lucide-react';
import { useTheme } from '@/hooks/useTheme';
import { cn } from '@/lib/utils';

const Footer = () => {
  const { theme } = useTheme();
  const isSquidGame = theme === 'squid-game';

  return (
    <footer className="mt-auto py-8 border-t border-border/40">
      <div className="container px-4 mx-auto">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div className="space-y-3">
            <h3 className={cn(
              "text-lg font-semibold",
              isSquidGame && "text-[#ed1b76]"
            )}>Spark Vest</h3>
            <p className={cn(
              "text-sm text-muted-foreground",
              isSquidGame && "text-[#037a76]"
            )}>
              Making investments smarter with AI-powered insights.
            </p>
          </div>
          
          <div>
            <h3 className={cn(
              "font-semibold mb-3",
              isSquidGame && "text-[#ed1b76]"
            )}>Quick Links</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/about" className={cn(
                  "text-sm text-muted-foreground hover:text-primary",
                  isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
                )}>
                  About Us
                </Link>
              </li>
              <li>
                <Link to="/market" className={cn(
                  "text-sm text-muted-foreground hover:text-primary",
                  isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
                )}>
                  Market
                </Link>
              </li>
              <li>
                <Link to="/portfolio" className={cn(
                  "text-sm text-muted-foreground hover:text-primary",
                  isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
                )}>
                  Portfolio
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className={cn(
              "font-semibold mb-3",
              isSquidGame && "text-[#ed1b76]"
            )}>Legal</h3>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy" className={cn(
                  "text-sm text-muted-foreground hover:text-primary",
                  isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
                )}>
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms" className={cn(
                  "text-sm text-muted-foreground hover:text-primary",
                  isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
                )}>
                  Terms of Service
                </Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className={cn(
              "font-semibold mb-3",
              isSquidGame && "text-[#ed1b76]"
            )}>Connect</h3>
            <div className="flex space-x-4">
              <a href="https://github.com/yashksaini-coder" className={cn(
                "text-muted-foreground hover:text-primary",
                isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
              )}>
                <Github className="h-5 w-5" />
              </a>
              <a href="https://x.com/yash_k_saini" className={cn(
                "text-muted-foreground hover:text-primary",
                isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
              )}>
                <Twitter className="h-5 w-5" />
              </a>
              <a href="https://www.linkedin.com/in/yashksaini/" className={cn(
                "text-muted-foreground hover:text-primary",
                isSquidGame && "text-[#037a76] hover:text-[#ed1b76]"
              )}>
                <Linkedin className="h-5 w-5" />
              </a>
            </div>
          </div>
        </div>
        
        <div className="mt-8 pt-4 border-t border-border/40">
          <p className={cn(
            "text-center text-sm text-muted-foreground",
            isSquidGame && "text-[#037a76]"
          )}>
            © {new Date().getFullYear()} Spark Vest. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
