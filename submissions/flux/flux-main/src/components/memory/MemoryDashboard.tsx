"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Search, Brain, Clock } from 'lucide-react';
import { useMemory } from '@/hooks/useMemory';

export default function MemoryDashboard() {
  const {
    searchMemories,
    loading,
    error
  } = useMemory();

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any>(null);
  const [allMemories, setAllMemories] = useState<any>(null);

  useEffect(() => {
    // Load initial data
    loadAllMemories();
  }, []);

  // Helper function to safely format dates
  const formatDate = (dateString: string | number | undefined) => {
    if (!dateString) return 'Date unavailable';
    
    try {
      const date = new Date(dateString);
      return isNaN(date.getTime()) ? 'Date unavailable' : date.toLocaleDateString();
    } catch (e) {
      return 'Date unavailable';
    }
  };

  const loadAllMemories = async () => {
    try {
      // Using a generic query that should return all memories
      const memories = await searchMemories('*', 50);
      setAllMemories(memories);
    } catch (err) {
      console.error('Failed to load all memories:', err);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const results = await searchMemories(searchQuery);
      setSearchResults(results);
    } catch (err) {
      console.error('Search failed:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center space-x-2">
        <Brain className="h-8 w-8 text-primary" />
        <h1 className="text-3xl font-bold">Memory Dashboard</h1>
      </div>
      
      <p className="text-muted-foreground">
        Explore your interaction history and past memories.
      </p>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Search className="h-5 w-5" />
            <span>Search Your Memories</span>
          </CardTitle>
          <CardDescription>
            Search through your stored memories and interactions
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Input
              placeholder="Search memories..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1"
            />
            <Button onClick={handleSearch} disabled={loading}>
              <Search className="h-4 w-4 mr-2" />
              Search
            </Button>
          </div>

          {searchResults && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">
                Search Results ({searchResults.memories?.length || 0})
              </h3>
              <div className="border rounded-md h-96 overflow-auto p-4">
                {searchResults.memories?.length === 0 ? (
                  <p className="text-muted-foreground text-center py-8">
                    No memories found for your search.
                  </p>
                ) : (
                  <div className="space-y-3">
                    {searchResults.memories?.map((memory: any, index: number) => (
                      <Card key={index} className="p-3">
                        <div className="space-y-2">
                          <div className="flex items-center justify-between mb-1">
                            <p className="text-sm">{memory.memory}</p>
                            {memory.metadata?.timestamp && (
                              <Badge variant="outline" className="text-xs">
                                {formatDate(memory.metadata.timestamp)}
                              </Badge>
                            )}
                          </div>
                          {memory.metadata && (
                            <div className="flex flex-wrap gap-1">
                              {Object.entries(memory.metadata)
                                .filter(([key]) => key !== 'timestamp')
                                .map(([key, value]) => (
                                  <Badge key={key} variant="outline" className="text-xs">
                                    {key}: {String(value)}
                                  </Badge>
                                ))}
                            </div>
                          )}
                        </div>
                      </Card>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* All Memories List */}
          <div className="space-y-4 mt-6">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold">
                All Memories ({allMemories?.memories?.length || 0})
              </h3>
              <Button variant="outline" size="sm" onClick={loadAllMemories} disabled={loading}>
                <Clock className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
            <div className="border rounded-md h-96 overflow-auto p-4">
              {loading ? (
                <p className="text-muted-foreground text-center py-8">
                  Loading memories...
                </p>
              ) : allMemories?.memories?.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  No memories found.
                </p>
              ) : (
                <div className="space-y-3">
                  {allMemories?.memories?.map((memory: any, index: number) => (
                    <Card key={index} className="p-3">
                      <div className="space-y-2">
                        <div className="flex items-center justify-between mb-1">
                          <p className="text-sm">{memory.memory}</p>
                          {memory.metadata?.timestamp && (
                            <Badge variant="outline" className="text-xs">
                              {formatDate(memory.metadata.timestamp)}
                            </Badge>
                          )}
                        </div>
                        {memory.metadata && (
                          <div className="flex flex-wrap gap-1">
                            {Object.entries(memory.metadata)
                              .filter(([key]) => key !== 'timestamp')
                              .map(([key, value]) => (
                                <Badge key={key} variant="outline" className="text-xs">
                                  {key}: {String(value)}
                                </Badge>
                              ))}
                          </div>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Card className="border-destructive">
          <CardContent className="pt-6">
            <p className="text-destructive text-sm">
              Error: {error}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
} 