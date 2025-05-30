// src/components/ResultsCard.tsx
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"; // Using more card parts
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Share2, Mail, Link as LinkIconLucide, Copy, Linkedin, Github, Twitter, Briefcase, UserCheck, Sparkles, BarChart3, UserSquare2 } from "lucide-react"; // Using Link from lucide
import { useToast as useShadcnToast } from "@/hooks/use-toast";

export interface AnalysisResult {
  description: string[];
  contacts: {
    email?: string;
    linkedin?: string;
    github?: string;
    twitter?: string;
    website?: string;
  };
  roast: string;
  traits: string[];
  vibes: string[];
  careerOptions?: string[];
  personalityArchetype?: string;
}

interface ResultsCardProps {
  result: AnalysisResult;
  originalUrl: string;
}

// Simplified card style
const SimpleCard = ({ children, className }: { children: React.ReactNode, className?: string }) => (
  <div className={`bg-white p-6 shadow-sm border border-slate-200 rounded-lg ${className}`}>
    {children}
  </div>
);

const SectionTitle = ({ icon, title, iconColorClass = "text-blue-600" }: { icon: React.ReactNode, title: string, iconColorClass?: string }) => (
  <h3 className={`text-xl font-semibold text-slate-700 mb-4 flex items-center gap-2.5 ${iconColorClass}`}>
    {icon}
    {title}
  </h3>
);


export const ResultsCard = ({ result, originalUrl }: ResultsCardProps) => {
  const { toast } = useShadcnToast();

  const handleShare = async () => {
    const shareText = `Roast: "${result.roast}"\n\nSee your roast: ${window.location.origin}`;
    // ... (rest of handleShare logic)
     if (navigator.share) {
      try {
        await navigator.share({
          title: "AI just Roasted my portfolio! 🔥",
          text: shareText
        });
      } catch (err) {
        console.warn("Share API failed or cancelled:", err);
        handleCopy(shareText, "Share text copied. The native share dialog couldn't be opened.");
      }
    } else {
      handleCopy(shareText, "Share text copied to clipboard!");
    }
  };

  const handleCopy = (text: string, description: string = "Copied to clipboard! 🔥") => {
    // ... (rest of handleCopy logic)
    navigator.clipboard.writeText(text).then(() => {
      toast({
        title: "Copied!",
        description: description,
        duration: 3000,
      });
    }).catch(err => {
      toast({
        title: "Copy Failed",
        description: "Could not copy text. Please try manually.",
        variant: "destructive",
      });
    });
  };

  const getIconForSocial = (key: keyof AnalysisResult['contacts']) => {
    // ... (same as before)
    switch(key) {
      case 'email': return <Mail className="w-4 h-4" />;
      case 'linkedin': return <Linkedin className="w-4 h-4" />;
      case 'github': return <Github className="w-4 h-4" />;
      case 'twitter': return <Twitter className="w-4 h-4" />;
      case 'website': return <LinkIconLucide className="w-4 h-4" />;
      default: return <LinkIconLucide className="w-4 h-4" />;
    }
  };

  return (
    <div className="space-y-6 md:space-y-8">
      {/* Description Card */}
      <SimpleCard>
        <SectionTitle icon={<UserSquare2 className="w-6 h-6" />} title="AI's First Impression" />
        <div className="space-y-1.5 text-slate-600">
          {result.description.map((line, index) => (
            <p key={index} className="leading-relaxed">{line}</p>
          ))}
        </div>
      </SimpleCard>

      {/* Contacts Card */}
      {(Object.values(result.contacts).some(v => v)) && (
        <SimpleCard>
          <SectionTitle icon={<Mail className="w-6 h-6" />} title="Contact Points" />
          <div className="flex flex-wrap gap-2.5">
            {Object.entries(result.contacts).map(([key, value]) => {
              if (value) {
                const contactKey = key as keyof AnalysisResult['contacts'];
                return (
                  <a 
                    key={key} 
                    href={contactKey === 'email' ? `mailto:${value}` : value.startsWith('http') ? value : `https://${value}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="inline-block"
                  >
                    <Badge
                      variant="outline" // Use outline for a cleaner look
                      className="border-blue-500 text-blue-600 hover:bg-blue-50 transition-colors px-3 py-1.5 text-sm capitalize flex items-center gap-1.5"
                    >
                      {getIconForSocial(contactKey)}
                      {key}
                    </Badge>
                  </a>
                );
              }
              return null;
            })}
          </div>
        </SimpleCard>
      )}
      
      {/* The Roast Card */}
      <SimpleCard className="bg-rose-50 border-rose-200"> {/* Slightly different bg for roast */}
        <SectionTitle icon={<span className="text-2xl">🔥</span>} title="The Roast" iconColorClass="text-rose-600" />
        <blockquote className="text-lg text-rose-700 italic leading-relaxed border-l-4 border-rose-400 pl-4 py-1">
          "{result.roast}"
        </blockquote>
        <Button
          onClick={() => handleCopy(`"${result.roast}"`)}
          variant="ghost"
          size="sm"
          className="mt-3 text-rose-600 hover:text-rose-700 hover:bg-rose-100 px-2"
        >
          <Copy className="w-3.5 h-3.5 mr-1.5" /> Copy Roast
        </Button>
      </SimpleCard>

      {/* Personality Traits Card */}
      {result.traits && result.traits.length > 0 && (
        <SimpleCard>
          <SectionTitle icon={<BarChart3 className="w-6 h-6" />} title="Personality Traits" />
          <div className="flex flex-wrap gap-2">
            {result.traits.map((trait, index) => (
              <Badge
                key={index}
                variant="secondary" // Uses muted background
                className="bg-slate-100 text-slate-700 border-slate-300 text-sm px-3 py-1"
              >
                {trait}
              </Badge>
            ))}
          </div>
        </SimpleCard>
      )}

      {/* Vibe Tags Card */}
      {result.vibes && result.vibes.length > 0 && (
        <SimpleCard>
          <SectionTitle icon={<Sparkles className="w-6 h-6" />} title="Your Vibe" />
          <div className="flex flex-wrap gap-2.5">
            {result.vibes.map((vibe, index) => (
              <Badge
                key={index}
                className="bg-blue-500 text-white text-sm px-3.5 py-1.5 font-medium" // Primary blue badge
              >
                {vibe}
              </Badge>
            ))}
          </div>
        </SimpleCard>
      )}

      {/* Personality Archetype Card */}
      {result.personalityArchetype && (
        <SimpleCard>
          <SectionTitle icon={<UserCheck className="w-6 h-6" />} title="Your Archetype" />
          <p className="text-lg text-slate-700 font-medium bg-slate-50 p-3 rounded-md border border-slate-200">
            {result.personalityArchetype}
          </p>
        </SimpleCard>
      )}

      {/* Career Options Card */}
      {result.careerOptions && result.careerOptions.length > 0 && (
        <SimpleCard>
          <SectionTitle icon={<Briefcase className="w-6 h-6" />} title="Potential Career Paths" />
          <ul className="space-y-1.5 list-disc list-inside text-slate-600">
            {result.careerOptions.map((option, index) => (
              <li key={index} className="ml-2">{option}</li>
            ))}
          </ul>
        </SimpleCard>
      )}

      {/* Share Button */}
      <div className="flex justify-center mt-10">
        <Button
          onClick={handleShare}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-8 py-3 text-md rounded-md
                     transition-colors transform hover:scale-105"
        >
          <Share2 className="w-5 h-5 mr-2" />
          Share Your Results
        </Button>
      </div>
    </div>
  );
};