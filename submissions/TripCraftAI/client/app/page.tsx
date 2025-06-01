import { Heart, Star, Users } from "lucide-react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

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
            <Button size="lg">Get Started</Button>
            <Button variant="ghost" size="lg">
              Learn More <span aria-hidden="true">→</span>
            </Button>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="mt-20 grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mb-4">
                <Star className="w-6 h-6 text-secondary-foreground" />
              </div>
              <CardTitle className="text-lg">Premium Quality</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Experience the best with our carefully curated selection of
                premium features and services.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mb-4">
                <Users className="w-6 h-6 text-secondary-foreground" />
              </div>
              <CardTitle className="text-lg">Community Driven</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Join a vibrant community of like-minded individuals sharing
                experiences and insights.
              </CardDescription>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-center justify-center w-12 h-12 bg-secondary rounded-lg mb-4">
                <Heart className="w-6 h-6 text-secondary-foreground" />
              </div>
              <CardTitle className="text-lg">Made with Love</CardTitle>
            </CardHeader>
            <CardContent>
              <CardDescription>
                Every detail is crafted with care to provide you with the best
                possible experience.
              </CardDescription>
            </CardContent>
          </Card>
        </div>
      </main>

      <Footer />
    </div>
  );
}
