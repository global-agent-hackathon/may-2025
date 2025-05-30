import { GoogleGenerativeAI } from '@google/generative-ai';
import { AnalysisResult } from '@/components/ResultsCard';

export class GeminiService {
  private static genAI = new GoogleGenerativeAI('AIzaSyB9iOctsAW4Bp_VcFDPDU2VBjygwmeRRds');

  static async analyzePortfolio(content: string, url: string): Promise<{ success: boolean; result?: AnalysisResult; error?: string }> {
    try {
      console.log('Starting Gemini analysis');
      
      const model = this.genAI.getGenerativeModel({ 
        model: "gemini-2.0-flash",
        systemInstruction: `
You are RoastMasterGPT, a brutally honest but lovable AI with a sharp tongue and a soft heart. Your mission is to analyze personal portfolios and create wildly entertaining, witty, and slightly shame-inducing roasts — the kind that makes people laugh, then rethink their life choices (in a good way).

You must:

1. **Summarize the person** in exactly 5 witty lines based on their portfolio.
2. **Extract contact info** if available (email, socials, website).
3. **Roast them** in a friendly yet savage paragraph. Think: roasting your smartest, most try-hard friend. Make it sting a little — just enough to feel the shame tickle — but never cross into being mean.
4. **Guess their personality traits** (e.g., “humble,” “overconfident,” “intelligent,” “wannabe guru,” “perfectionist”).
5. **Assign vibe tags** (fun, meme-like labels like "AI Bro", "Startup Overthinker", "Design Diva", "Clout Chaser"). Provide 3 vibe tags.
6. **Suggest Career Options:** Based on the skills and projects, suggest 3-4 potential career paths or roles.
7. **Identify Personality Archetype:** Match their overall profile to a known archetype like "The Visionary Entrepreneur, Elon Musk" "The Meticulous Researcher, Ilya" "The Polymath Technologist," "The Creative Scientist, Albert Einstein" or "Curiosity Driven, Richar Feynman" Be descriptive in a single phrase or short sentence.

## 🧠 Your tone:
- Playful, sarcastic, internet-savvy
- Throw in subtle burns, ironic praise, Gen Z humor, and observational comedy
- Avoid cruelty — you're here to mock lovingly

## 🛑 STRICT OUTPUT FORMAT:
IMPORTANT: Respond ONLY with valid JSON in this exact format:
{
  "description": ["5 lines describing the person"],
  "contacts": {
    "email": "email@example.com or null",
    "linkedin": "linkedin_url or null", 
    "github": "github_url or null",
    "twitter": "twitter_url or null",
    "website": "website_url or null"
  },
  "roast": "One funny, shame-tinged roast paragraph",
  "traits": ["trait1", "trait2", "trait3", "trait4", "trait5"],
  "vibes": ["vibe1", "vibe2", "vibe3"],
  "careerOptions": ["Career Option 1", "Career Option 2", "Career Option 3"],
  "personalityArchetype": "Example: The Eccentric Genius with a Coffee Addiction"
}

❗ No markdown, no comments, no explanation — just pure JSON that can be rendered in an app.
`
      });

      const prompt = `Analyze this portfolio content and roast this person (playfully):

URL: ${url}

Content:
${content.slice(0, 80000)}

Remember: Respond with ONLY valid JSON, no markdown formatting or extra text.`;

      const result = await model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      console.log('Gemini raw response (with new features):', text);

      let cleanedText = text.trim();
      if (cleanedText.startsWith('```json')) {
        cleanedText = cleanedText.replace(/^```json\s*/, '').replace(/\s*```$/, '');
      } else if (cleanedText.startsWith('```')) {
        cleanedText = cleanedText.replace(/^```\s*/, '').replace(/\s*```$/, '');
      }
      
      // Attempt to parse, ensure it's valid JSON
      try {
        const analysisResult: AnalysisResult = JSON.parse(cleanedText);
        console.log('Parsed analysis result (with new features):', analysisResult);
        
        // Basic validation for new fields (optional but good practice)
        if (!Array.isArray(analysisResult.careerOptions)) {
            console.warn("Career options not found or not an array, setting to empty array");
            analysisResult.careerOptions = [];
        }
        if (typeof analysisResult.personalityArchetype !== 'string') {
            console.warn("Personality archetype not found or not a string, setting to default");
            analysisResult.personalityArchetype = "Archetype Undefined";
        }

        return {
          success: true,
          result: analysisResult
        };
      } catch (parseError) {
        console.error('Gemini JSON parsing error:', parseError);
        console.error('Problematic JSON string:', cleanedText);
        return {
          success: false,
          error: 'AI returned an invalid format. Could not parse the analysis.'
        };
      }
    } catch (error)
    {
      console.error('Gemini analysis error in service:', error);
      let errorMessage = 'AI analysis failed due to an unexpected issue.';
      if (error instanceof Error) {
        errorMessage = error.message;
      }
      // More specific error handling for API errors if possible
      // e.g. if (error.status === 429) { errorMessage = "API rate limit exceeded." }
      return {
        success: false,
        error: errorMessage
      };
    }
  }
}
