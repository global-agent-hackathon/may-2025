import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import { 
  BanknotesIcon, 
  UsersIcon, 
  ChartBarIcon, 
  ExclamationTriangleIcon,
  HeartIcon,
  ShieldCheckIcon,
  Square3Stack3DIcon,
  ArrowTopRightOnSquareIcon,
  DocumentTextIcon,
  ChevronDownIcon,
  MagnifyingGlassIcon
} from '@heroicons/react/24/outline';
import Chart from '../components/ui/Chart';
import { 
  formatRevenueData, 
  formatExpensesData, 
  formatFundingData, 
  formatMarginsData,
  formatCurrency
} from '../lib/formatChartData';
import type { CompanyAnalysisData } from '../types/CompanyAnalysis';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../lib/api-client';

// Create a reusable IframeWithFullscreen component
function IframeWithFullscreen({ src, title, height = '300px' }: { src: string, title: string, height?: string }) {
  return (
    <div className="relative w-full overflow-hidden rounded-xl shadow-sm">
      <iframe 
        src={src}
        className="w-full border-0 rounded-xl"
        style={{ height }}
        title={title}
        sandbox="allow-scripts allow-same-origin"
      />
      <button 
        onClick={() => window.open(src, '_blank')}
        className="absolute top-2 right-2 bg-white rounded-full p-1.5 shadow-md hover:bg-gray-100 transition-colors duration-200 z-10"
        title="View full visualization"
        aria-label="View full visualization"
      >
        <ArrowTopRightOnSquareIcon className="w-5 h-5 text-gray-600" />
      </button>
    </div>
  );
}

// Utility to convert to Camel Case
function toCamelCase(str: string) {
  return str
    .split(' ')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join(' ');
}

export default function CompanyAnalysisPage() {
  // Get params from both route patterns
  const { companyName, id } = useParams<{ companyName?: string; id?: string }>();
  const [companyData, setCompanyData] = useState<CompanyAnalysisData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  // State for expanded sections if needed in the future
  // const [expandedSection, setExpandedSection] = useState<string | null>(null);

  // Sidebar navigation state
  const sectionList = [
    { key: 'finance', label: 'Financial Analysis', icon: <BanknotesIcon className="w-5 h-5" />, disabled: false },
    { key: 'team', label: 'Team Analysis', icon: <UsersIcon className="w-5 h-5" />, disabled: false },
    { key: 'market', label: 'Market Analysis', icon: <ChartBarIcon className="w-5 h-5" />, disabled: false },
    { key: 'risk', label: 'Risk Analysis', icon: <ExclamationTriangleIcon className="w-5 h-5" />, disabled: true },
    { key: 'sentiment', label: 'Customer Sentiment', icon: <HeartIcon className="w-5 h-5" />, disabled: true },
    { key: 'partnership', label: 'Partnership Network', icon: <Square3Stack3DIcon className="w-5 h-5" />, disabled: true },
    { key: 'compliance', label: 'Regulatory Compliance', icon: <ShieldCheckIcon className="w-5 h-5" />, disabled: true },
  ];
  const [activeSection, setActiveSection] = useState<string>('finance');

  // Handler for expanding sections if needed in the future
  // const handleExpand = (section: string) => {
  //   setExpandedSection(prev => (prev === section ? null : section));
  // };

  const { user } = useAuth();
  const [connectedCompanies, setConnectedCompanies] = useState<string[]>([]);
  const [docUrls, setDocUrls] = useState<{
    pitch_deck_file_url?: string | null;
    business_plan_file_url?: string | null;
    financial_model_file_url?: string | null;
    product_demo_file_url?: string | null;
  }>({});
  const [deepResearchLoading, setDeepResearchLoading] = useState(false);
  const [documentsDropdownOpen, setDocumentsDropdownOpen] = useState(false);

  useEffect(() => {
    const fetchCompanyAnalysis = async () => {
      // Use either companyName or id parameter
      const companyIdentifier = companyName || id;
      
      if (!companyIdentifier) {
        setError('No company identifier provided');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        // Use the appropriate endpoint based on the route pattern
        const endpoint = companyName 
          ? `${import.meta.env.VITE_BACKEND_URL}/companies/${encodeURIComponent(companyName)}/analysis`
          : `${import.meta.env.VITE_BACKEND_URL}/companies/${encodeURIComponent(id!)}/analysis`;
        
        console.log('Fetching from:', endpoint);
        const response = await axios.get(endpoint);
        
        if (!response.data) {
          throw new Error('No company data found');
        }

        console.log('API response:', response.data);
        setCompanyData(response.data);
        setIsLoading(false);
      } catch (err: unknown) {
        console.error('Company analysis fetch error:', err);
        let errorMessage = 'Failed to fetch company analysis';
        
        if (err && typeof err === 'object' && 'response' in err && 
            err.response && typeof err.response === 'object' && 
            'data' in err.response && err.response.data && 
            typeof err.response.data === 'object' && 
            'message' in err.response.data && 
            typeof err.response.data.message === 'string') {
          errorMessage = err.response.data.message;
        }
        
        setError(errorMessage);
        setIsLoading(false);
        setCompanyData(null); // Use null instead of empty object
      }
    };

    if (companyName || id) {
      fetchCompanyAnalysis();
    }
  }, [companyName, id]);

  useEffect(() => {
    if (user?.user_type === 'vc' && user?.email) {
      apiClient.get(`/auth/vc-connected-companies?email=${encodeURIComponent(user.email)}`)
        .then((data) => {
          const resp = data as { connected_companies?: string[] };
          if (resp && Array.isArray(resp.connected_companies)) {
            setConnectedCompanies(resp.connected_companies.map((c: string) => c.toLowerCase()));
          } else {
            setConnectedCompanies([]);
          }
        })
        .catch(() => setConnectedCompanies([]));
    }
  }, [user?.user_type, user?.email]);

  useEffect(() => {
    // Fetch document URLs if VC and connected
    if (
      user?.user_type === 'vc' &&
      companyData?.company_name &&
      connectedCompanies.includes(companyData.company_name.toLowerCase())
    ) {
      apiClient.get(`/files/get-files/${encodeURIComponent(companyData.company_name)}`)
        .then((data) => {
          setDocUrls(data || {});
        })
        .catch(() => setDocUrls({}));
    } else {
      setDocUrls({});
    }
  }, [user?.user_type, companyData?.company_name, connectedCompanies]);

  const handleDeepResearch = async () => {
    if (!companyData?.company_name) return;
    setDeepResearchLoading(true);
    try {
      const response = await apiClient.get(`/research/${encodeURIComponent(companyData.company_name)}`);
      if (response && typeof response === 'object' && 'finance' in response && 'linkedin_team' in response) {
        // Preserve the original company description if it exists
        const originalDescription = companyData?.linkedin_team?.team_overview?.company_description;
        const newData = { ...response } as CompanyAnalysisData;
        if (
          originalDescription &&
          newData.linkedin_team &&
          typeof newData.linkedin_team === 'object' &&
          'team_overview' in newData.linkedin_team &&
          newData.linkedin_team.team_overview &&
          typeof newData.linkedin_team.team_overview === 'object'
        ) {
          (newData.linkedin_team.team_overview as { company_description?: string }).company_description = originalDescription;
        }
        setCompanyData(newData);
      } else {
        // Optionally handle unexpected response
      }
    } catch (err) {
      // Optionally handle error
    } finally {
      setDeepResearchLoading(false);
    }
  };

// Fixed Loading state
if (isLoading) {
  return (
    <div className="min-h-screen w-[100%] bg-gray-50">
      
        {/* Loading Header Card */}
        <div className="bg-white border-0 shadow-sm rounded-2xl p-8 flex flex-col md:flex-row md:items-center gap-6 mb-8 w-full">
          <div className="w-20 h-20 bg-purple-light/20 rounded-2xl animate-pulse flex-shrink-0"></div>
          <div className="flex-1 min-w-0">
            <div className="h-6 bg-gray-200 rounded w-3/4 mb-4 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2 animate-pulse"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3 mb-4 animate-pulse"></div>
            <div className="flex flex-wrap gap-3">
              <div className="h-8 w-32 bg-gray-200 rounded-full animate-pulse"></div>
              <div className="h-8 w-40 bg-gray-200 rounded-full animate-pulse"></div>
              <div className="h-8 w-36 bg-gray-200 rounded-full animate-pulse"></div>
            </div>
          </div>
          <div className="flex flex-col md:flex-row items-center gap-3 mt-4 md:mt-0 flex-shrink-0">
            <div className="h-10 w-36 bg-gray-200 rounded-lg animate-pulse"></div>
            <div className="h-10 w-32 bg-gray-200 rounded-lg animate-pulse"></div>
          </div>
        </div>

        <div className="flex gap-8 w-full mt-8">
          {/* Sidebar Loading */}
          <div className="w-56 flex-shrink-0 hidden md:block">
            <div className="sticky top-24 space-y-2">
              {[...Array(7)].map((_, i) => (
                <div key={i} className="h-12 bg-gray-200 rounded-lg animate-pulse"></div>
              ))}
            </div>
          </div>
          
          {/* Main Content Loading */}
          <div className="flex-1 min-w-0 w-full">
            <div className="space-y-10 w-full">
              {/* Loading Cards */}
              {[...Array(3)].map((_, i) => (
                <div key={i} className="bg-white rounded-2xl shadow-md border border-gray-200 p-8 flex flex-col md:flex-row gap-8 w-full animate-pulse">
                  <div className="md:w-1/2 w-full h-64 bg-gray-200 rounded-xl flex-shrink-0"></div>
                  <div className="flex-1 min-w-0">
                    <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                    <div className="flex flex-wrap gap-3 mb-4">
                      <div className="h-8 w-32 bg-gray-200 rounded-full"></div>
                      <div className="h-8 w-28 bg-gray-200 rounded-full"></div>
                    </div>
                    <div className="h-3 bg-gray-200 rounded w-1/4 mb-4"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/3 mb-2"></div>
                    <div className="space-y-2">
                      <div className="h-3 bg-gray-200 rounded w-full"></div>
                      <div className="h-3 bg-gray-200 rounded w-full"></div>
                      <div className="h-3 bg-gray-200 rounded w-3/4"></div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
      </div>
    </div>
  );
}

  // Error state
  if (!isLoading && error) {
    return (
      <div className="min-h-screen bg-off-white flex items-center justify-center">
        <div className="text-center bg-white p-8 rounded-2xl shadow-sm max-w-md">
          <h1 className="text-2xl font-bold text-primary mb-4">Error Loading Data</h1>
          <p className="text-secondary mb-6">{error}</p>
          <button 
            className="px-4 py-2 bg-purple text-white rounded-md hover:bg-purple-dark transition-colors"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // If no data is available, return null
  if (!companyData && !isLoading) {
    return null;
  }

  return (
    <div className="min-h-screen bg-off-white pb-8 w-full">
      {/* Main Header Card */}
      <div className="bg-white border-0 shadow-sm rounded-2xl p-8 flex flex-col md:flex-row md:items-center gap-6 mb-8 w-full">
        <div className="w-20 h-20 bg-purple-light/20 rounded-2xl flex items-center justify-center text-4xl font-bold text-purple-dark">
          {companyData?.company_name ? toCamelCase(companyData.company_name).charAt(0) : ''}
        </div>
        <div className="flex-1">
          <div className="text-secondary mb-2 text-lg font-medium">
            {companyData?.linkedin_team?.team_overview?.company_description || 'No company description available.'}
          </div>
          <div className="flex flex-wrap gap-3 text-sm">
            {companyData?.linkedin_team?.team_overview?.locations && companyData.linkedin_team.team_overview.locations.length > 0 && (
              <span className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full font-medium">
                {companyData.linkedin_team.team_overview.locations[0]}
              </span>
            )}
            {typeof companyData?.finance?.funding?.total_funding === 'number' && !isNaN(companyData.finance.funding.total_funding) && (
              <span className="bg-purple-50 text-purple-700 px-3 py-1 rounded-full font-medium">
                Funding: ${ (companyData.finance.funding.total_funding).toFixed(1) }M
              </span>
            )}
            {companyData?.linkedin_team?.team_overview?.total_employees && (
              <span className="bg-purple-light/20 text-purple px-3 py-1 rounded-full font-medium">
                Employees: {companyData.linkedin_team.team_overview.total_employees}
              </span>
            )}
          </div>
        </div>
        <div className="flex flex-col md:flex-row items-center gap-3 mt-4 md:mt-0">
          {/* Show Deep Research button only for VC users and only if connected to this company */}
          {user?.user_type === 'vc' && companyData?.company_name && connectedCompanies.includes(companyData.company_name.toLowerCase()) && (
            <>
              <button
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg flex items-center gap-2 hover:bg-indigo-700 transition-colors w-full md:w-auto disabled:opacity-60 disabled:cursor-not-allowed"
                onClick={handleDeepResearch}
                disabled={deepResearchLoading}
              >
                {deepResearchLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5 mr-2 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>
                    </svg>
                    Processing...
                  </>
                ) : (
                  <>
                    <MagnifyingGlassIcon className="w-5 h-5" />
                    Deep Research
                  </>
                )}
              </button>
              <div className="relative w-full md:w-auto">
                <button 
                  className="px-4 py-2 bg-gray-100 text-primary rounded-lg flex items-center justify-between gap-2 hover:bg-purple-light/10 transition-colors w-full"
                  onClick={() => setDocumentsDropdownOpen(!documentsDropdownOpen)}
                  aria-expanded={documentsDropdownOpen}
                  aria-haspopup="true"
                >
                  <div className="flex items-center gap-2">
                    <DocumentTextIcon className="w-5 h-5" />
                    Documents
                  </div>
                  <ChevronDownIcon className="w-4 h-4" />
                </button>
                {documentsDropdownOpen && (
                  <div className="absolute right-0 mt-2 w-60 bg-white rounded-lg shadow-lg overflow-hidden z-20 border border-gray-200">
                    <div className="py-2">
                      <a
                        href={docUrls.pitch_deck_file_url || undefined}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block px-4 py-2 text-sm ${docUrls.pitch_deck_file_url ? 'text-primary hover:bg-purple-light/10 hover:text-purple' : 'text-gray-400 cursor-not-allowed'}`}
                        tabIndex={docUrls.pitch_deck_file_url ? 0 : -1}
                        aria-disabled={!docUrls.pitch_deck_file_url}
                      >
                        Pitch Deck File
                      </a>
                      <a
                        href={docUrls.business_plan_file_url || undefined}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block px-4 py-2 text-sm ${docUrls.business_plan_file_url ? 'text-primary hover:bg-purple-light/10 hover:text-purple' : 'text-gray-400 cursor-not-allowed'}`}
                        tabIndex={docUrls.business_plan_file_url ? 0 : -1}
                        aria-disabled={!docUrls.business_plan_file_url}
                      >
                        Business Plan File
                      </a>
                      <a
                        href={docUrls.financial_model_file_url || undefined}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block px-4 py-2 text-sm ${docUrls.financial_model_file_url ? 'text-primary hover:bg-purple-light/10 hover:text-purple' : 'text-gray-400 cursor-not-allowed'}`}
                        tabIndex={docUrls.financial_model_file_url ? 0 : -1}
                        aria-disabled={!docUrls.financial_model_file_url}
                      >
                        Finance Model File
                      </a>
                      <a
                        href={docUrls.product_demo_file_url || undefined}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`block px-4 py-2 text-sm ${docUrls.product_demo_file_url ? 'text-primary hover:bg-purple-light/10 hover:text-purple' : 'text-gray-400 cursor-not-allowed'}`}
                        tabIndex={docUrls.product_demo_file_url ? 0 : -1}
                        aria-disabled={!docUrls.product_demo_file_url}
                      >
                        Product Demo File
                      </a>
                    </div>
                  </div>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="flex gap-8 w-full mt-8">
        {/* Sidebar Navigation */}
        <aside className="w-56 flex-shrink-0 hidden md:block">
          <nav className="sticky top-24 space-y-2 p-3 bg-gradient-to-b from-purple-light/10 to-off-white rounded-lg border border-purple-light/20 shadow-sm">
            {/* Section title */}
            <div className="mb-3 pb-2 border-b border-gray-200">
              <h3 className="text-sm font-medium text-primary">Analysis Sections</h3>
            </div>
            {sectionList.map(section => (
              <button 
                key={section.key}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg text-left font-medium transition-colors ${
                  section.disabled 
                    ? 'text-gray-400 cursor-not-allowed' 
                    : activeSection === section.key 
                      ? 'bg-purple-light/10 text-purple-dark shadow-sm' 
                      : 'text-primary hover:bg-gray-100'
                }`}
                onClick={() => !section.disabled && setActiveSection(section.key)}
                disabled={section.disabled}
                title={section.disabled ? 'This feature is not yet implemented' : ''}
              >
                {section.icon}
                <div className="flex flex-col">
                  {section.label}
                  {section.disabled && <span className="text-xs text-gray-500 mt-0.5">(Coming soon)</span>}
                </div>
              </button>
            ))}
          </nav>
        </aside>
        {/* Main Content Area */}
        <main className="flex-1 min-w-0 w-full">
          {/* Section Content */}
          {activeSection === 'finance' && companyData?.finance && (
            <section className="space-y-10 mx-4 md:mx-6 lg:mx-8">
              {/* Revenue */}
              {companyData.finance.revenue && (
                <div className="bg-white rounded-2xl shadow-lg border border-gray-200 p-8 flex flex-col md:flex-row gap-8 w-full">
                  {/* Chart left, details right */}
                  <div className="md:w-1/2 w-full flex items-center justify-center">
                    {companyData.finance.revenue.iframe_url ? (
                      <IframeWithFullscreen
                        src={companyData.finance.revenue.iframe_url}
                        title={`Revenue Trends - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="400px"
                      />
                    ) : (
                      <Chart
                        type="line"
                        title="Revenue Over Time"
                        description="Historical revenue performance"
                        data={formatRevenueData(companyData.finance.revenue)}
                      />
                    )}
                  </div>
                  <div className="flex-1">
                    <div className="mb-2 text-xl font-bold text-primary">Revenue</div>
                    <div className="text-secondary mb-3 text-base font-medium">{companyData.finance.revenue.summary || 'No summary available.'}</div>
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <span className="bg-purple-light/10 text-purple-dark px-3 py-1 rounded-full font-medium">
                        Financial Analysis
                      </span>
                      <span className="bg-purple-light/20 text-purple px-3 py-1 rounded-full font-medium">
                        Revenue Trends
                      </span>
                    </div>
                    <div className="text-xs text-secondary mb-2">Last updated: {companyData.finance.revenue.last_updated ? new Date(companyData.finance.revenue.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {companyData.finance.revenue.citations && companyData.finance.revenue.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-secondary mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.finance.revenue.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
              {/* Funding */}
              {companyData.finance.funding && (
                <div className="bg-white rounded-2xl shadow-sm p-8 flex flex-col md:flex-row gap-8 w-full border border-gray-200">
                  {/* Details left, chart right */}
                  <div className="flex-1 order-2 md:order-1">
                    <div className="mb-2 text-xl font-bold text-primary">Funding</div>
                    <div className="text-secondary mb-3 text-base font-medium">{companyData.finance.funding.summary || 'No summary available.'}</div>
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <span className="bg-purple-light/10 text-purple-dark px-3 py-1 rounded-full font-medium">
                        Total Funding: {companyData.finance.funding.total_funding ? formatCurrency(companyData.finance.funding.total_funding) : 'N/A'}
                      </span>
                      <span className="bg-purple-light/20 text-purple px-3 py-1 rounded-full font-medium">
                        Funding Rounds
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mb-2">Last updated: {companyData.finance.funding.last_updated ? new Date(companyData.finance.funding.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {companyData.finance.funding.citations && companyData.finance.funding.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.finance.funding.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
                        </div>
                  )}
                        </div>
                  <div className="md:w-1/2 w-full flex items-center justify-center order-1 md:order-2">
                    {companyData.finance.funding.iframe_url ? (
                            <IframeWithFullscreen 
                              src={companyData.finance.funding.iframe_url}
                        title={`Funding History - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="400px"
                            />
                    ) : (
                          <Chart 
                            type="bar" 
                            title="Funding Rounds"
                            description="Historical funding rounds"
                            data={formatFundingData(companyData.finance.funding)}
                          />
                        )}
                  </div>
                </div>
              )}
              {/* Expenses */}
              {companyData.finance.expenses && (
                <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8 w-full">
                  {/* Chart left, details right */}
                  <div className="md:w-1/2 w-full flex items-center justify-center">
                    {companyData.finance.expenses.iframe_url ? (
                            <IframeWithFullscreen 
                              src={companyData.finance.expenses.iframe_url}
                        title={`Expense Categories - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="400px"
                            />
                    ) : (
                          <Chart 
                            type="pie" 
                            title="Expense Breakdown"
                            description="Distribution of expenses by category"
                            data={formatExpensesData(companyData.finance.expenses)}
                          />
                        )}
                  </div>
                  <div className="flex-1">
                    <div className="mb-2 text-xl font-bold text-gray-900">Expenses</div>
                    <div className="text-gray-700 mb-3 text-base font-medium">{companyData.finance.expenses.summary || 'No summary available.'}</div>
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <span className="bg-orange-50 text-orange-700 px-3 py-1 rounded-full font-medium">
                        Expense Analysis
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mb-2">Last updated: {companyData.finance.expenses.last_updated ? new Date(companyData.finance.expenses.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {companyData.finance.expenses.citations && companyData.finance.expenses.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.finance.expenses.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              )}
              {/* Margins */}
              {companyData.finance.margins && (
                <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8 w-full">
                  {/* Details left, chart right */}
                  <div className="flex-1 order-2 md:order-1">
                    <div className="mb-2 text-xl font-bold text-gray-900">Profit Margins</div>
                    <div className="text-gray-700 mb-3 text-base font-medium">{companyData.finance.margins.summary || 'No summary available.'}</div>
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <span className="bg-purple-light/20 text-purple px-3 py-1 rounded-full font-medium">
                        Margin Analysis
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mb-2">Last updated: {companyData.finance.margins.last_updated ? new Date(companyData.finance.margins.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {companyData.finance.margins.citations && companyData.finance.margins.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.finance.margins.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                  <div className="md:w-1/2 w-full flex items-center justify-center order-1 md:order-2">
                    {companyData.finance.margins.iframe_url ? (
                            <IframeWithFullscreen 
                              src={companyData.finance.margins.iframe_url}
                        title={`Profit Margins - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="400px"
                            />
                    ) : (
                          <Chart 
                            type="bar" 
                            title="Profit Margins"
                            description="Profit margin breakdown"
                            data={formatMarginsData(companyData.finance.margins)}
                          />
                        )}
                  </div>
                </div>
              )}
              {/* Valuation */}
              {companyData.finance.valuation && (
                <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8 w-full">
                  {/* Chart left, details right */}
                  <div className="md:w-1/2 w-full flex items-center justify-center">
                    {companyData.finance.valuation.iframe_url ? (
                            <IframeWithFullscreen 
                              src={companyData.finance.valuation.iframe_url}
                        title={`Valuation History - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="400px"
                            />
                    ) : null}
                  </div>
                  <div className="flex-1">
                    <div className="mb-2 text-xl font-bold text-gray-900">Valuation</div>
                    <div className="text-gray-700 mb-3 text-base font-medium">{companyData.finance.valuation.summary || 'No summary available.'}</div>
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <span className="bg-indigo-50 text-indigo-700 px-3 py-1 rounded-full font-medium">
                        Valuation Analysis
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 mb-2">Last updated: {companyData.finance.valuation.last_updated ? new Date(companyData.finance.valuation.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {companyData.finance.valuation.citations && companyData.finance.valuation.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.finance.valuation.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
                    </div>
                  )}
              </div>
            </div>
          )}
            </section>
          )}

          {/* Repeat for other sections: Team, Market, Risk, Sentiment, Partnership, Compliance */}
          {activeSection === 'team' && companyData?.linkedin_team && (
            <section className="space-y-10 mx-4 md:mx-6 lg:mx-8">
              {/* Team Overview Card */}
              {companyData.linkedin_team.team_overview && (
                <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8 w-full">
                  {/* Optional Iframe/Chart */}
                  {companyData.linkedin_team.team_overview.iframe_url && (
                    <div className="md:w-1/2 w-full flex items-center justify-center">
                          <IframeWithFullscreen 
                            src={companyData.linkedin_team.team_overview.iframe_url}
                        title={`Team Overview - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                  )}
                  <div className="flex-1">
                    <div className="mb-2 text-xl font-bold text-gray-900">Team Overview</div>
                    <div className="text-gray-700 mb-3 text-base font-medium">
                      {companyData.linkedin_team.team_overview.company_description || 'No team description available.'}
                        </div>
                    <div className="flex flex-wrap gap-4 mb-3 text-sm">
                      <span className="bg-purple-light/20 text-purple px-3 py-1 rounded-full font-medium">
                        Employees: {companyData.linkedin_team.team_overview.total_employees}
                            </span>
                      <span className="bg-green-50 text-green-700 px-3 py-1 rounded-full font-medium">
                        Growth Rate: {companyData.linkedin_team.team_overview.growth_rate ? `${companyData.linkedin_team.team_overview.growth_rate}%` : 'N/A'}
                            </span>
                      {companyData.linkedin_team.team_overview.locations && companyData.linkedin_team.team_overview.locations.length > 0 && (
                        <span className="bg-gray-100 text-primary px-3 py-1 rounded-full font-medium">
                          {companyData.linkedin_team.team_overview.locations.join(', ')}
                        </span>
                      )}
                    </div>
                    {companyData.linkedin_team.team_overview.key_hiring_areas && companyData.linkedin_team.team_overview.key_hiring_areas.length > 0 && (
                      <div className="mb-3">
                        <span className="font-semibold text-xs text-gray-700 mr-2">Key Hiring Areas:</span>
                        <span className="text-xs text-gray-600">{companyData.linkedin_team.team_overview.key_hiring_areas.join(', ')}</span>
            </div>
          )}
                    <div className="text-xs text-gray-500 mb-2">Last updated: {companyData.linkedin_team.team_overview.last_updated ? new Date(companyData.linkedin_team.team_overview.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {/* Citations */}
                    {companyData.linkedin_team.team_overview.citations && companyData.linkedin_team.team_overview.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.linkedin_team.team_overview.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
                        </div>
                    )}
                          </div>
                        </div>
                      )}
              {/* Org Structure Card */}
              {companyData.linkedin_team.org_structure && (
                <div className="bg-white rounded-2xl shadow-lg p-8 w-full">
                  <div className="mb-2 text-xl font-bold text-gray-900">Org Structure</div>
                  <div className="mb-3 text-base text-gray-700 font-medium">CEO: {companyData.linkedin_team.org_structure.ceo}</div>
                  {companyData.linkedin_team.org_structure.departments && companyData.linkedin_team.org_structure.departments.length > 0 && (
                    <div className="mb-3">
                      <span className="font-semibold text-xs text-gray-700 mr-2">Departments:</span>
                      <span className="text-xs text-gray-600">{companyData.linkedin_team.org_structure.departments.map(dep => dep.name).join(', ')}</span>
                    </div>
                  )}
                  {companyData.linkedin_team.org_structure.leadership_team && companyData.linkedin_team.org_structure.leadership_team.length > 0 && (
                    <div className="mb-3">
                      <span className="font-semibold text-xs text-gray-700 mr-2">Leadership Team:</span>
                      <span className="text-xs text-gray-600">{companyData.linkedin_team.org_structure.leadership_team.map(lead => `${lead.name} (${lead.title})`).join(', ')}</span>
                        </div>
                  )}
                  {/* Org Chart (if available) */}
                  {companyData.linkedin_team.org_structure.iframe_url && (
                    <div className="w-full flex items-center justify-center mt-4">
                          <IframeWithFullscreen 
                        src={companyData.linkedin_team.org_structure.iframe_url}
                        title={`Org Chart - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                      )}
                        </div>
                      )}
              {/* Team Growth Card */}
              {companyData.linkedin_team.team_growth && (
                <div className="bg-white rounded-2xl shadow-lg p-8 w-full">
                  <div className="mb-2 text-xl font-bold text-gray-900">Team Growth</div>
                  <div className="mb-3 text-base text-gray-700 font-medium">
                    Net Growth: {companyData.linkedin_team.team_growth.net_growth ?? 'N/A'} | Annualized Growth Rate: {companyData.linkedin_team.team_growth.growth_rate_annualized ? `${companyData.linkedin_team.team_growth.growth_rate_annualized}%` : 'N/A'}
                  </div>
                  {companyData.linkedin_team.team_growth.key_hiring_areas && companyData.linkedin_team.team_growth.key_hiring_areas.length > 0 && (
                    <div className="mb-3">
                      <span className="font-semibold text-xs text-gray-700 mr-2">Key Hiring Areas:</span>
                      <span className="text-xs text-gray-600">{companyData.linkedin_team.team_growth.key_hiring_areas.join(', ')}</span>
                    </div>
                  )}
                  {/* Team Growth Chart (if available) */}
                  {companyData.linkedin_team.team_growth.iframe_url && (
                    <div className="w-full flex items-center justify-center mt-4">
                          <IframeWithFullscreen 
                        src={companyData.linkedin_team.team_growth.iframe_url}
                        title={`Team Growth - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                      )}
                    </div>
              )}
              {/* Key People Card */}
              {companyData.linkedin_team.individual_performance && (
                <div className="bg-white rounded-2xl shadow-lg p-8 w-full">
                  <div className="mb-2 text-xl font-bold text-gray-900">Key People</div>
                  <div className="flex flex-wrap gap-6">
                    {/* If individual_performance is an array, map over it. If not, render single. */}
                    {Array.isArray(companyData.linkedin_team.individual_performance)
                      ? companyData.linkedin_team.individual_performance.map((person, idx) => (
                          <div key={idx} className="flex flex-col items-center w-48 p-4 bg-gray-50 rounded-xl shadow border border-gray-100">
                            {person.image_url && (
                              <img src={person.image_url} alt={person.individual_name} className="w-16 h-16 rounded-full object-cover mb-2" />
                            )}
                            <div className="font-semibold text-gray-900 text-base mb-1">{person.individual_name}</div>
                            <div className="text-xs text-gray-600 mb-1">{person.title}</div>
                            <div className="text-xs text-gray-500 mb-1">Tenure: {person.tenure_years ? `${person.tenure_years} yrs` : 'N/A'}</div>
                            {person.key_strengths && person.key_strengths.length > 0 && (
                              <div className="text-xs text-green-700 mb-1">Strengths: {person.key_strengths.join(', ')}</div>
                            )}
                            {person.development_areas && person.development_areas.length > 0 && (
                              <div className="text-xs text-orange-700">Development: {person.development_areas.join(', ')}</div>
                  )}
                </div>
                        ))
                      : (
                          <div className="flex flex-col items-center w-48 p-4 bg-gray-50 rounded-xl shadow border border-gray-100">
                            {companyData.linkedin_team.individual_performance.image_url && (
                              <img src={companyData.linkedin_team.individual_performance.image_url} alt={companyData.linkedin_team.individual_performance.individual_name} className="w-16 h-16 rounded-full object-cover mb-2" />
                            )}
                            <div className="font-semibold text-gray-900 text-base mb-1">{companyData.linkedin_team.individual_performance.individual_name}</div>
                            <div className="text-xs text-gray-600 mb-1">{companyData.linkedin_team.individual_performance.title}</div>
                            <div className="text-xs text-gray-500 mb-1">Tenure: {companyData.linkedin_team.individual_performance.tenure_years ? `${companyData.linkedin_team.individual_performance.tenure_years} yrs` : 'N/A'}</div>
                            {companyData.linkedin_team.individual_performance.key_strengths && companyData.linkedin_team.individual_performance.key_strengths.length > 0 && (
                              <div className="text-xs text-green-700 mb-1">Strengths: {companyData.linkedin_team.individual_performance.key_strengths.join(', ')}</div>
                            )}
                            {companyData.linkedin_team.individual_performance.development_areas && companyData.linkedin_team.individual_performance.development_areas.length > 0 && (
                              <div className="text-xs text-orange-700">Development: {companyData.linkedin_team.individual_performance.development_areas.join(', ')}</div>
                            )}
            </div>
          )}
                    </div>
                    </div>
                  )}
            </section>
          )}
          {activeSection === 'market' && companyData?.market_analysis && (
            <section className="space-y-10 mx-4 md:mx-6 lg:mx-8">
              {/* Market Trends Card */}
              {companyData.market_analysis.market_trends && (
                <div className="bg-white rounded-2xl shadow-lg p-8 flex flex-col md:flex-row gap-8 w-full">
                  {companyData.market_analysis.market_trends.iframe_url && (
                    <div className="md:w-1/2 w-full flex items-center justify-center">
                          <IframeWithFullscreen 
                        src={companyData.market_analysis.market_trends.iframe_url}
                        title={`Market Trends - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                      )}
                  <div className="flex-1">
                    <div className="mb-2 text-xl font-bold text-gray-900">Market Trends</div>
                    <div className="text-gray-700 mb-3 text-base font-medium">
                      {companyData.market_analysis.market_trends.summary || 'No market trends summary available.'}
                    </div>
                    {companyData.market_analysis.market_trends.market_size && companyData.market_analysis.market_trends.market_size.length > 0 && (
                      <div className="mb-3">
                        <span className="font-semibold text-xs text-gray-700 mr-2">Market Size:</span>
                        <span className="text-xs text-gray-600">{companyData.market_analysis.market_trends.market_size.map(ms => `${ms.industry}: ${ms.percentage}%`).join(', ')}</span>
                    </div>
                  )}
                    <div className="text-xs text-gray-500 mb-2">Last updated: {companyData.market_analysis.market_trends.last_updated ? new Date(companyData.market_analysis.market_trends.last_updated).toLocaleDateString() : 'N/A'}</div>
                    {/* Citations */}
                    {companyData.market_analysis.market_trends.citations && companyData.market_analysis.market_trends.citations.length > 0 && (
                      <div className="mt-2">
                        <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                        <ul className="list-disc list-inside space-y-1">
                          {companyData.market_analysis.market_trends.citations.map((citation, idx) => (
                            <li key={idx}>
                              <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                            </li>
                          ))}
                        </ul>
            </div>
                    )}
                    </div>
                    </div>
                  )}
              {/* Competitive Analysis Card */}
              {companyData.market_analysis.competitive_analysis && (
                <div className="bg-white rounded-2xl shadow-lg p-8 w-full mb-8">
                  <div className="mb-2 text-xl font-bold text-gray-900">Competitive Analysis</div>
                  <div className="text-gray-700 mb-3 text-base font-medium">
                    {companyData.market_analysis.competitive_analysis.summary || 'No competitive analysis summary available.'}
                        </div>
                  {companyData.market_analysis.competitive_analysis.top_competitors && companyData.market_analysis.competitive_analysis.top_competitors.length > 0 && (
                    <div className="mb-3 overflow-x-auto">
                      <table className="min-w-[600px] w-full text-xs border rounded-lg">
                        <thead>
                          <tr className="bg-purple-light/10 text-purple-dark">
                            <th className="px-3 py-2 text-left font-medium">Company</th>
                            <th className="px-3 py-2 text-left font-medium">Industry</th>
                            <th className="px-3 py-2 text-left font-medium">Market Share</th>
                            <th className="px-3 py-2 text-left font-medium">Revenue</th>
                            <th className="px-3 py-2 text-left font-medium">Growth Rate</th>
                            <th className="px-3 py-2 text-left font-medium">Strengths</th>
                            <th className="px-3 py-2 text-left font-medium">Weaknesses</th>
                          </tr>
                        </thead>
                        <tbody>
                          {companyData.market_analysis.competitive_analysis.top_competitors.map((comp, idx) => (
                            <tr key={idx} className="border-t">
                              <td className="px-3 py-2 font-semibold text-gray-900">{comp.company_name}</td>
                              <td className="px-3 py-2">{comp.industry}</td>
                              <td className="px-3 py-2">{comp.market_share}%</td>
                              <td className="px-3 py-2">
                                {typeof comp.revenue === 'number' && !isNaN(comp.revenue)
                                  ? `$${comp.revenue.toLocaleString()}`
                                  : 'N/A'}
                              </td>
                              <td className="px-3 py-2">
                                {typeof comp.growth_rate === 'number' && !isNaN(comp.growth_rate)
                                  ? `${comp.growth_rate}%`
                                  : 'N/A'}
                              </td>
                               <td className="px-3 py-2 text-success">
                                {Array.isArray(comp.strengths) && comp.strengths.length > 0
                                  ? comp.strengths.join(', ')
                                  : 'N/A'}
                              </td>
                               <td className="px-3 py-2 text-warning">
                                {Array.isArray(comp.weaknesses) && comp.weaknesses.length > 0
                                  ? comp.weaknesses.join(', ')
                                  : 'N/A'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                        </div>
                      )}
                  {/* Chart/Iframe if available */}
                  {companyData.market_analysis.competitive_analysis.iframe_url && (
                    <div className="w-full flex items-center justify-center mt-4">
                          <IframeWithFullscreen 
                        src={companyData.market_analysis.competitive_analysis.iframe_url}
                        title={`Competitive Analysis - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                      )}
                  {/* Citations */}
                  {companyData.market_analysis.competitive_analysis.citations && companyData.market_analysis.competitive_analysis.citations.length > 0 && (
                    <div className="mt-2">
                      <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {companyData.market_analysis.competitive_analysis.citations.map((citation, idx) => (
                          <li key={idx}>
                            <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
            </div>
          )}
              {/* Growth Projections Card */}
              {companyData.market_analysis.growth_projections && (
                <div className="bg-white rounded-2xl shadow-lg p-8 w-full">
                  <div className="mb-2 text-xl font-bold text-gray-900">Growth Projections</div>
                  <div className="text-gray-700 mb-3 text-base font-medium">
                    {companyData.market_analysis.growth_projections.summary || 'No growth projections summary available.'}
                    </div>
                  {/* Chart/Iframe if available */}
                  {companyData.market_analysis.growth_projections.iframe_url && (
                    <div className="w-full flex items-center justify-center mt-4">
                          <IframeWithFullscreen 
                        src={companyData.market_analysis.growth_projections.iframe_url}
                        title={`Growth Projections - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                      )}
                  {/* Projections Table if available */}
                  {companyData.market_analysis.growth_projections.projections_timeseries && companyData.market_analysis.growth_projections.projections_timeseries.length > 0 && (
                    <div className="mb-3 overflow-x-auto">
                      <table className="min-w-[500px] w-full text-xs border rounded-lg">
                        <thead>
                          <tr className="bg-gray-50 text-gray-700">
                            <th className="px-3 py-2 text-left">Period</th>
                            <th className="px-3 py-2 text-left">Metric</th>
                            <th className="px-3 py-2 text-left">Projected Value</th>
                          </tr>
                        </thead>
                        <tbody>
                          {companyData.market_analysis.growth_projections.projections_timeseries.map((proj, idx) => (
                            <tr key={idx} className="border-t">
                              <td className="px-3 py-2">{proj.period_start} - {proj.period_end}</td>
                              <td className="px-3 py-2">{proj.metric}</td>
                              <td className="px-3 py-2">{proj.projected_value}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {/* Citations */}
                  {companyData.market_analysis.growth_projections.citations && companyData.market_analysis.growth_projections.citations.length > 0 && (
                    <div className="mt-2">
                      <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {companyData.market_analysis.growth_projections.citations.map((citation, idx) => (
                          <li key={idx}>
                            <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                          </li>
                        ))}
                      </ul>
            </div>
          )}
                    </div>
                  )}
              {/* Regional Trends Card */}
              {companyData.market_analysis.regional_trends && (
                <div className="bg-white rounded-2xl shadow-lg p-8 w-full">
                  <div className="mb-2 text-xl font-bold text-gray-900">Regional Trends</div>
                  <div className="text-gray-700 mb-3 text-base font-medium">
                    {companyData.market_analysis.regional_trends.summary || 'No regional trends summary available.'}
                  </div>
                  {/* Chart/Iframe if available */}
                  {companyData.market_analysis.regional_trends.iframe_url && (
                    <div className="w-full flex items-center justify-center mt-4">
                          <IframeWithFullscreen 
                        src={companyData.market_analysis.regional_trends.iframe_url}
                        title={`Regional Trends - ${companyData.company_name ? toCamelCase(companyData.company_name) : ''}`}
                        height="350px"
                          />
                        </div>
                      )}
                  {/* Regional Trends Table if available */}
                  {companyData.market_analysis.regional_trends.regional_trends && companyData.market_analysis.regional_trends.regional_trends.length > 0 && (
                    <div className="mb-3 overflow-x-auto">
                      <table className="min-w-[500px] w-full text-xs border rounded-lg">
                        <thead>
                          <tr className="bg-purple-light/5 text-primary">
                            <th className="px-3 py-2 text-left font-medium">Industry</th>
                            <th className="px-3 py-2 text-left font-medium">Region</th>
                            <th className="px-3 py-2 text-left font-medium">Period</th>
                            <th className="px-3 py-2 text-left font-medium">Value</th>
                            <th className="px-3 py-2 text-left font-medium">Metric</th>
                          </tr>
                        </thead>
                        <tbody>
                          {companyData.market_analysis.regional_trends.regional_trends.map((trend, idx) => (
                            <tr key={idx} className="border-t hover:bg-purple-light/5 transition-colors">
                              <td className="px-3 py-2 text-secondary">{trend.industry}</td>
                              <td className="px-3 py-2 text-secondary">{trend.region}</td>
                              <td className="px-3 py-2 text-secondary">{trend.period_start} - {trend.period_end}</td>
                              <td className="px-3 py-2 text-secondary">{trend.value}</td>
                              <td className="px-3 py-2 text-secondary">{trend.metric}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                  {/* Citations */}
                  {companyData.market_analysis.regional_trends.citations && companyData.market_analysis.regional_trends.citations.length > 0 && (
                    <div className="mt-2">
                      <div className="font-semibold text-xs text-gray-700 mb-1">Citations:</div>
                      <ul className="list-disc list-inside space-y-1">
                        {companyData.market_analysis.regional_trends.citations.map((citation, idx) => (
                          <li key={idx}>
                            <a href={citation.url} target="_blank" rel="noopener noreferrer" className="text-purple hover:text-purple-dark hover:underline transition-colors text-xs">{citation.title || citation.url}</a>
                          </li>
                        ))}
                      </ul>
                </div>
                  )}
            </div>
          )}
            </section>
          )}
          {activeSection === 'risk' && companyData?.risk_analysis && (
            <section>
              {/* ...risk analysis section content, wide layout... */}
            </section>
          )}
          {activeSection === 'sentiment' && companyData?.customer_sentiment && (
            <section>
              {/* ...customer sentiment section content, wide layout... */}
            </section>
          )}
          {activeSection === 'partnership' && companyData?.partnership_network && (
            <section>
              {/* ...partnership network section content, wide layout... */}
            </section>
          )}
          {activeSection === 'compliance' && companyData?.regulatory_compliance && (
            <section>
              {/* ...regulatory compliance section content, wide layout... */}
            </section>
          )}
        </main>
      </div>
    </div>
  );
}