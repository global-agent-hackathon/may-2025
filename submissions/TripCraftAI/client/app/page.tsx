import { Heart, Star, Users } from "lucide-react";
import Header from "./components/Header";
import Footer from "./components/Footer";

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      <Header />

      {/* Hero Section */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center">
          <h2 className="text-4xl font-bold sm:text-6xl">
            Welcome to <span className="text-accent">TripCraft AI</span>
          </h2>
          <p className="mt-6 text-lg leading-8 text-secondary-foreground max-w-2xl mx-auto">
            Discover amazing experiences and create unforgettable memories with
            our AI-powered platform.
          </p>
          <div className="mt-10 flex items-center justify-center gap-x-6">
            <button className="rounded-md bg-primary px-3.5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm hover:bg-primary/90">
              Get Started
            </button>
            <button className="text-sm font-semibold leading-6 text-primary">
              Learn More <span aria-hidden="true">→</span>
            </button>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <div className="bg-card rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mb-4">
              <Star className="w-6 h-6 text-secondary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">
              Premium Quality
            </h3>
            <p className="text-secondary-foreground">
              Experience the best with our carefully curated selection of
              premium features and services.
            </p>
          </div>

          <div className="bg-card rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mb-4">
              <Users className="w-6 h-6 text-secondary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">
              Community Driven
            </h3>
            <p className="text-secondary-foreground">
              Join a vibrant community of like-minded individuals sharing
              experiences and insights.
            </p>
          </div>

          <div className="bg-card rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
            <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mb-4">
              <Heart className="w-6 h-6 text-secondary-foreground" />
            </div>
            <h3 className="text-lg font-semibold text-primary mb-2">
              Made with Love
            </h3>
            <p className="text-secondary-foreground">
              Every detail is crafted with care to provide you with the best
              possible experience.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
