import FireCrawlApp from '@mendable/firecrawl-js';

export class FirecrawlService {
  private static app = new FireCrawlApp({
    apiKey: "fc-54a37b47967e4588aecf3601f020a6c1" // TODO: Consider moving to environment variables
  });

  static async scrapePortfolio(url: string): Promise<{ success: boolean; content?: string; error?: string }> {
    try {
      console.log('Starting Firecrawl crawl for:', url);
      
      // Use the dynamic 'url' parameter
      const crawlApiResponse = await this.app.crawlUrl(url, {
        limit: 10, // Max 10 pages, adjust as needed
        scrapeOptions: {
          formats: [ "markdown" ],
          onlyMainContent: true // Attempts to get only the main content of the pages
        }
        // 'returnPageData' defaults to true, which populates the 'data' field.
      });
      
      if (crawlApiResponse.success) {
        if (crawlApiResponse.data && Array.isArray(crawlApiResponse.data) && crawlApiResponse.data.length > 0) {
          console.log('Firecrawl crawl successful, data received for', crawlApiResponse.data.length, 'pages');
          
          // Concatenate markdown content from all crawled pages
          const allMarkdownContent = crawlApiResponse.data
            .map(pageData => pageData.markdown) // Extract markdown from each page object
            .filter(md => typeof md === 'string' && md.trim() !== '') // Ensure markdown is a non-empty string
            .join("\n\n---\n\n"); // Join content from different pages with a separator

          if (!allMarkdownContent || allMarkdownContent.trim() === "") {
            console.warn('No non-empty markdown content extracted from crawled pages.');
            return {
              success: false,
              error: 'No meaningful textual content could be extracted from the portfolio. The site might be heavily reliant on JavaScript rendering or primarily image-based.'
            };
          }
          
          console.log('Total markdown content length:', allMarkdownContent.length);
          return {
            success: true,
            content: allMarkdownContent
          };
        } else {
          // This case means crawl was successful but returned no data objects or an empty data array
          console.warn('Firecrawl crawl successful but no data or empty data array received.');
          return {
            success: false,
            error: 'Portfolio crawled, but no pages with extractable content were found.'
          };
        }
      } else {
        // crawlApiResponse.success is false
        const errorMessage = crawlApiResponse.error || (typeof crawlApiResponse.data === 'string' ? crawlApiResponse.data : 'Failed to crawl the portfolio URL.');
        console.error('Firecrawl crawl failed:', errorMessage);
        return {
          success: false,
          error: errorMessage
        };
      }
    } catch (error) {
      console.error('Exception in FirecrawlService.scrapePortfolio:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'An unexpected error occurred during the crawling process.'
      };
    }
  }
}