import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import CompanyCarousel from '../components/homepage/CompanyCarousel';
import InvestorCard from '../components/homepage/InvestorCard';
import bgImage from '../assets/bg.png';
import { apiClient } from '../lib/api-client';
import type { Company, NewsArticle, CompanySearchResult } from '../lib/api-types';
import { API_ENDPOINTS } from '../lib/api-types';

export default function Home() {
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedQuery, setDebouncedQuery] = useState('');
  const [news, setNews] = useState<NewsArticle[]>([]);
  const [loadingNews, setLoadingNews] = useState(false);
  const [errorNews, setErrorNews] = useState<string | null>(null);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [searchedCompanies, setSearchedCompanies] = useState<Company[]>([]);
  const [loadingCompanies, setLoadingCompanies] = useState(false);
  const [errorCompanies, setErrorCompanies] = useState<string | null>(null);
  interface Investor {
    id?: string;
    email?: string;
    linkedin_url?: string;
    first_name?: string;
    last_name?: string;
    company_name?: string;
    title?: string;
    photo_url?: string;
    focus_areas?: string[];
    portfolio?: number;
    companies_invested?: number;
  }
  
  const [investors, setInvestors] = useState<Investor[]>([]);
  const [loadingInvestors, setLoadingInvestors] = useState(false);
  const [errorInvestors, setErrorInvestors] = useState<string | null>(null);
  const [showConnectionModal, setShowConnectionModal] = useState(false);
  const [connectionPayload, setConnectionPayload] = useState<{ founder_email: string; vc_email: string; vc_name: string } | null>(null);
  // Use string literals with a type declaration for better TypeScript support
  const CONNECTION_STATUS = {
    IDLE: 'idle',
    LOADING: 'loading', 
    SUCCESS: 'success',
    ERROR: 'error'
  } as const;
  
  // Create a string union type from the values
  type ConnectionStatus = typeof CONNECTION_STATUS[keyof typeof CONNECTION_STATUS];
  
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(CONNECTION_STATUS.IDLE);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [selectedNews, setSelectedNews] = useState<NewsArticle | null>(null);
  const [connectedVCs, setConnectedVCs] = useState<string[]>([]);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const navigate = useNavigate();
  const { user } = useAuth();
  const backgroundRef = useRef<HTMLDivElement>(null);
  const backgroundImageRef = useRef<HTMLDivElement>(null);
  const searchContainerRef = useRef<HTMLDivElement>(null);

  // Debounce search query
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQuery(searchQuery);
      if (searchQuery.trim()) {
        setShowDropdown(true);
      } else {
        setShowDropdown(false);
      }
    }, 400);
    return () => clearTimeout(handler);
  }, [searchQuery]);
  
  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  // Fetch companies for search results
  useEffect(() => {
    if (!debouncedQuery.trim()) {
      setSearchedCompanies([]);
      return;
    }
    
    setLoadingCompanies(true);
    setErrorCompanies(null);
    
    apiClient.get<CompanySearchResult[] | string[] | {companies: Company[]} | Company[]>(`${API_ENDPOINTS.COMPANIES_SEARCH}?query=${encodeURIComponent(debouncedQuery)}`)
      .then(data => {
        let companyList: Company[] = [];
        
        // Handle case where API returns CompanySearchResult objects
        if (Array.isArray(data) && data.length > 0 && typeof data[0] === 'object' && 'name' in data[0] && 'logoUrl' in data[0]) {
          companyList = (data as CompanySearchResult[]).map(result => ({
            id: result.name, // Use name as ID
            name: result.name,
            logoUrl: result.logoUrl,
            fundingStage: '' // Required by Company type
          }));
        }
        // Handle case where API returns just an array of strings (company names)
        else if (Array.isArray(data) && data.length > 0 && typeof data[0] === 'string') {
          companyList = (data as string[]).map(name => ({
            id: name, // Use name as ID
            name: name,
            fundingStage: '' // Required by Company type
          }));
        } 
        // Handle case where API returns array of Company objects
        else if (Array.isArray(data)) {
          companyList = data as Company[];
        } 
        // Handle case where API returns object with companies array
        else if (data && Array.isArray(data.companies)) {
          companyList = data.companies;
        }
        
        setSearchedCompanies(companyList);
      })
      .catch(err => setErrorCompanies(err.message || 'Error fetching companies for search'))
      .finally(() => setLoadingCompanies(false));
  }, [debouncedQuery]);

  // Fetch FEATURED companies
  useEffect(() => {
    setLoadingCompanies(true);
    setErrorCompanies(null);

    apiClient.get<{companies: Company[]} | Company[]>(API_ENDPOINTS.COMPANIES_FEATURED)
      .then(data => {
        const companyList: Company[] = Array.isArray(data) ? data : data.companies || [];
        setCompanies(companyList);
      })
      .catch(err => setErrorCompanies(err.message || 'Error fetching featured companies'))
      .finally(() => setLoadingCompanies(false));
  }, []);

  // Fetch Trending News
  useEffect(() => {
    setLoadingNews(true);
    setErrorNews(null);
    
    apiClient.get<{news: NewsArticle[], articles: NewsArticle[]} | NewsArticle[]>(`${API_ENDPOINTS.NEWS_TRENDING}?limit=15`)
      .then((data) => {
        let newsData: NewsArticle[] = [];
        if (Array.isArray(data)) {
          newsData = data;
        } else if (data && Array.isArray(data.news)) {
          newsData = data.news;
        } else if (data && Array.isArray(data.articles)) {
          newsData = data.articles;
        }
        setNews(newsData);
      })
      .catch((err) => {
        setErrorNews(err.message || 'Error fetching news');
      })
      .finally(() => setLoadingNews(false));
  }, []);

  // Fetch top investors if user is founder
  useEffect(() => {
    if (user?.user_type === 'founder') {
      setLoadingInvestors(true);
      setErrorInvestors(null);
      apiClient.get('/companies/top-investors') // Changed endpoint
        .then((responseData) => {
          // Assert the possible shapes of the response data
          const data = responseData as { investors?: Investor[] } | Investor[];

          if (data && 'investors' in data && Array.isArray(data.investors)) {
            // Case 1: data is { investors: [...] }
            setInvestors(data.investors);
          } else if (Array.isArray(data)) {
            // Case 2: data is [...]
            setInvestors(data);
          } else {
            setInvestors([]);
          }
        })
        .catch((err) => setErrorInvestors(err.message || 'Error fetching investors'))
        .finally(() => setLoadingInvestors(false));
    }
  }, [user?.user_type]);

  // Fetch connected VCs for founders
  useEffect(() => {
    if (user?.user_type === 'founder' && user?.email) {
      apiClient.get(`/auth/founder-connected-vcs?email=${encodeURIComponent(user.email)}`) // Changed endpoint
        .then((data) => {
          const resp = data as { connected_vcs?: string[] }; // Keep current type assertion for safety
          if (resp && Array.isArray(resp.connected_vcs)) {
            setConnectedVCs(resp.connected_vcs);
          } else {
            setConnectedVCs([]);
          }
        })
        .catch(() => setConnectedVCs([]));
    }
  }, [user?.user_type, user?.email]);

  // Handle input change for search query
  const handleSearchInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden bg-off-white">
      {/* Interactive Background */}
      {/* Mercury-style background with hover effect */}
      <div 
        ref={backgroundRef}
        className="fixed inset-0 z-0 w-full h-full overflow-hidden"
        style={{ contain: 'paint layout' }}
        onMouseMove={(e: React.MouseEvent) => {
          if (backgroundRef.current) {
            const rect = backgroundRef.current.getBoundingClientRect();
            // Calculate position as percentage of container width/height
            const x = (e.clientX - rect.left) / rect.width;
            const y = (e.clientY - rect.top) / rect.height;
            setMousePosition({
              x: e.clientX - rect.left,
              y: e.clientY - rect.top
            });
            
            // Apply an extremely subtle Mercury-style parallax effect to the background
            if (backgroundImageRef.current) {
              // Reduce movement even more on the right side of the screen
              const xMovement = x > 0.5 ? -x * 3 : -x * 5;
              // Use translate3d for hardware acceleration
              backgroundImageRef.current.style.transform = `translate3d(${xMovement}px, ${-y * 4}px, 0)`;
            }
          }
        }}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => {
          setIsHovering(false);
          // Reset position when mouse leaves
          if (backgroundImageRef.current) {
            backgroundImageRef.current.style.transform = 'translate3d(0, 0, 0)';
          }
        }}
      >
        {/* Background image with Mercury-style parallax effect */}
        <div 
          ref={backgroundImageRef}
          className="absolute inset-0 will-change-transform"
          style={{
            backgroundImage: `url(${bgImage})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center',
            transform: 'translate3d(0, 0, 0)',
            transition: 'transform 1.5s cubic-bezier(0.215, 0.61, 0.355, 1)',
            backfaceVisibility: 'hidden',
            WebkitBackfaceVisibility: 'hidden',
          }}
        />
        
        {/* Mercury-style glass overlay with subtle gradient */}
        <div 
          className="absolute inset-0 will-change-[mask-image]"
          style={{
            background: 'linear-gradient(135deg, rgba(246,243,237,0.85) 0%, rgba(246,243,237,0.8) 25%, rgba(246,243,237,0.7) 50%, rgba(246,243,237,0.6) 75%, rgba(246,243,237,0.5) 100%)',
            backdropFilter: 'blur(12px) saturate(110%)',
            WebkitBackdropFilter: 'blur(12px) saturate(110%)',
            boxShadow: 'inset 0 0 200px rgba(255,255,255,0.15)',
            WebkitMaskImage: isHovering ? `radial-gradient(circle 2in at ${mousePosition.x}px ${mousePosition.y}px, transparent 0%, black 100%)` : 'none',
            maskImage: isHovering ? `radial-gradient(circle 2in at ${mousePosition.x}px ${mousePosition.y}px, transparent 0%, black 100%)` : 'none',
            transform: 'translateZ(0)',
          }}
        />
        
        {/* Light reflection effect similar to Mercury */}
        <div 
          className="absolute inset-0 opacity-40"
          style={{
            background: 'radial-gradient(ellipse at 30% 20%, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0) 60%)',
            pointerEvents: 'none',
          }}
        />
        
        {/* Subtle grain texture for realism */}
        <div 
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 200 200\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noiseFilter\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.65\' numOctaves=\'3\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%\' height=\'100%\' filter=\'url(%23noiseFilter)\' opacity=\'0.5\' /%3E%3C/svg%3E")',
            backgroundRepeat: 'repeat',
            pointerEvents: 'none',
            mixBlendMode: 'overlay',
          }}
        />
      </div>
      {/* Main Content */}
      <main className="flex-grow relative z-10">
        {/* Hero Section */}
        <section className="text-center py-12 sm:py-16 md:py-20 lg:py-24 min-h-[90vh] flex items-center justify-center w-full">
          <div className="w-full max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl sm:text-4xl md:text-5xl lg:text-6xl font-bold text-primary mb-4 sm:mb-6 tracking-tight">
              Where Innovation Meets <span className="text-purple-dark">Investment</span>
            </h1>
            <p className="text-base sm:text-lg text-secondary max-w-3xl mx-auto mb-6 sm:mb-10 leading-relaxed">
              Discover Future Unicorns with AI-Powered Precision — Transforming Data into Opportunities
            </p>
            <div className="w-full max-w-3xl mx-auto relative">
              {/* Feature Pills - Similar to Crunchbase */}
              <div className="flex flex-wrap justify-center gap-2 sm:gap-3 mb-6 sm:mb-8">
                <button className="pill flex items-center bg-white/80 backdrop-blur-sm px-3 sm:px-4 py-1.5 sm:py-2 rounded-full shadow-sm hover:shadow-md transition-all duration-300 text-primary text-xs sm:text-sm font-medium">
                  <span className="text-purple-dark mr-2 text-lg">🔍</span>
                  <span>AI-Powered Search</span>
                </button>
                <button className="pill flex items-center bg-white/80 backdrop-blur-sm px-3 sm:px-4 py-1.5 sm:py-2 rounded-full shadow-sm hover:shadow-md transition-all duration-300 text-primary text-xs sm:text-sm font-medium">
                  <span className="text-purple-dark mr-2 text-lg">🧠</span>
                  <span>Deep Search Capabilities</span>
                </button>
                <button className="pill flex items-center bg-white/80 backdrop-blur-sm px-3 sm:px-4 py-1.5 sm:py-2 rounded-full shadow-sm hover:shadow-md transition-all duration-300 text-primary text-xs sm:text-sm font-medium">
                  <span className="text-purple-dark mr-2 text-lg">🌐</span>
                  <span>Community-Driven Intelligence</span>
                </button>
                <button className="pill flex items-center bg-white/80 backdrop-blur-sm px-3 sm:px-4 py-1.5 sm:py-2 rounded-full shadow-sm hover:shadow-md transition-all duration-300 text-primary text-xs sm:text-sm font-medium">
                  <span className="text-purple-dark mr-2 text-lg">⚡</span>
                  <span>Blazing Fast Performance</span>
                </button>
              </div>
              <div className="relative group max-w-3xl mx-auto" ref={searchContainerRef}>
                <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-light via-purple to-purple-dark rounded-xl blur opacity-30 group-hover:opacity-60 transition duration-1000 group-hover:duration-300 animate-pulse-slow"></div>
                <div className="relative">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={handleSearchInputChange}
                    placeholder="Search for a company..."
                    className="w-full px-4 sm:px-6 py-3 sm:py-4 pl-12 sm:pl-14 rounded-xl border-none focus:ring-2 focus:ring-purple outline-none shadow-md bg-white/90 backdrop-blur-sm transition-all duration-300 placeholder:text-gray-400"
                    autoComplete="off"
                  />
                  <div className="absolute left-3 sm:left-4 top-1/2 transform -translate-y-1/2 text-purple-dark">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                </div>
                {/* Search results dropdown */}
                {debouncedQuery.trim() && showDropdown && (
                  <div className="absolute top-full left-0 right-0 mt-2 bg-white/95 backdrop-blur-sm rounded-xl shadow-lg z-50 overflow-hidden border border-purple/10">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-purple-light/30 via-purple/30 to-purple-dark/30 rounded-xl blur-sm opacity-30"></div>
                    <div className="relative p-2">
                      {loadingCompanies && (
                        <div className="p-4 text-accent flex items-center justify-center">
                          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-purple" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          <span>Searching...</span>
                        </div>
                      )}
                      {errorCompanies && <p className="p-4 text-error font-medium">{errorCompanies}</p>}
                      {!loadingCompanies && searchedCompanies.length === 0 && debouncedQuery.trim() && (
                        <div className="p-4 text-secondary flex items-center">
                          <svg className="w-5 h-5 mr-2 text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.5" d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                          <span>No companies found for <span className="font-medium text-purple-dark">"{debouncedQuery}"</span></span>
                        </div>
                      )}
                      {searchedCompanies.length > 0 && (
                        <ul className="py-1 max-h-72 overflow-y-auto scrollbar-hide">
                          {searchedCompanies.map((company) => (
                            <li 
                              key={company.id}
                              onClick={() => {
                                navigate(`/companies/${encodeURIComponent(company.name.toLowerCase())}/analysis`);
                                setSearchQuery(''); // Clear search after selection
                              }}
                              className="px-5 py-3 hover:bg-purple-light/10 cursor-pointer text-primary transition-all duration-200 flex items-center group"
                            >
                              {company.logoUrl && (
                                <img 
                                  src={company.logoUrl} 
                                  alt={`${company.name} logo`} 
                                  className="w-6 h-6 mr-3 object-contain"
                                />
                              )}
                              {company.name}
                            </li>
                          ))}
                        </ul>
                      )}
                    </div>
                  </div>
                )}
              </div>
              
              {/* News Section */}
              <div className="mt-12 sm:mt-16 md:mt-20">
                <h2 className="text-3xl font-bold text-primary text-center mb-3">Trending News</h2>
                <p className="text-base sm:text-lg text-secondary text-center max-w-2xl mx-auto mb-6 sm:mb-8 leading-relaxed">
                  Stay informed with the latest developments in the venture capital ecosystem and emerging technology trends.
                </p>

                <div className="news-section">
                  {loadingNews && (
                    <div className="flex items-center justify-center py-4">
                      <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-purple"></div>
                    </div>
                  )}

                  {errorNews && (
                    <div className="text-center py-4 text-error">
                      {errorNews}
                    </div>
                  )}

                  {!loadingNews && !errorNews && news.length > 0 && (
                    <div 
                      className="w-full inline-flex flex-nowrap overflow-hidden mask-gradient" 
                      ref={(el) => {
                        // Apply a mask gradient to create fade effects at the edges
                        if (el) {
                          el.style.maskImage = 'linear-gradient(to right, transparent 0, black 100px, black calc(100% - 100px), transparent 100%)';
                          el.style.webkitMaskImage = 'linear-gradient(to right, transparent 0, black 100px, black calc(100% - 100px), transparent 100%)';
                        }
                      }}
                    >
                      {/* Primary list */}
                      <ul className="flex items-center md:justify-start [&_li]:mx-4 sm:[&_li]:mx-5 md:[&_li]:mx-6 animate-infinite-scroll">
                        {news.map((newsItem) => (
                          <li key={newsItem.id} className="cursor-pointer" onClick={() => setSelectedNews(newsItem)}>
                            <div className="bg-white/80 backdrop-blur-sm px-3 sm:px-4 md:px-5 py-1.5 sm:py-2 rounded-full shadow-sm hover:shadow-md transition-all duration-300 flex items-center">
                              <span className="h-2 w-2 rounded-full bg-purple-dark mr-3 flex-shrink-0"></span>
                              <span className="text-primary font-medium whitespace-nowrap">{newsItem.title}</span>
                            </div>
                          </li>
                        ))}
                      </ul>
                      
                      {/* Duplicate list for seamless scrolling (with aria-hidden for accessibility) */}
                      <ul className="flex items-center md:justify-start [&_li]:mx-4 sm:[&_li]:mx-5 md:[&_li]:mx-6 animate-infinite-scroll" aria-hidden="true">
                        {news.map((newsItem) => (
                          <li key={`${newsItem.id}-dup`} className="cursor-pointer" onClick={() => setSelectedNews(newsItem)}>
                            <div className="bg-white/80 backdrop-blur-sm px-3 sm:px-4 md:px-5 py-1.5 sm:py-2 rounded-full shadow-sm hover:shadow-md transition-all duration-300 flex items-center">
                              <span className="h-2 w-2 rounded-full bg-purple-dark mr-3 flex-shrink-0"></span>
                              <span className="text-primary font-medium whitespace-nowrap">{newsItem.title}</span>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Featured Investment Opportunities or Popular Investors Section */}
        {user?.user_type === 'vc' ? (
          <section className="py-8 sm:py-12 md:py-14 lg:py-16 w-full">
            <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 opacity-0 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
              <div className="flex flex-col items-center">
                <h2 className="text-3xl font-bold text-primary text-center mb-3">Featured Investment Opportunities</h2>
                <p className="text-secondary text-center max-w-2xl mx-auto mb-6 sm:mb-8 text-sm sm:text-base leading-relaxed">
                  Handpicked startups with exceptional growth potential, curated by our AI analysis and market intelligence.
                </p>
                {loadingCompanies && !errorCompanies && (
                  <div className="flex items-center justify-center py-4">
                    <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-purple" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <span className="text-accent font-medium">Loading featured companies...</span>
                  </div>
                )}
              </div>
              {errorCompanies && <p className="text-center text-error">{errorCompanies}</p>}
              {!loadingCompanies && companies.length === 0 && !errorCompanies && <p className="text-center text-secondary">No featured opportunities available at the moment.</p>}
              {companies.length > 0 && <CompanyCarousel companies={companies} />}
            </div>
          </section>
        ) : user?.user_type === 'founder' ? (
          <section className="py-8 sm:py-12 md:py-14 lg:py-16 w-full">
            <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 mb-6 sm:mb-8">
              <div className="flex flex-col items-center">
                <h2 className="text-3xl font-bold text-primary text-center mb-3">Popular Investors</h2>
                <p className="text-secondary text-center max-w-2xl mx-auto mb-6 sm:mb-8 text-sm sm:text-base leading-relaxed">
                  Connect with leading venture capitalists and angel investors actively seeking innovative startups in your industry.
                </p>
                <div className="flex space-x-3 sm:space-x-4 justify-center w-full">
                  <button
                    className="bg-white p-2 rounded-full shadow-md hover:shadow-lg transition-all transform hover:scale-105 focus:outline-none"
                    onClick={() => {
                      // Handle scrolling left for investors
                      const container = document.getElementById('investors-container');
                      if (container) container.scrollBy({ left: -340, behavior: 'smooth' });
                    }}
                    aria-label="Previous"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>
                  <button
                    className="bg-white p-2 rounded-full shadow-md hover:shadow-lg transition-all transform hover:scale-105 focus:outline-none"
                    onClick={() => {
                      // Handle scrolling right for investors
                      const container = document.getElementById('investors-container');
                      if (container) container.scrollBy({ left: 340, behavior: 'smooth' });
                    }}
                    aria-label="Next"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            <div className="relative overflow-hidden w-full bg-off-white/50 py-8 sm:py-10 md:py-12 rounded-[2rem] shadow-inner">
              {loadingInvestors && !errorInvestors && (
                <div className="flex items-center justify-center py-4">
                  <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-purple" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  <span className="text-accent font-medium">Loading investors...</span>
                </div>
              )}
              {errorInvestors && <p className="text-center text-error">{errorInvestors}</p>}
              {!loadingInvestors && investors.length === 0 && !errorInvestors && <p className="text-center text-secondary">No popular investors available at the moment.</p>}
              {investors.length > 0 && (
                <div 
                  id="investors-container"
                  className="flex gap-6 sm:gap-8 overflow-x-auto pb-4 pt-2 px-4 sm:px-6 scrollbar-hide snap-x w-[95%] max-w-[1400px] mx-auto"
                  style={{ scrollBehavior: 'smooth' }}
                >
                  {investors.map((investor, idx) => {
                    const isConnected = investor.email ? connectedVCs.includes(investor.email) : false;
                    return (
                      <div
                        key={investor.linkedin_url || idx}
                        className="min-w-[340px] w-[340px] flex-shrink-0 snap-start transform transition-all duration-300 shadow-lg hover:shadow-xl rounded-2xl overflow-hidden"
                        style={{
                          padding: '0.5rem',
                          background: 'linear-gradient(to bottom right, rgba(255,255,255,0.8), rgba(255,255,255,0.5))',
                          backdropFilter: 'blur(10px)'
                        }}
                      >
                        <InvestorCard 
                          investor={{
                            first_name: investor.first_name || '',
                            last_name: investor.last_name || '',
                            linkedin_url: investor.linkedin_url || '',
                            portfolio: investor.portfolio || 0,
                            companies_invested: investor.companies_invested || 0,
                            email: investor.email
                          }}
                          onReachOut={isConnected ? undefined : () => {
                            setConnectionPayload({
                              founder_email: user?.email || '',
                              vc_email: investor.email || '',
                              vc_name: `${investor.first_name || ''} ${investor.last_name || ''}`
                            });
                            setShowConnectionModal(true);
                          }}
                          isConnected={isConnected}
                        />
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </section>
        ) : null}

        <section className="text-center py-12 sm:py-16 md:py-20 lg:py-24 min-h-[90vh] flex items-center justify-center w-full">
          <div className="max-w-[1400px] mx-auto px-4 sm:px-6 lg:px-8 opacity-0 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <div className="flex flex-col items-center text-center">
              <h2 className="grid text-primary text-2xl sm:text-3xl font-semibold">
                <span>Zero friction.</span>
              </h2>
              <div className="mt-6 space-y-[1em] text-secondary text-base sm:text-lg max-w-3xl [&>span]:block">
                <span>
                  Connects seamlessly, smart decisions happen naturally.
                  Real-time market intelligence meets intuitive design—creating one smooth, unified experience.
                </span>
              </div>
              {/* Button to Venture Chat */}
              <div className="mt-10">
                <button
                  onClick={() => navigate('/intersectx-chat')}
                  className="px-8 py-3 bg-transparent hover:bg-purple text-purple hover:text-white font-semibold rounded-lg border-2 border-purple shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-purple focus:ring-opacity-75"
                >
                  Explore IntersectX Chat
                </button>
              </div>
            </div>
          </div>
        </section>


        {/* Modal for connection request */}
        {showConnectionModal && connectionPayload && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-primary bg-opacity-40 backdrop-blur-sm">
            <div className="bg-white rounded-xl shadow-lg p-8 max-w-md w-full border border-purple-light/20">
              <h3 className="text-xl font-bold mb-4 text-primary">Share Documents with Investor</h3>
              <p className="mb-4 text-secondary">
                By making this request, you agree to share all your uploaded documents with <span className="font-semibold text-indigo">{connectionPayload.vc_name}</span> for their research and analysis.<br />
                Do you agree to continue?
              </p>
              {connectionStatus === 'error' && (
                <div className="mb-3 text-error text-sm font-medium">{connectionError || 'Failed to make connection request.'}</div>
              )}
              {connectionStatus === 'success' && (
                <div className="mb-3 text-success text-sm font-medium">Request sent successfully!</div>
              )}
              <div className="flex justify-end gap-2">
                {(connectionStatus === CONNECTION_STATUS.IDLE) && (
                  <>
                    <button
                      className="px-4 py-2 rounded bg-gray-200 hover:bg-purple-light/20 text-primary font-medium transition-colors"
                      onClick={() => {
                        setShowConnectionModal(false);
                        setConnectionStatus(CONNECTION_STATUS.IDLE);
                        setConnectionError(null);
                      }}
                    >
                      No
                    </button>
                    <button
                      className="px-4 py-2 rounded bg-purple-dark hover:bg-purple text-white font-medium transition-colors"
                      onClick={async () => {
                        setConnectionStatus(CONNECTION_STATUS.LOADING);
                        setConnectionError(null);
                        try {
                          await apiClient.post('/auth/make-connection', {
                            founder_email: connectionPayload.founder_email,
                            vc_email: connectionPayload.vc_email,
                          });
                          setConnectionStatus(CONNECTION_STATUS.SUCCESS);
                          setTimeout(() => {
                            setShowConnectionModal(false);
                            setConnectionStatus(CONNECTION_STATUS.IDLE);
                          }, 1500);
                        } catch (err: any) {
                          setConnectionStatus(CONNECTION_STATUS.ERROR);
                          setConnectionError(err.message || 'Failed to make connection request.');
                        }
                      }}
                      disabled={false}
                    >
                      Yes, Continue
                    </button>
                  </>
                )}
                {(connectionStatus === CONNECTION_STATUS.SUCCESS || connectionStatus === CONNECTION_STATUS.ERROR) && (
                  <button
                    className="px-4 py-2 rounded bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium"
                    onClick={() => {
                      setShowConnectionModal(false);
                      setConnectionStatus(CONNECTION_STATUS.IDLE);
                      setConnectionError(null);
                    }}
                  >
                    Close
                  </button>
                )}
              </div>
            </div>
          </div>
        )}
      </main>

      {/* News Article Modal */}
      {selectedNews && (
        <div className="fixed inset-0 z-[100] overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={() => setSelectedNews(null)}></div>
            
            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            
            <div className="inline-block align-bottom bg-white rounded-xl text-left overflow-hidden shadow-xl transform transition-all my-4 sm:my-8 sm:align-middle w-full max-w-md sm:max-w-lg md:max-w-2xl lg:max-w-3xl">
              <div className="absolute top-0 right-0 pt-4 pr-4">
                <button
                  type="button"
                  className="bg-white rounded-full p-1 text-gray-400 hover:text-gray-500 focus:outline-none"
                  onClick={() => setSelectedNews(null)}
                >
                  <span className="sr-only">Close</span>
                  <svg className="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="bg-white px-4 sm:px-6 pt-4 sm:pt-5 pb-4 sm:pb-6">
                <h3 className="text-2xl font-bold text-primary mb-4 text-center">{selectedNews.title}</h3>
                
                <div className="flex flex-wrap justify-center mb-6 text-sm text-gray-500 gap-2">
                  <span className="bg-purple-light/20 text-purple-dark px-3 py-1 rounded-full">{selectedNews.category}</span>
                  <span>{new Date(selectedNews.published_at).toLocaleDateString()}</span>
                  {selectedNews.source && selectedNews.source.length > 0 && (
                    <span>{selectedNews.source[0]}</span>
                  )}
                </div>
                
                <div className="text-secondary leading-relaxed mb-6 break-words whitespace-pre-wrap">
                  {selectedNews.content}
                </div>
                
                {selectedNews.citations && selectedNews.citations.length > 0 && (
                  <div className="border-t border-gray-200 pt-4 mt-6">
                    <h4 className="text-sm font-medium text-primary mb-2">Sources:</h4>
                    <ul className="text-xs text-gray-600 space-y-1">
                      {selectedNews.citations.map((citation, index) => (
                        <li key={index}>{citation.title}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
