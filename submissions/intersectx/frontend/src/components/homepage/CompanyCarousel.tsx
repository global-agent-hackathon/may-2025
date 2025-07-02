import { useRef, useState } from 'react';
import CompanyCard from './CompanyCard';
import type { Company } from '../../lib/api-types';

interface CompanyCarouselProps {
  companies: Company[];
}

export default function CompanyCarousel({ companies }: CompanyCarouselProps) {
  const [currentPage, setCurrentPage] = useState(0);
  const [isScrolling, setIsScrolling] = useState(false);
  const carouselRef = useRef<HTMLDivElement>(null);

  // Always show 3 items per page
  const itemsPerPage = 3;
  const totalPages = Math.ceil(companies.length / itemsPerPage);

  const scroll = (direction: 'left' | 'right') => {
    if (isScrolling) return;
    
    setIsScrolling(true);
    let newPage;

    if (direction === 'left') {
      newPage = currentPage === 0 ? totalPages - 1 : currentPage - 1;
    } else {
      newPage = currentPage === totalPages - 1 ? 0 : currentPage + 1;
    }

    setCurrentPage(newPage);
    setTimeout(() => setIsScrolling(false), 500);
  };

  // Get visible companies for current page
  const visibleCompanies = () => {
    const start = currentPage * itemsPerPage;
    const end = start + itemsPerPage;
    return companies.slice(start, end);
  };

  return (
    <div className="relative w-full">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-8">
        <div className="flex flex-col items-center">
          {/* Navigation buttons moved below */}
        </div>
      </div>

      <div className="relative overflow-hidden w-full bg-off-white/50 py-12 rounded-[2rem] shadow-inner">
        {/* Carousel Container */}
        <div
          ref={carouselRef}
          className="w-full overflow-hidden px-6"
        >
          <div className="grid grid-cols-3 gap-6 max-w-[1400px] mx-auto transition-opacity duration-300"
               style={{ opacity: isScrolling ? 0.7 : 1 }}>
            {visibleCompanies().map((company) => (
              <div
                key={company.id}
                className="transform transition-all duration-300 shadow-lg hover:shadow-xl rounded-2xl overflow-hidden"
                style={{
                  padding: '0.5rem',
                  background: 'linear-gradient(to bottom right, rgba(255,255,255,0.8), rgba(255,255,255,0.5))',
                  backdropFilter: 'blur(10px)',
                }}
              >
                <CompanyCard company={company} />
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Navigation Controls */}
      <div className="flex flex-col items-center mt-8 mb-4">
        {/* Progress Dots */}
        <div className="flex justify-center space-x-4 mb-4">
          {Array.from({ length: totalPages }).map((_, index) => (
            <button
              key={index}
              className={`w-2.5 h-2.5 rounded-full transition-all transform hover:scale-110 ${index === currentPage ? 'bg-purple shadow-md scale-125' : 'bg-gray-300/70'}`}
              onClick={() => {
                if (isScrolling) return;
                setCurrentPage(index);
              }}
              aria-label={`Go to slide ${index + 1}`}
            />
          ))}
        </div>
        
        {/* Navigation Buttons */}
        <div className="flex space-x-4 justify-center">
          <button
            className="bg-white p-2 rounded-full shadow-md hover:shadow-lg transition-all transform hover:scale-105 focus:outline-none"
            onClick={() => scroll('left')}
            disabled={isScrolling}
            aria-label="Previous"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <button
            className="bg-white p-2 rounded-full shadow-md hover:shadow-lg transition-all transform hover:scale-105 focus:outline-none"
            onClick={() => scroll('right')}
            disabled={isScrolling}
            aria-label="Next"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-purple" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}
