import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EnvelopeIcon, LockClosedIcon, UserIcon, BuildingOfficeIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../lib/api-client';

// Define the form interfaces for each step
interface FounderInfo {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  linkedInUrl: string;
  role: string;
  phoneNumber: string;
}

interface CompanyInfo {
  companyName: string;
  industry: string;
  stage: string;
  city: string;
  country: string;
}

interface FundingDetails {
  fundingAmount: string;
  fundingPurpose: string;
  timeline: string;
}

interface CompanyStatus {
  isIncorporated: boolean;
  websiteUrl: string;
  description: string;
}

interface DocumentUpload {
  pitchDeck: File | null;
  businessPlan: File | null;
  financialModel: File | null;
  productDemo: File | null;
}

type Step = 'founderInfo' | 'companyInfo' | 'fundingDetails' | 'companyStatus' | 'documents';

export default function FounderSignup() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [currentStep, setCurrentStep] = useState<Step>('founderInfo');
  const [error, setError] = useState<string | null>(null);
  const [consent, setConsent] = useState(false);
  const [showLoading, setShowLoading] = useState(false);
  
  // Form state for each step
  const [founderInfo, setFounderInfo] = useState<FounderInfo>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    linkedInUrl: '',
    role: '',
    phoneNumber: '',
  });
  
  const [companyInfo, setCompanyInfo] = useState<CompanyInfo>({
    companyName: '',
    industry: '',
    stage: '',
    city: '',
    country: '',
  });
  
  const [fundingDetails, setFundingDetails] = useState<FundingDetails>({
    fundingAmount: '',
    fundingPurpose: '',
    timeline: '',
  });
  
  const [companyStatus, setCompanyStatus] = useState<CompanyStatus>({
    isIncorporated: false,
    websiteUrl: '',
    description: '',
  });
  
  const [documents, setDocuments] = useState<DocumentUpload>({
    pitchDeck: null,
    businessPlan: null,
    financialModel: null,
    productDemo: null,
  });
  
  // Industry options
  const industryOptions = [
    'Software & SaaS',
    'Fintech',
    'Healthcare & Biotech',
    'AI & Machine Learning',
    'E-commerce',
    'Hardware & IoT',
    'Mobile Applications',
    'Enterprise Software',
    'Cleantech & Sustainability',
    'Consumer Internet',
    'Other'
  ];
  
  // Company stage options
  const stageOptions = [
    'Pre-seed',
    'Seed',
    'Series A',
    'Series B',
    'Series C+',
    'Growth'
  ];
  
  // Funding purpose options
  const fundingPurposeOptions = [
    'Product Development',
    'Market Expansion',
    'Team Building',
    'Sales & Marketing',
    'Research & Development',
    'Working Capital',
    'Other'
  ];
  
  // Timeline options
  const timelineOptions = [
    'Immediate',
    '1-3 months',
    '3-6 months',
    '6-12 months'
  ];
  
  // Handle file upload
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>, type: keyof DocumentUpload) => {
    if (e.target.files && e.target.files[0]) {
      setDocuments(prev => ({
        ...prev,
        [type]: e.target.files![0]
      }));
    }
  };
  
  // Navigation between steps
  const nextStep = () => {
    if (currentStep === 'founderInfo') setCurrentStep('companyInfo');
    else if (currentStep === 'companyInfo') setCurrentStep('fundingDetails');
    else if (currentStep === 'fundingDetails') setCurrentStep('companyStatus');
    else if (currentStep === 'companyStatus') setCurrentStep('documents');
  };
  
  const prevStep = () => {
    if (currentStep === 'companyInfo') setCurrentStep('founderInfo');
    else if (currentStep === 'fundingDetails') setCurrentStep('companyInfo');
    else if (currentStep === 'companyStatus') setCurrentStep('fundingDetails');
    else if (currentStep === 'documents') setCurrentStep('companyStatus');
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!consent) {
      setError('You must consent to share your documents with VCs to complete registration.');
      return;
    }
    setShowLoading(true);
    try {
      // Step 1: Upload each document file individually (if present)
      const fileUrls: {
        pitch_deck_file_url?: string;
        business_plan_file_url?: string;
        financial_model_file_url?: string;
        product_demo_file_url?: string;
      } = {};
      const uploadTasks: Promise<void>[] = [];
      const docTypes: Array<keyof DocumentUpload> = [
        'pitchDeck',
        'businessPlan',
        'financialModel',
        'productDemo',
      ];
      docTypes.forEach((type) => {
        const file = documents[type];
        if (file) {
          const uploadPromise = apiClient.uploadFiles<any>([file], companyInfo.companyName)
            .then((res) => {
              // API returns { cloud_url, company }
              if (res && res.cloud_url) {
                if (type === 'pitchDeck') fileUrls.pitch_deck_file_url = res.cloud_url;
                if (type === 'businessPlan') fileUrls.business_plan_file_url = res.cloud_url;
                if (type === 'financialModel') fileUrls.financial_model_file_url = res.cloud_url;
                if (type === 'productDemo') fileUrls.product_demo_file_url = res.cloud_url;
              }
            });
          uploadTasks.push(uploadPromise);
        }
      });
      // Wait for all uploads to finish
      await Promise.all(uploadTasks);
      // Step 2: Create the structured request payload according to the backend model
      const founderSignupPayload = {
        personal_info: {
          first_name: founderInfo.firstName,
          last_name: founderInfo.lastName,
          email: founderInfo.email,
          password: founderInfo.password,
          linkedin_url: founderInfo.linkedInUrl,
          role: founderInfo.role,
          phone_number: founderInfo.phoneNumber
        },
        company_info: {
          company_name: companyInfo.companyName,
          industry: companyInfo.industry,
          stage: companyInfo.stage,
          city: companyInfo.city,
          country: companyInfo.country
        },
        funding_details: {
          funding_amount: fundingDetails.fundingAmount,
          funding_purpose: fundingDetails.fundingPurpose,
          timeline: fundingDetails.timeline
        },
        company_status: {
          is_incorporated: companyStatus.isIncorporated,
          website_url: companyStatus.websiteUrl,
          description: companyStatus.description
        },
        documents: Object.keys(fileUrls).length > 0 ? fileUrls : undefined
      };
      // Step 3: Send the structured data to the founder signup endpoint
      const res = await apiClient.post<{
        token: string;
        email: string;
        first_name: string;
        last_name: string;
        user_type: string;
      }>('/auth/founder-signup', founderSignupPayload);
      // Step 4: Handle successful registration
      login({
        email: res.email,
        first_name: res.first_name,
        last_name: res.last_name,
        token: res.token,
        user_type: 'founder',
      });
      setShowLoading(false);
      navigate('/auth');
    } catch (err: any) {
      setShowLoading(false);
      console.error('Founder signup error:', err);
      setError(err.message || 'Signup failed');
    }
  };
  
  // Progress bar calculation
  const getProgressPercentage = () => {
    const steps = ['founderInfo', 'companyInfo', 'fundingDetails', 'companyStatus', 'documents'];
    const currentIndex = steps.indexOf(currentStep);
    return (currentIndex / (steps.length - 1)) * 100;
  };
  
  // Validation for each step
  const isFounderInfoValid = () => {
    return (
      founderInfo.firstName.trim() !== '' &&
      founderInfo.lastName.trim() !== '' &&
      founderInfo.email.trim() !== '' &&
      founderInfo.password.trim() !== '' &&
      founderInfo.linkedInUrl.trim() !== '' &&
      founderInfo.role.trim() !== '' &&
      founderInfo.phoneNumber.trim() !== ''
    );
  };

  const isCompanyInfoValid = () => {
    return (
      companyInfo.companyName.trim() !== '' &&
      companyInfo.industry.trim() !== '' &&
      companyInfo.stage.trim() !== '' &&
      companyInfo.city.trim() !== '' &&
      companyInfo.country.trim() !== ''
    );
  };

  const isFundingDetailsValid = () => {
    return (
      fundingDetails.fundingAmount.trim() !== '' &&
      fundingDetails.fundingPurpose.trim() !== '' &&
      fundingDetails.timeline.trim() !== ''
    );
  };

  const isCompanyStatusValid = () => {
    return (
      companyStatus.description.trim() !== ''
    );
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      {showLoading && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white bg-opacity-80">
          {/* Custom CSS animation */}
          <div className="relative flex flex-col items-center">
            <div className="w-24 h-24 flex items-center justify-center">
              <div className="absolute w-20 h-20 rounded-full border-4 border-indigo-300 animate-spin-slow border-t-indigo-600 border-b-transparent"></div>
              <div className="absolute w-14 h-14 rounded-full border-4 border-indigo-200 animate-spin-reverse border-b-indigo-400 border-t-transparent"></div>
              <div className="w-8 h-8 bg-indigo-500 rounded-full shadow-lg animate-pulse"></div>
            </div>
            <div className="mt-6 text-lg font-semibold text-indigo-700 animate-pulse text-center">
              Processing your registration...<br />
              <span className="text-base font-normal text-gray-700 animate-bounce mt-2 block">Documents are being processed</span>
            </div>
          </div>
        </div>
      )}
      <div className="max-w-2xl w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <a href="/" className="text-3xl font-bold text-purple hover:text-purple-dark transition-colors">
            Intersectx
          </a>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            Founder Registration
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            Already have an account?{' '}
            <a href="/auth" className="font-medium text-purple hover:text-purple-dark transition-colors">
              Sign in
            </a>
          </p>
        </div>
        
        {/* Progress bar */}
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className="bg-purple h-2.5 rounded-full transition-all duration-300" 
            style={{ width: `${getProgressPercentage()}%` }}
          ></div>
        </div>
        
        {/* Step indicator */}
        <div className="flex justify-between text-xs text-gray-600">
          <div className={currentStep === 'founderInfo' ? 'font-bold text-purple' : ''}>
            Founder Info
          </div>
          <div className={currentStep === 'companyInfo' ? 'font-bold text-purple' : ''}>
            Company Basics
          </div>
          <div className={currentStep === 'fundingDetails' ? 'font-bold text-purple' : ''}>
            Funding Details
          </div>
          <div className={currentStep === 'companyStatus' ? 'font-bold text-purple' : ''}>
            Company Status
          </div>
          <div className={currentStep === 'documents' ? 'font-bold text-purple' : ''}>
            Documents
          </div>
        </div>
        
        {/* Form Container */}
        <div className="mt-8 bg-white py-8 px-4 shadow-sm border border-purple-light/20 sm:rounded-lg sm:px-10">
          {error && (
            <div className="font-bold text-purple text-center text-sm font-medium">{error}</div>
          )}
          
          {/* Founder Information Form */}
          {currentStep === 'founderInfo' && (
            <form className="space-y-6">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
                    First name *
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <UserIcon className="h-5 w-5 text-purple-light" aria-hidden="true" />
                    </div>
                    <input
                      id="firstName"
                      name="firstName"
                      type="text"
                      required
                      value={founderInfo.firstName}
                      onChange={(e) => setFounderInfo({ ...founderInfo, firstName: e.target.value })}
                      className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-purple focus:border-purple transition-colors sm:text-sm"
                      placeholder="John"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
                    Last name *
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <UserIcon className="h-5 w-5 text-purple-light" aria-hidden="true" />
                    </div>
                    <input
                      id="lastName"
                      name="lastName"
                      type="text"
                      required
                      value={founderInfo.lastName}
                      onChange={(e) => setFounderInfo({ ...founderInfo, lastName: e.target.value })}
                      className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-purple focus:border-purple transition-colors sm:text-sm"
                      placeholder="Doe"
                    />
                  </div>
                </div>
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email address *
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <EnvelopeIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={founderInfo.email}
                    onChange={(e) => setFounderInfo({ ...founderInfo, email: e.target.value })}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-purple focus:border-purple transition-colors sm:text-sm"
                    placeholder="you@example.com"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password *
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockClosedIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="new-password"
                    required
                    value={founderInfo.password}
                    onChange={(e) => setFounderInfo({ ...founderInfo, password: e.target.value })}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-purple focus:border-purple transition-colors sm:text-sm"
                    placeholder="••••••••"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="linkedInUrl" className="block text-sm font-medium text-gray-700">
                  LinkedIn Profile URL *
                </label>
                <div className="mt-1">
                  <input
                    id="linkedInUrl"
                    name="linkedInUrl"
                    type="url"
                    required
                    value={founderInfo.linkedInUrl}
                    onChange={(e) => setFounderInfo({ ...founderInfo, linkedInUrl: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="https://linkedin.com/in/yourprofile"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                  Role/Title *
                </label>
                <div className="mt-1">
                  <input
                    id="role"
                    name="role"
                    type="text"
                    required
                    value={founderInfo.role}
                    onChange={(e) => setFounderInfo({ ...founderInfo, role: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="CEO, CTO, etc."
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700">
                  Phone Number *
                </label>
                <div className="mt-1">
                  <input
                    id="phoneNumber"
                    name="phoneNumber"
                    type="tel"
                    required
                    value={founderInfo.phoneNumber}
                    onChange={(e) => setFounderInfo({ ...founderInfo, phoneNumber: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="+1 (555) 123-4567"
                  />
                </div>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  onClick={nextStep}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!isFounderInfoValid()}
                >
                  Next
                </button>
              </div>
            </form>
          )}
          
          {/* Company Information Form */}
          {currentStep === 'companyInfo' && (
            <form className="space-y-6">
              <div>
                <label htmlFor="companyName" className="block text-sm font-medium text-gray-700">
                  Company Name *
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <BuildingOfficeIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                  </div>
                  <input
                    id="companyName"
                    name="companyName"
                    type="text"
                    required
                    value={companyInfo.companyName}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, companyName: e.target.value })}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-200 rounded-md focus:outline-none focus:ring-purple focus:border-purple transition-colors sm:text-sm"
                    placeholder="Startup Inc."
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="industry" className="block text-sm font-medium text-gray-700">
                  Industry/Sector *
                </label>
                <div className="mt-1">
                  <select
                    id="industry"
                    name="industry"
                    required
                    value={companyInfo.industry}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, industry: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    <option value="">Select an industry</option>
                    {industryOptions.map((option, index) => (
                      <option key={index} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div>
                <label htmlFor="stage" className="block text-sm font-medium text-gray-700">
                  Stage *
                </label>
                <div className="mt-1">
                  <select
                    id="stage"
                    name="stage"
                    required
                    value={companyInfo.stage}
                    onChange={(e) => setCompanyInfo({ ...companyInfo, stage: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    <option value="">Select a stage</option>
                    {stageOptions.map((option, index) => (
                      <option key={index} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="city" className="block text-sm font-medium text-gray-700">
                    City *
                  </label>
                  <div className="mt-1">
                    <input
                      id="city"
                      name="city"
                      type="text"
                      required
                      value={companyInfo.city}
                      onChange={(e) => setCompanyInfo({ ...companyInfo, city: e.target.value })}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="San Francisco"
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="country" className="block text-sm font-medium text-gray-700">
                    Country *
                  </label>
                  <div className="mt-1">
                    <input
                      id="country"
                      name="country"
                      type="text"
                      required
                      value={companyInfo.country}
                      onChange={(e) => setCompanyInfo({ ...companyInfo, country: e.target.value })}
                      className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="United States"
                    />
                  </div>
                </div>
              </div>
              
              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={prevStep}
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={nextStep}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!isCompanyInfoValid()}
                >
                  Next
                </button>
              </div>
            </form>
          )}
          
          {/* Funding Details Form */}
          {currentStep === 'fundingDetails' && (
            <form className="space-y-6">
              <div>
                <label htmlFor="fundingAmount" className="block text-sm font-medium text-gray-700">
                  Funding Amount Requested *
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <span className="text-gray-500 sm:text-sm">$</span>
                  </div>
                  <input
                    id="fundingAmount"
                    name="fundingAmount"
                    type="text"
                    required
                    value={fundingDetails.fundingAmount}
                    onChange={(e) => setFundingDetails({ ...fundingDetails, fundingAmount: e.target.value })}
                    className="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="1,000,000"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="fundingPurpose" className="block text-sm font-medium text-gray-700">
                  Funding Purpose *
                </label>
                <div className="mt-1">
                  <select
                    id="fundingPurpose"
                    name="fundingPurpose"
                    required
                    value={fundingDetails.fundingPurpose}
                    onChange={(e) => setFundingDetails({ ...fundingDetails, fundingPurpose: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    <option value="">Select a purpose</option>
                    {fundingPurposeOptions.map((option, index) => (
                      <option key={index} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div>
                <label htmlFor="timeline" className="block text-sm font-medium text-gray-700">
                  Timeline for Funding *
                </label>
                <div className="mt-1">
                  <select
                    id="timeline"
                    name="timeline"
                    required
                    value={fundingDetails.timeline}
                    onChange={(e) => setFundingDetails({ ...fundingDetails, timeline: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                  >
                    <option value="">Select a timeline</option>
                    {timelineOptions.map((option, index) => (
                      <option key={index} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
              
              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={prevStep}
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={nextStep}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!isFundingDetailsValid()}
                >
                  Next
                </button>
              </div>
            </form>
          )}
          
          {/* Company Status Form */}
          {currentStep === 'companyStatus' && (
            <form className="space-y-6">
              <div>
                <div className="flex items-center">
                  <input
                    id="isIncorporated"
                    name="isIncorporated"
                    type="checkbox"
                    checked={companyStatus.isIncorporated}
                    onChange={(e) => setCompanyStatus({ ...companyStatus, isIncorporated: e.target.checked })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="isIncorporated" className="ml-2 block text-sm font-medium text-gray-700">
                    Company is incorporated
                  </label>
                </div>
              </div>
              
              <div>
                <label htmlFor="websiteUrl" className="block text-sm font-medium text-gray-700">
                  Website URL (optional)
                </label>
                <div className="mt-1">
                  <input
                    id="websiteUrl"
                    name="websiteUrl"
                    type="url"
                    value={companyStatus.websiteUrl}
                    onChange={(e) => setCompanyStatus({ ...companyStatus, websiteUrl: e.target.value })}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="https://yourcompany.com"
                  />
                </div>
              </div>
              
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Brief Company Description (2-3 sentences) *
                </label>
                <div className="mt-1">
                  <textarea
                    id="description"
                    name="description"
                    required
                    value={companyStatus.description}
                    onChange={(e) => setCompanyStatus({ ...companyStatus, description: e.target.value })}
                    rows={3}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Briefly describe what your company does and your value proposition"
                  />
                </div>
              </div>
              
              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={prevStep}
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="button"
                  onClick={nextStep}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!isCompanyStatusValid()}
                >
                  Next
                </button>
              </div>
            </form>
          )}
          
          {/* Documents Upload Form */}
          {currentStep === 'documents' && (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div className="bg-gray-50 p-4 rounded-md">
                <p className="text-sm text-gray-700 mb-4">
                  These documents are optional, but will help investors understand your business better.
                </p>
                
                <div className="space-y-4">
                  <div>
                    <label htmlFor="pitchDeck" className="block text-sm font-medium text-gray-700">
                      Pitch Deck (PDF)
                    </label>
                    <div className="mt-1 flex items-center">
                      <input
                        id="pitchDeck"
                        name="pitchDeck"
                        type="file"
                        accept=".pdf"
                        onChange={(e) => handleFileUpload(e, 'pitchDeck')}
                        className="block w-full text-sm text-gray-500
                          file:mr-4 file:py-2 file:px-4
                          file:rounded-md file:border-0
                          file:text-sm file:font-medium
                          file:bg-indigo-50 file:text-indigo-700
                          hover:file:bg-indigo-100"
                      />
                      {documents.pitchDeck && (
                        <span className="ml-2 text-sm text-indigo-600">
                          <DocumentTextIcon className="h-5 w-5 inline" /> {documents.pitchDeck.name}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="businessPlan" className="block text-sm font-medium text-gray-700">
                      Business Plan (PDF)
                    </label>
                    <div className="mt-1 flex items-center">
                      <input
                        id="businessPlan"
                        name="businessPlan"
                        type="file"
                        accept=".pdf"
                        onChange={(e) => handleFileUpload(e, 'businessPlan')}
                        className="block w-full text-sm text-gray-500
                          file:mr-4 file:py-2 file:px-4
                          file:rounded-md file:border-0
                          file:text-sm file:font-medium
                          file:bg-indigo-50 file:text-indigo-700
                          hover:file:bg-indigo-100"
                      />
                      {documents.businessPlan && (
                        <span className="ml-2 text-sm text-indigo-600">
                          <DocumentTextIcon className="h-5 w-5 inline" /> {documents.businessPlan.name}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="financialModel" className="block text-sm font-medium text-gray-700">
                      Financial Model (PDF/Excel)
                    </label>
                    <div className="mt-1 flex items-center">
                      <input
                        id="financialModel"
                        name="financialModel"
                        type="file"
                        accept=".pdf,.xlsx,.xls"
                        onChange={(e) => handleFileUpload(e, 'financialModel')}
                        className="block w-full text-sm text-gray-500
                          file:mr-4 file:py-2 file:px-4
                          file:rounded-md file:border-0
                          file:text-sm file:font-medium
                          file:bg-indigo-50 file:text-indigo-700
                          hover:file:bg-indigo-100"
                      />
                      {documents.financialModel && (
                        <span className="ml-2 text-sm text-indigo-600">
                          <DocumentTextIcon className="h-5 w-5 inline" /> {documents.financialModel.name}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <div>
                    <label htmlFor="productDemo" className="block text-sm font-medium text-gray-700">
                      Product Demo/Screenshots (PDF)
                    </label>
                    <div className="mt-1 flex items-center">
                      <input
                        id="productDemo"
                        name="productDemo"
                        type="file"
                        accept=".pdf,.png,.jpg,.jpeg"
                        onChange={(e) => handleFileUpload(e, 'productDemo')}
                        className="block w-full text-sm text-gray-500
                          file:mr-4 file:py-2 file:px-4
                          file:rounded-md file:border-0
                          file:text-sm file:font-medium
                          file:bg-indigo-50 file:text-indigo-700
                          hover:file:bg-indigo-100"
                      />
                      {documents.productDemo && (
                        <span className="ml-2 text-sm text-indigo-600">
                          <DocumentTextIcon className="h-5 w-5 inline" /> {documents.productDemo.name}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex items-center mt-6">
                <input
                  id="consent"
                  name="consent"
                  type="checkbox"
                  checked={consent}
                  onChange={e => setConsent(e.target.checked)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  required
                />
                <label htmlFor="consent" className="ml-2 block text-sm text-gray-700">
                  I consent to share my uploaded documents with any VCs I connect to on Intersectx.
                </label>
              </div>
              
              <div className="flex justify-between">
                <button
                  type="button"
                  onClick={prevStep}
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Back
                </button>
                <button
                  type="submit"
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!consent}
                >
                  Complete Registration
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}

<style>
{`
@keyframes spin-slow {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
@keyframes spin-reverse {
  0% { transform: rotate(360deg); }
  100% { transform: rotate(0deg); }
}
.animate-spin-slow {
  animation: spin-slow 2s linear infinite;
}
.animate-spin-reverse {
  animation: spin-reverse 3s linear infinite;
}
`}
</style> 