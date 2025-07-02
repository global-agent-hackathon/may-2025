// React is used implicitly in JSX

interface ChartRendererProps {
  iframeUrls: string[];
}

export function ChartRenderer({ iframeUrls }: ChartRendererProps) {
  if (!iframeUrls || iframeUrls.length === 0) {
    return null;
  }

  return (
    <div className="chart-section">      
      
      {/* Bento-style grid - 2 columns on desktop, 1 column on mobile */}
      <div className="grid grid-cols-1 md:grid-cols-1 w-[100%] gap-6">
        {iframeUrls.map((url, index) => (
          <div 
            key={`chart-${index}`} 
            className="chart-bubble bg-white rounded-lg overflow-hidden shadow-sm border border-[#e7edf4] flex flex-col transition-all"
          >
            {/* Chart header */}
            <div className="px-3 py-2 border-b border-[#e7edf4] flex justify-between items-center bg-[#f9fafb]">
              <span className="text-sm font-medium text-[#0d141c]">Chart {index + 1}</span>
              <span className="bg-blue-50 px-2 py-1 rounded-full text-xs text-blue-600 font-medium">Interactive</span>
            </div>
            
            {/* Chart iframe */}
            <div className="p-2 flex-grow">
              <iframe 
                src={url} 
                title={`Chart ${index + 1}`}
                className="w-full rounded border border-[#f0f0f0]"
                height="300"
                style={{ border: 'none' }}
                loading="lazy"
                sandbox="allow-scripts allow-same-origin"
              />
            </div>
            
            {/* Footer with optional actions */}
            <div className="px-3 py-2 border-t border-[#e7edf4] flex justify-end">
              <button className="text-xs text-[#3d98f4] hover:underline">View full size</button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
