export default function Header() {
  return (
    <header className="bg-card shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-6">
          <h1 className="text-2xl font-bold text-accent">TripCraft AI</h1>
          <button className="rounded-md bg-primary px-4 py-2 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90">
            Get Started
          </button>
        </div>
      </div>
    </header>
  );
}
