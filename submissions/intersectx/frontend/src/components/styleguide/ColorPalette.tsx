import React from 'react';

const ColorCard = ({ 
  color, 
  name, 
  hex, 
  description 
}: { 
  color: string; 
  name: string; 
  hex: string; 
  description: string 
}) => {
  return (
    <div className="flex flex-col">
      <div 
        className={`${color} h-24 rounded-t-lg shadow-sm`}
        aria-label={`${name} color: ${hex}`}
      ></div>
      <div className="p-4 bg-white rounded-b-lg shadow-sm border-t-0 border border-gray-200">
        <h3 className="font-semibold text-primary">{name}</h3>
        <div className="text-sm text-secondary">{hex}</div>
        <p className="mt-2 text-sm text-primary">{description}</p>
      </div>
    </div>
  );
};

const ColorPalette: React.FC = () => {
  return (
    <div className="bg-primary min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <div className="mb-12">
          <h1 className="text-3xl font-bold text-primary mb-2">Intersectx Color Palette</h1>
          <p className="text-secondary">Mercury-inspired finance application color scheme.</p>
        </div>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Primary / Brand Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ColorCard 
              color="bg-purple" 
              name="Soft Purple" 
              hex="#A484DE" 
              description="Main accent color for primary actions, links, and highlights."
            />
            <ColorCard 
              color="bg-purple-dark" 
              name="Dark Purple" 
              hex="#836AB2" 
              description="For primary buttons, hover states, and emphasis."
            />
            <ColorCard 
              color="bg-purple-light" 
              name="Light Lavender" 
              hex="#C6A9E4" 
              description="For subtle backgrounds, hover effects, or focus rings."
            />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Neutrals & Support Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <ColorCard 
              color="bg-off-white" 
              name="Off-White Background" 
              hex="#F6F3ED" 
              description="Main page and section background color."
            />
            <ColorCard 
              color="bg-white" 
              name="Pure White" 
              hex="#FFFFFF" 
              description="For cards, panels, dialogs, and input fields."
            />
            <ColorCard 
              color="bg-[#E5E7EB]" 
              name="Light Gray" 
              hex="#E5E7EB" 
              description="For surfaces, sub-panels, and non-critical UI zones."
            />
            <ColorCard 
              color="bg-[#D1D5DB]" 
              name="Gray Border" 
              hex="#D1D5DB" 
              description="For borders, dividers, and outlines."
            />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Text Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <ColorCard 
              color="bg-[#111827]" 
              name="Dark Text" 
              hex="#111827" 
              description="Primary text color for all light backgrounds."
            />
            <ColorCard 
              color="bg-[#4B5563]" 
              name="Secondary Text" 
              hex="#4B5563" 
              description="For secondary text, hints, labels, and inactive icons."
            />
            <ColorCard 
              color="bg-[#6B7280]" 
              name="Icon/Accent Gray" 
              hex="#6B7280" 
              description="For icons or disabled text."
            />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Accent / Supporting Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ColorCard 
              color="bg-indigo" 
              name="Indigo Blue" 
              hex="#5767B4" 
              description="For secondary accents like hyperlinks, info icons, and graphs."
            />
            <ColorCard 
              color="bg-[#22C55E]" 
              name="Teal/Greenish" 
              hex="#22C55E" 
              description="Optional vibrant accent for freshness (use sparingly)."
            />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Feedback & Status Colors</h2>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <ColorCard 
              color="bg-success" 
              name="Success" 
              hex="#28A745" 
              description="For success messages, badges, or iconography."
            />
            <ColorCard 
              color="bg-warning" 
              name="Warning" 
              hex="#FBBF24" 
              description="For cautions or warnings (use sparingly)."
            />
            <ColorCard 
              color="bg-error" 
              name="Error" 
              hex="#EF4444" 
              description="For errors and critical alerts."
            />
            <ColorCard 
              color="bg-info" 
              name="Info" 
              hex="#3B82F6" 
              description="For informational messages or neutral alerts."
            />
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Button Examples</h2>
          <div className="flex flex-wrap gap-4">
            <button className="px-4 py-2 bg-purple-dark text-white rounded-md hover:bg-purple transition-colors">
              Primary Button
            </button>
            <button className="px-4 py-2 bg-white text-purple-dark border border-purple-dark rounded-md hover:bg-purple-light hover:text-white transition-colors">
              Secondary Button
            </button>
            <button className="px-4 py-2 bg-white text-indigo border border-indigo rounded-md hover:bg-indigo hover:text-white transition-colors">
              Accent Button
            </button>
            <button className="px-4 py-2 bg-[#E5E7EB] text-accent rounded-md cursor-not-allowed">
              Disabled Button
            </button>
          </div>
        </section>

        <section className="mb-12">
          <h2 className="text-xl font-semibold text-primary mb-4">Feedback Message Examples</h2>
          <div className="space-y-4">
            <div className="p-4 bg-white border-l-4 border-success rounded shadow-sm">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-success" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-success font-medium">Successfully updated your profile</p>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-white border-l-4 border-warning rounded shadow-sm">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-warning" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-warning font-medium">Your subscription will expire in 3 days</p>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-white border-l-4 border-error rounded shadow-sm">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-error" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-error font-medium">There was an error processing your payment</p>
                </div>
              </div>
            </div>
            
            <div className="p-4 bg-white border-l-4 border-info rounded shadow-sm">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-info" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2h-1V9a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm text-info font-medium">New features have been added to your dashboard</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
};

export default ColorPalette;
