"use client";

import React, { useState, useEffect } from "react";
import { Check, AlertCircle, X } from "lucide-react";
import { cn } from "@/lib/utils";

export const SectionBadge = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="flex justify-center items-center gap-2 bg-blue-100 px-2.5 py-1 rounded-full">
      <div className="relative flex justify-center items-center bg-blue-400/40 rounded-full w-1.5 h-1.5">
        <div className="flex justify-center items-center bg-blue-500 rounded-full w-2 h-2 animate-ping">
          <div className="flex justify-center items-center bg-blue-500 rounded-full w-2 h-2 animate-ping"></div>
        </div>
        <div className="top-1/2 left-1/2 absolute flex justify-center items-center bg-blue-600 rounded-full w-1.5 h-1.5 -translate-x-1/2 -translate-y-1/2"></div>
      </div>
      <span className="bg-clip-text bg-gradient-to-r from-purple-600 to-purple-800 font-medium text-transparent text-xs">
        {children}
      </span>
    </div>
  );
};

export function PricingSection() {
  const [billingPeriod, setBillingPeriod] = useState<"monthly" | "annual">("monthly");
  const [showAlert, setShowAlert] = useState(false);

  useEffect(() => {
    if (showAlert) {
      const timer = setTimeout(() => {
        setShowAlert(false);
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [showAlert]);

  const calculateAnnualPrice = (monthlyPrice: number) => {
    const annualPrice = monthlyPrice * 12 * 0.8; // 20% discount
    return annualPrice / 12; // Show as monthly equivalent
  };

  const handlePricingButtonClick = (e: React.MouseEvent) => {
    e.preventDefault();
    setShowAlert(true);
  };

  return (
    <section className="w-full py-20 relative overflow-hidden">
      {/* Content container */}
      <div className="container mx-auto px-4">
        <div className="flex flex-col items-center text-center mb-12">
          <SectionBadge>PRICING</SectionBadge>
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold mt-4 mb-4 text-gray-900">
            Choose the right plan for you
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Get started for free or upgrade to unlock all features. All plans include a 14-day trial.
          </p>
          
          {/* Billing Period Toggle */}
          <div className="mt-8 p-1 bg-blue-50/50 backdrop-blur-sm rounded-lg inline-flex border border-blue-200/50 shadow-sm">
            <button
              onClick={() => setBillingPeriod("monthly")}
              className={cn(
                "px-6 py-2 rounded-md text-sm font-medium transition-all duration-300 relative overflow-hidden",
                billingPeriod === "monthly"
                  ? "bg-gradient-to-r from-blue-50 to-blue-100 text-blue-600 shadow-sm border border-blue-200/50" 
                  : "text-gray-500 hover:text-gray-700"
              )}
            >
              {billingPeriod === "monthly" && (
                <span className="absolute inset-0 bg-gradient-to-r from-blue-400/10 to-blue-500/10 animate-spotlight"></span>
              )}
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod("annual")}
              className={cn(
                "px-6 py-2 rounded-md text-sm font-medium transition-all duration-300 relative overflow-hidden",
                billingPeriod === "annual"
                  ? "bg-gradient-to-r from-blue-50 to-blue-100 text-blue-600 shadow-sm border border-blue-200/50" 
                  : "text-gray-500 hover:text-gray-700"
              )}
            >
              {billingPeriod === "annual" && (
                <span className="absolute inset-0 bg-gradient-to-r from-blue-400/10 to-blue-500/10 animate-spotlight"></span>
              )}
              Annual <span className="ml-1 text-green-500 text-xs font-bold">Save 20%</span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {/* Free Plan */}
          <div className="backdrop-blur-sm rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-300 p-8 flex flex-col group relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-bl from-blue-50/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            {/* Top-right to bottom-left gradient spotlight effect */}
            <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-to-bl from-blue-300/20 to-transparent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 transform group-hover:translate-x-full group-hover:translate-y-full"></div>
            <h3 className="text-xl font-bold text-gray-900">Free</h3>
            <p className="text-gray-500 mt-2 mb-6">Perfect for getting started</p>
            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">$0</span>
              <span className="text-gray-500">/month</span>
            </div>
            <button
              onClick={handlePricingButtonClick}
              className="py-2 px-4 bg-blue-50 text-blue-600 rounded-md transition-colors border-white hover:border hover:border-blue-100 mb-6 relative overflow-hidden group-hover:bg-blue-100/50"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-blue-400/0 via-blue-400/10 to-blue-400/0 opacity-0 group-hover:opacity-100 animate-spotlight"></span>
              Start for free
            </button>
            <ul className="space-y-3 flex-grow">
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Basic project management</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">5 projects</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Community support</span>
              </li>
              <li className="flex items-start">
                <X className="h-5 w-5 text-gray-400 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-400">Advanced features</span>
              </li>
              <li className="flex items-start">
                <X className="h-5 w-5 text-gray-400 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-400">Priority support</span>
              </li>
            </ul>
          </div>

          {/* Basic Plan */}
          <div className="backdrop-blur-sm rounded-xl border-2 border-blue-500 shadow-md hover:shadow-lg hover:border-blue-600 transition-all duration-300 p-8 flex flex-col relative group overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-bl from-blue-50/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            {/* Top-right to bottom-left gradient spotlight effect */}
            <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-to-bl from-blue-400/30 to-transparent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 transform group-hover:translate-x-full group-hover:translate-y-full"></div>
            <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg rounded-tr-lg">
              POPULAR
            </div>
            <h3 className="text-xl font-bold text-gray-900">Basic</h3>
            <p className="text-gray-500 mt-2 mb-6">For professionals and teams</p>
            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">${billingPeriod === "monthly" ? "20" : calculateAnnualPrice(20).toFixed(2)}</span>
              <span className="text-gray-500">/month{billingPeriod === "annual" ? ", billed annually" : ""}</span>
              {billingPeriod === "annual" && (
                <div className="mt-1 text-xs text-green-600 font-medium">
                  Billed annually (${(20 * 12 * 0.8).toFixed(2)})
                </div>
              )}
            </div>
            <button
              onClick={handlePricingButtonClick}
              className="py-2 px-4 bg-blue-600 text-white rounded-md mb-6 hover:bg-blue-700 transition-colors relative overflow-hidden"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-blue-400/0 via-blue-400/20 to-blue-400/0 opacity-0 group-hover:opacity-100 animate-spotlight"></span>
              Get started
            </button>
            <ul className="space-y-3 flex-grow">
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Everything in Free</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Unlimited projects</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Advanced analytics</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Priority email support</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">API access</span>
              </li>
            </ul>
          </div>

          {/* Enterprise Plan */}
          <div className="backdrop-blur-sm rounded-xl border border-gray-200 shadow-sm hover:shadow-md hover:border-blue-300 transition-all duration-300 p-8 flex flex-col group relative overflow-hidden">
            <div className="absolute inset-0 bg-gradient-to-bl from-blue-50/50 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
            {/* Top-right to bottom-left gradient spotlight effect */}
            <div className="absolute top-0 right-0 w-1/2 h-1/2 bg-gradient-to-bl from-blue-300/20 to-transparent opacity-0 group-hover:opacity-100 blur-xl transition-opacity duration-500 transform group-hover:translate-x-full group-hover:translate-y-full"></div>
            <h3 className="text-xl font-bold text-gray-900">Enterprise</h3>
            <p className="text-gray-500 mt-2 mb-6">For large organizations</p>
            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">Custom</span>
            </div>
            <button
              onClick={handlePricingButtonClick}
              className="py-2 px-4 bg-gray-800 text-white rounded-md mb-6 hover:bg-gray-900 transition-colors relative overflow-hidden"
            >
              <span className="absolute inset-0 bg-gradient-to-r from-gray-500/0 via-gray-500/20 to-gray-500/0 opacity-0 group-hover:opacity-100 animate-spotlight"></span>
              Contact us
            </button>
            <ul className="space-y-3 flex-grow">
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Everything in Basic</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Dedicated support</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Custom integrations</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">SLA guarantees</span>
              </li>
              <li className="flex items-start">
                <Check className="h-5 w-5 text-green-500 mr-2 shrink-0 mt-0.5" />
                <span className="text-gray-600">Tailored solutions</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Coming Soon Alert */}
        {showAlert && (
          <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-6 py-3 rounded-lg shadow-lg flex items-center space-x-2 animate-fade-in z-50">
            <AlertCircle className="h-5 w-5" />
            <span>Coming soon! We're still building this feature.</span>
            <button onClick={() => setShowAlert(false)} className="ml-2 text-gray-400 hover:text-gray-300">
              <X size={16} />
            </button>
          </div>
        )}
      </div>
    </section>
  );
} 