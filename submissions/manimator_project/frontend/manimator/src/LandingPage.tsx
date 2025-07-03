"use client";

import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Separator } from "@/components/ui/separator";
import { useNavigate } from 'react-router-dom';
import { v4 as uuidv4 } from 'uuid';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import {
  Menu,
  Paperclip,
  Sparkles,
  SendHorizonal,
  PlusCircle,
  Github,
  Twitter,
  Linkedin,
  ExternalLink,
  Search,
  Settings,
  Users,
  BarChart,
} from "lucide-react";

// Project Card
function ProjectCard({
    name,
    editedTime,
    imageUrl = "https://ui.shadcn.com/placeholder.svg",
    avatarUrl = "https://github.com/shadcn.png",
  }: {
    name: string;
    editedTime: string;
    imageUrl?: string;
    avatarUrl?: string;
  }) {
    return (
      <div className="flex flex-col gap-4">
        {/* Replace next/image with native <img> */}
        <img
          src={imageUrl}
          alt={name}
          width={280}
          height={159}
          className="rounded-lg object-cover aspect-[280/159]"
          loading="lazy"
        />
  
        <div className="flex items-center gap-2">
          <Avatar>
            <AvatarImage src={avatarUrl} alt={name} />
            <AvatarFallback>{name.substring(0, 2)}</AvatarFallback>
          </Avatar>
          <div className="flex flex-col">
            <p className="text-sm font-medium text-foreground">{name}</p>
            <p className="text-xs text-muted-foreground">{editedTime}</p>
          </div>
        </div>
      </div>
    );
  }

// Suggestion Button
function SuggestionButton({ icon, text, onClick }: { icon: React.ReactNode; text: string; onClick: () => void }) {
  return (
    <Button
      variant="outline"
      className="rounded-full h-auto px-3 py-1.5 text-xs bg-muted border-card hover:bg-muted/80 text-foreground flex items-center gap-1.5"
      onClick={onClick}
    >
      {icon}
      {text}
    </Button>
  );
}

// Header Component
function Header({ onMobileMenuToggle }: { onMobileMenuToggle: (value: boolean) => void }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 max-w-screen-2xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <a href="#" className="mr-6 flex items-center space-x-2">
          <span className="font-bold text-[42px] leading-[1.3] text-foreground" style={{ fontFamily: 'Pixelify Sans', fontSize: '3.36em' }}>M</span>
        </a>
        <div className="hidden md:flex items-center gap-3">
          <Button variant="outline" size="sm" onClick={() => console.log("Sign In clicked")}>Sign In</Button>
          <Button size="sm" onClick={() => console.log("Sign Up clicked")}>Sign Up</Button>
        </div>
        <div className="md:hidden">
          <MobileMenu onToggle={onMobileMenuToggle} />
        </div>
      </div>
    </header>
  );
}

// Mobile Menu
function MobileMenu({ onToggle }: { onToggle: (open: boolean) => void }) {
  const navLinks = [
    { label: "Sign In", href: "#" },
    { label: "Sign Up", href: "#" },
  ];

  return (
    <Sheet onOpenChange={onToggle}>
      <SheetTrigger asChild>
        <Button variant="ghost" size="icon">
          <Menu className="h-6 w-6" />
        </Button>
      </SheetTrigger>
      <SheetContent side="right">
        <SheetHeader>
          <SheetTitle>
            <span className="font-bold text-2xl font-pixelify-sans text-foreground">M</span>animator
          </SheetTitle>
        </SheetHeader>
        <div className="flex flex-col space-y-3 pt-6">
          {navLinks.map((link) => (
            <Button
              key={link.label}
              variant="ghost"
              className="w-full justify-start text-base"
              onClick={() => {
                console.log(`${link.label} clicked`);
                onToggle(false);
              }}
            >
              {link.label}
            </Button>
          ))}
        </div>
      </SheetContent>
    </Sheet>
  );
}
function HeroSection({ prompt, setPrompt }: { prompt: string; setPrompt: (s: string) => void }) {
  return (
    <section 
      className="flex flex-col items-center gap-8 my-12 md:my-16 bg-cover bg-center bg-no-repeat"
    >
      <h1 className="text-4xl md:text-5xl font-bold text-center text-foreground">
        Imagine with <span style={{ fontFamily: 'Pixelify Sans', fontSize: '1.2em' }}>Manimator</span>
      </h1>
      <div className="w-full max-w-2xl flex flex-col items-center gap-6">
        <PromptInput prompt={prompt} setPrompt={setPrompt} />
        <SuggestionBar setPrompt={setPrompt} />
      </div>
    </section>
  );
}
function PromptInput({ prompt, setPrompt }: { prompt: string; setPrompt: (s: string) => void }) {
  const navigate = useNavigate();

  const handleSend = () => {
    if (!prompt.trim()) return;
    const sessionId = uuidv4();
    navigate(`/chat/${sessionId}`, { state: { prompt } });
  };

  return (
    <div className="w-full bg-card border border-border rounded-lg p-4 shadow-lg">
      <Input
        type="text"
        placeholder="Create a math animation about..."
        value={prompt}
        onChange={(e) => setPrompt(e.target.value)}
        className="text-sm bg-transparent border-0 shadow-none focus-visible:ring-0 focus-visible:ring-offset-0 placeholder:text-muted-foreground h-auto pb-10"
      />
      <Separator className="my-2 bg-border" />
      <div className="flex justify-between items-center pt-1">
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <Paperclip className="h-5 w-5" />
        </Button>
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
            <Sparkles className="h-5 w-5" />
          </Button>
          <Button variant="default" size="icon" onClick={handleSend}>
            <SendHorizonal className="h-5 w-5" />
          </Button>
        </div>
      </div>
    </div>
  );
}

function SuggestionBar({ setPrompt }: { setPrompt: (s: string) => void }) {
  const suggestions = [
    { icon: <Search className="h-4 w-4" />, text: "Sine wave", promptText: "Create an animation of a sine wave." },
    { icon: <BarChart className="h-4 w-4" />, text: "Bar chart", promptText: "Generate an animated bar chart." },
    { icon: <Settings className="h-4 w-4" />, text: "Animated square", promptText: "Animate a square rotating and changing color." },
    { icon: <Users className="h-4 w-4" />, text: "Moving circle", promptText: "Show a circle moving across the screen." },
  ];

  return (
    <div className="flex flex-wrap justify-center gap-2.5">
      {suggestions.map((suggestion) => (
        <SuggestionButton
          key={suggestion.text}
          icon={suggestion.icon}
          text={suggestion.text}
          onClick={() => setPrompt(suggestion.promptText)}
        />
      ))}
    </div>
  );
}
// Projects Section
function ProjectsSection() {
  const projectItems = Array(4).fill({
    name: "Project Name",
    editedTime: "Edited 3 days ago",
  });

  return (
    <section className="bg-card rounded-2xl p-6 md:p-8 my-12 md:my-16 shadow-xl">
      <div className="flex flex-col items-center gap-16">
        <div className="w-full">
          <h2 className="text-lg font-medium mb-6">My Projects</h2>
          <div className="flex flex-wrap gap-6">
            <ProjectCard name="Project Name" editedTime="Edited 3 days ago" />
            <Button
              variant="outline"
              className="w-full sm:w-auto h-auto aspect-square flex flex-col items-center justify-center gap-2 p-4 text-muted-foreground hover:text-foreground min-w-[280px] min-h-[215px]"
              onClick={() => console.log("Add new project")}
            >
              <PlusCircle className="h-10 w-10" />
              <span>New Project</span>
            </Button>
          </div>
        </div>

        <div className="w-full">
          <h2 className="text-lg font-medium mb-6">From the Community</h2>
          <CommunityProjectsGrid projectItems={projectItems} />
          <Button
            variant="outline"
            size="sm"
            className="text-black border-black hover:text-black/80 hover:border-black/80"
            onClick={() => console.log("Show More clicked")}
          >
            Show More
          </Button>
        </div>
      </div>
    </section>
  );
}

function CommunityProjectsGrid({ projectItems }: { projectItems: any[] }) {
  return (
    <>
      {[1, 2, 3].map((section) => (
        <div key={section} className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6 mb-6">
          {projectItems.map((item, index) => (
            <ProjectCard key={`community-${section}-${index}`} name={item.name} editedTime={item.editedTime} />
          ))}
        </div>
      ))}
    </>
  );
}

// Footer
function Footer() {
  return (
    <footer className="border-t border-border py-14">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between gap-12">
        <div className="mb-10 md:mb-0">
          <h3 className="text-2xl font-bold text-foreground mb-4"><span className="font-['Pixelify_Sans']">Manimator</span></h3>
          <div className="flex space-x-4">
            {[Github, Twitter, Linkedin].map((Icon, index) => (
              <a key={index} href="#" className="text-muted-foreground hover:text-foreground">
                <Icon className="h-6 w-6" />
              </a>
            ))}
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 md:gap-12">
          {[
            { title: "Product", items: ["About", "News", "Hire a Partner", "Become a Partner", "Roadmap"] },
            { title: "Resources", items: ["Launched", "Support", "Affiliates", "Integrations", "Builder Hall of Fame"] },
            { title: "Legal", items: ["Privacy Policy", "Terms & Conditions", "Report Abuse"] },
          ].map((section, i) => (
            <div key={i}>
              <h4 className="font-bold text-sm text-foreground mb-3">{section.title}</h4>
              <ul className="space-y-3">
                {section.items.map((item) => (
                  <li key={item}>
                    <a href="#" className="text-sm text-muted-foreground hover:text-foreground">{item}</a>
                  </li>
                ))}
                {section.title === "Resources" && (
                  <li>
                    <a href="#" className="text-sm text-muted-foreground hover:text-foreground flex items-center">
                      Learn <ExternalLink className="ml-1 h-3 w-3" />
                    </a>
                  </li>
                )}
              </ul>
            </div>
          ))}
        </div>
      </div>
      <div className="text-center text-sm text-muted-foreground mt-12">
        © {new Date().getFullYear()} Manimator. All rights reserved.
      </div>
    </footer>
  );
}

// Main Page Component
export default function ManimatorPage() {
  const [prompt, setPrompt] = useState("");
  const [showMobileMenu, setShowMobileMenu] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground font-sans">
      <Header onMobileMenuToggle={setShowMobileMenu} />
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <HeroSection prompt={prompt} setPrompt={setPrompt} />
        <ProjectsSection />
      </main>
      <Footer />
    </div>
  );
}
