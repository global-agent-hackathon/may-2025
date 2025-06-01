import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Header() {
  return (
    <header className="bg-card shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <Link href="/" className="hover:opacity-80 transition-opacity">
            <h1 className="text-2xl font-bold text-accent">TripCraft AI</h1>
          </Link>
          <Link href="/plan">
            <Button className="bg-primary hover:bg-primary/90">
              Get Started
            </Button>
          </Link>
        </div>
      </div>
    </header>
  );
}
