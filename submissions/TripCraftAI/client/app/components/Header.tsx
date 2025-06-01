import { Button } from "@/components/ui/button";

export default function Header() {
  return (
    <header className="bg-card shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <h1 className="text-2xl font-bold text-accent">TripCraft AI</h1>
          <Button>Get Started</Button>
        </div>
      </div>
    </header>
  );
}
