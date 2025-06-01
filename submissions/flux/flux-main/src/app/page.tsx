'use client'
import Image from 'next/image'
import { DotPattern } from '@/components/ui/dot-pattern'
import { Header } from '@/components/ui/header'
import { ColorfulText } from '@/components/ui/colourful-text'
import { SignupButton } from '@/components/ui/signup-button'
import { AnimatedShinyText } from '@/components/ui/animated-shiny-text'
import { cn } from "@/lib/utils"
import "./globals.css";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs"
import { LayoutDashboard, Edit3, ListChecks, BarChart3, PieChart, FileImage, BookOpen, Plug, Settings } from "lucide-react"
import { Linkedin, Github, X } from "lucide-react";
import Footer from "@/components/ui/footer";
import { PricingSection } from "@/components/ui/pricing-section";
import { ChevronDown } from "lucide-react";
import dynamic from 'next/dynamic'

// Lazily load heavy components
const MarqueeDemo = dynamic(() => import('@/components/magicui/marquee').then(mod => ({ default: mod.MarqueeDemo })), {
  loading: () => <div className="w-full h-[200px] bg-gray-50 rounded-lg animate-pulse" />,
  ssr: false
})

const WobbleCardDemo = dynamic(() => import('@/components/ui/wobble-card').then(mod => ({ default: mod.WobbleCardDemo })), {
  loading: () => <div className="w-full h-[200px] bg-gray-50 rounded-lg animate-pulse" />,
  ssr: false
})

// TabContent component for placeholder PNG and title
function TabContent({ title }: { title: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      {/* Placeholder for PNG */}
      <div className="w-[900px] h-[540px] flex items-center justify-center mb-2">
        <Image src="/placeholder.png" alt="placeholder" width={900} height={540} className="object-contain rounded-lg border border-dashed border-gray-300 bg-gray-50" />
      </div>
      
    </div>
  )
}

// FAQ Section Components
import React from "react";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/custom-accordion";

const FAQS = [
  {
    question: "What is Flux?",
    answer: "Flux is an AI-powered form builder and analytics platform that helps you create, analyze, and gain insights from your data instantly.",
  },
  {
    question: "How does AI help with forms?",
    answer: "Our AI agents can help you design forms, analyze responses, and generate actionable insights automatically, saving you time and effort.",
  },
  {
    question: "Can I integrate Flux with other tools?",
    answer: "Yes! Flux supports integrations with popular tools and APIs, making it easy to connect your forms and data workflows.",
  },
  {
    question: "Is my data secure?",
    answer: "Absolutely. We use industry-standard encryption and privacy practices to keep your data safe and secure.",
  },
  {
    question: "How do I get started?",
    answer: "Just sign up for free and start building your first AI-powered form in seconds!",
  },
];

const SectionBadge = ({ title }: { title: string }) => (
  <div className="flex justify-center items-center gap-2 bg-blue-100 px-2.5 py-1 rounded-full">
    <div className="relative flex justify-center items-center bg-blue-400/40 rounded-full w-1.5 h-1.5">
      <div className="flex justify-center items-center bg-blue-500 rounded-full w-2 h-2 animate-ping">
        <div className="flex justify-center items-center bg-blue-500 rounded-full w-2 h-2 animate-ping"></div>
      </div>
      <div className="top-1/2 left-1/2 absolute flex justify-center items-center bg-blue-600 rounded-full w-1.5 h-1.5 -translate-x-1/2 -translate-y-1/2"></div>
    </div>
    <span className="bg-clip-text bg-gradient-to-r from-purple-600 to-purple-800 font-medium text-transparent text-xs">
      {title}
    </span>
  </div>
);

const AnimationContainer = ({
  children,
  className,
  animation = "fadeUp",
  delay = 0,
}: {
  children: React.ReactNode;
  className?: string;
  animation?: "fadeUp" | "fadeDown" | "fadeLeft" | "fadeRight" | "scaleUp";
  delay?: number;
}) => {
  // Simple implementation without animations
  const delayStyle = {
    animationDelay: `${delay * 0.2}s`
  };
  
  return (
    <div 
      className={cn(
        "animate-fade-in", 
        {
          "animate-fade-in-up": animation === "fadeUp",
          "animate-fade-in-down": animation === "fadeDown",
          "animate-fade-in-left": animation === "fadeLeft",
          "animate-fade-in-right": animation === "fadeRight",
          "animate-scale-in": animation === "scaleUp",
        },
        className
      )}
      style={delayStyle}
    >
      {children}
    </div>
  );
};

const Wrapper = ({ className, children }: { className?: string; children: React.ReactNode }) => (
  <section className={cn("h-full mx-auto w-full lg:max-w-screen-xl px-4 lg:px-20", className)}>
    {children}
  </section>
);

function FAQSection() {
  return (
    <Wrapper className="py-20 lg:py-32">
      <div className="flex flex-col items-center gap-4 text-center">
        <AnimationContainer animation="fadeUp" delay={0.2}>
          <SectionBadge title="FAQ" />
        </AnimationContainer>
        <AnimationContainer animation="fadeUp" delay={0.3}>
          <h2 className="font-black text-3xl md:text-4xl lg:text-5xl text-gray-900">
            Frequently Asked Questions
          </h2>
        </AnimationContainer>
        <AnimationContainer animation="fadeUp" delay={0.4}>
          <p className="mx-auto max-w-xl text-gray-600 text-base md:text-lg">
            Find answers to common questions about how Flux helps you build, analyze, and automate forms with AI.
          </p>
        </AnimationContainer>
      </div>
      <div className="mx-auto pt-10 max-w-3xl">
        <Accordion type="single" collapsible className="space-y-4 w-full">
          {FAQS.map((item, index) => (
            <AnimationContainer
              key={index}
              animation="fadeUp"
              delay={0.5 + index * 0.1}
            >
              <AccordionItem
                value={`item-${index}`}
                className="bg-blue-50/50 px-6 border border-blue-100 rounded-2xl"
              >
                <AccordionTrigger className="py-6 font-medium text-gray-900 text-base md:text-lg text-left hover:no-underline">
                  {item.question}
                </AccordionTrigger>
                <AccordionContent className="text-gray-700 text-left">
                  {item.answer}
                </AccordionContent>
              </AccordionItem>
            </AnimationContainer>
          ))}
        </Accordion>
      </div>
    </Wrapper>
  );
}

export default function Home() {
  return (
    <div className="relative min-h-screen bg-white flex flex-col">
      <DotPattern
        className="absolute inset-0 w-full h-full [mask-image:radial-gradient(ellipse_at_center,transparent_20%,white_80%)]"
        glow
        width={18}
        height={18}
        maxDots={12000}
        cr={1}
        style={{ position: 'fixed', zIndex: 0 }}
      />
      <Header />
      
      {/* Hero Section */}
      <div className="container mx-auto px-4 pt-40 pb-20 flex flex-col items-center justify-center min-h-[90vh] relative z-10">
        <div className="absolute left-[35%] right-[35%] top-[25%] bottom-[30%] -z-10 bg-white [mask-image:radial-gradient(circle_at_center,white_100%,white_80%_30%,white_50%_60%,transparent_90%)] rounded-lg"></div>
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-4 text-gray-900">
            Superintelligent Form Builder with <ColorfulText text="Agents" /> and Memory
          </h1>
          <p className="text-base text-gray-600 mb-6 max-w-xl mx-auto leading-snug">
            Form Builder with AI-Powered Creation and Analysis. Design beautiful forms in seconds, gather insights automatically, and let our AI agents help you understand your data.
          </p>
          <div className="flex justify-center mb-6">
            <div className={cn(
              "group rounded-full border border-gray-200 bg-white text-base transition-all ease-in hover:cursor-pointer hover:bg-gray-50 hover:shadow-sm"
            )}>
              <AnimatedShinyText className="inline-flex items-center justify-center px-4 py-1 transition ease-out text-gray-800 font-medium hover:text-neutral-600 hover:duration-300 hover:dark:text-neutral-400">
                <span>✨ Powered by</span>
                <Image src="/agno.png" alt="Agno" width={40} height={18} className="inline-block mx-1" />
                
              </AnimatedShinyText>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-6">
            <SignupButton href="/auth/sign-up">
              Sign up for free
            </SignupButton>
            <button 
              onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
              className="bg-blue-50 text-blue-600 text-sm font-medium py-3 px-8 rounded-md transition-colors border border-blue-100 hover:bg-blue-100"
            >
              Explore features
            </button>
          </div>
        </div>
      </div>

      {/* Tabs Section */}
      <div id="features" className="container mx-auto px-4 pb-15 flex flex-col items-center justify-center relative z-10">
        <Tabs defaultValue="overview" className="w-full max-w-4xl">
          <TabsList className="flex flex-wrap justify-center items-center gap-2 mb-6 bg-transparent p-0 w-full">
            <TabsTrigger value="overview" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <LayoutDashboard className="w-5 h-5" /> Overview
            </TabsTrigger>
            <TabsTrigger value="form-builder" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <Edit3 className="w-5 h-5" /> Form Builder
            </TabsTrigger>
            <TabsTrigger value="responses" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <ListChecks className="w-5 h-5" /> Responses
            </TabsTrigger>
            <TabsTrigger value="analysis" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <BarChart3 className="w-5 h-5" /> Analysis
            </TabsTrigger>
            <TabsTrigger value="visualizations" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <PieChart className="w-5 h-5" /> Visualizations
            </TabsTrigger>
            <TabsTrigger value="media-insights" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <FileImage className="w-5 h-5" /> Media Insights
            </TabsTrigger>
            <TabsTrigger value="memory" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <BookOpen className="w-5 h-5" /> Memory
            </TabsTrigger>
            <TabsTrigger value="integrations" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <Plug className="w-5 h-5" /> Integrations
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center gap-2 px-4 py-2 rounded-xl border border-gray-200 data-[state=active]:bg-gray-900 data-[state=active]:text-white data-[state=active]:border-gray-900 bg-white text-gray-900 font-medium text-base shadow-none transition-colors">
              <Settings className="w-5 h-5" /> Settings
            </TabsTrigger>
          </TabsList>
          <TabsContent value="overview">
            <TabContent title="Overview" />
          </TabsContent>
          <TabsContent value="form-builder">
            <TabContent title="Form Builder" />
          </TabsContent>
          <TabsContent value="responses">
            <TabContent title="Responses" />
          </TabsContent>
          <TabsContent value="analysis">
            <TabContent title="Analysis" />
          </TabsContent>
          <TabsContent value="visualizations">
            <TabContent title="Visualizations" />
          </TabsContent>
          <TabsContent value="media-insights">
            <TabContent title="Media Insights" />
          </TabsContent>
          <TabsContent value="memory">
            <TabContent title="Memory" />
          </TabsContent>
          <TabsContent value="integrations">
            <TabContent title="Integrations" />
          </TabsContent>
          <TabsContent value="settings">
            <TabContent title="Settings" />
          </TabsContent>
        </Tabs>
      </div>

      {/* Wall Of Love Section */}
      <div className="relative z-10 flex flex-col items-center justify-center w-full py-20">
        <span className="text-[15px] font-semibold text-orange-600 mb-3" style={{letterSpacing: 0}}>What our customers say</span>
<h2
  className="text-[44px] leading-tight font-black text-neutral-900 mb-10"
  style={{ fontFamily: 'Satoshi, sans-serif' }}
>
  Wall of love
</h2>
        <div className="w-full max-w-5xl">
          <MarqueeDemo />
        </div>
      </div>

      {/* Pricing Section */}
      <div id="pricing" className="relative z-10">
        <PricingSection />
      </div>

      {/* Wobble Card Section */}
      <div className="w-full flex flex-col items-center justify-center py-16 relative z-10">
        <WobbleCardDemo />
      </div>

      {/* FAQ Section */}
      <div id="faq" className="w-full relative z-10">
        <FAQSection />
      </div>

      {/* Footer */}
      <div className="relative z-10">
        <Footer />
      </div>

    </div>
  )
}
