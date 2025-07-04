
import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Upload, Download, Clock, BarChart3, PieChart } from "lucide-react";
import StatusPieChart from "@/components/charts/StatusPieChart";
import FeatureBarChart from "@/components/charts/FeatureBarChart";
import TestDurationBarChart from "@/components/charts/TestDurationBarChart";
import { useTheme } from "@/hooks/useTheme";

const DashboardPage = () => {
  const { theme } = useTheme();
  
  // Mock data for demonstration
  const [statusData] = useState([
    { name: "Passed", value: 67, color: "#4ade80" },
    { name: "Failed", value: 18, color: "#f87171" },
    { name: "Skipped", value: 15, color: "#facc15" },
  ]);

  const [featureData] = useState([
    { name: "Login", passed: 12, failed: 4, skipped: 2 },
    { name: "Search", passed: 18, failed: 5, skipped: 2 },
    { name: "Cart", passed: 14, failed: 6, skipped: 3 },
    { name: "Checkout", passed: 21, failed: 2, skipped: 1 },
    { name: "Product", passed: 18, failed: 1, skipped: 4 },
    { name: "Profile", passed: 14, failed: 0, skipped: 5 },
  ]);

  const [browserData] = useState([
    { name: "Chrome", value: 45, color: "#3b82f6" },
    { name: "Firefox", value: 28, color: "#f97316" },
    { name: "Safari", value: 15, color: "#a3a3a3" },
    { name: "Edge", value: 12, color: "#38bdf8" },
  ]);
  
  const [durationData] = useState([
    { name: "Login Tests", min: 0.5, avg: 1.2, max: 2.4 },
    { name: "Search Tests", min: 0.8, avg: 1.8, max: 4.1 },
    { name: "Cart Tests", min: 0.6, avg: 1.5, max: 2.8 },
    { name: "Checkout Tests", min: 1.2, avg: 2.4, max: 5.3 },
  ]);

  const totalTests = statusData.reduce((sum, item) => sum + item.value, 0);
  const passedTests = statusData.find(item => item.name === "Passed")?.value || 0;
  const failedTests = statusData.find(item => item.name === "Failed")?.value || 0;
  const skippedTests = statusData.find(item => item.name === "Skipped")?.value || 0;
  
  const handleUpload = () => {
    const input = document.createElement("input");
    input.type = "file";
    input.accept = ".json,.xml";
    input.onchange = (e) => {
      const target = e.target as HTMLInputElement;
      const file = target.files?.[0];
      if (file) {
        console.log("File selected:", file);
      }
    };
    input.click();
  };

  const handleDownload = () => {
    console.log("Download report clicked");
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      <div className="flex flex-wrap justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">Test Execution Results</h1>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3 lg:grid-cols-4">
        {/* Test Summary Card */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Test Summary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="flex flex-wrap justify-center gap-4">
                <div className="flex flex-col items-center">
                  <p className="text-3xl font-bold">{totalTests}</p>
                  <p className="text-xs text-muted-foreground">Total</p>
                </div>
                <div className="flex flex-col items-center">
                  <p className="text-3xl font-bold text-green-500">{passedTests}</p>
                  <p className="text-xs text-muted-foreground">Passed</p>
                </div>
                <div className="flex flex-col items-center">
                  <p className="text-3xl font-bold text-red-500">{failedTests}</p>
                  <p className="text-xs text-muted-foreground">Failed</p>
                </div>
                <div className="flex flex-col items-center">
                  <p className="text-3xl font-bold text-yellow-500">{skippedTests}</p>
                  <p className="text-xs text-muted-foreground">Skipped</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Duration Card */}
        <Card className="col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Duration</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold">02:45</p>
                <p className="text-xs text-muted-foreground">Total Run Time</p>
              </div>
              <div>
                <p className="text-3xl font-bold">00:38</p>
                <p className="text-xs text-muted-foreground">Avg Test Run</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Coverage Card */}
        <Card className="col-span-1 md:col-span-1">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Coverage</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4 text-center">
              <div>
                <p className="text-3xl font-bold">4/5</p>
                <p className="text-xs text-muted-foreground">Scenarios</p>
              </div>
              <div>
                <p className="text-3xl font-bold">12/15</p>
                <p className="text-xs text-muted-foreground">Endpoints</p>
              </div>
            </div>
          </CardContent>
        </Card>
        
        <Card className="hidden lg:block" />
      </div>

      {/* Charts Grid */}
      <div className="grid gap-6 md:grid-cols-2">
        {/* Test Status Distribution */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <PieChart className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Test Status Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <StatusPieChart data={statusData} />
          </CardContent>
        </Card>
        
        {/* Feature Breakdown */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Feature Breakdown</CardTitle>
          </CardHeader>
          <CardContent>
            <FeatureBarChart data={featureData} />
          </CardContent>
        </Card>
      </div>
      
      <div className="grid gap-6 md:grid-cols-2">
        {/* Browser Distribution */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <PieChart className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Browser Distribution</CardTitle>
          </CardHeader>
          <CardContent>
            <StatusPieChart data={browserData} />
          </CardContent>
        </Card>
        
        {/* Test Duration */}
        <Card>
          <CardHeader className="flex flex-row items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground" />
            <CardTitle>Test Duration (seconds)</CardTitle>
          </CardHeader>
          <CardContent>
            <TestDurationBarChart data={durationData} />
          </CardContent>
        </Card>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-wrap justify-center gap-4 pt-4">
        <Button onClick={handleUpload} className="bg-blue-600 hover:bg-blue-700">
          <Upload className="h-4 w-4 mr-2" />
          Upload Results File
        </Button>
        <Button variant="outline" onClick={handleDownload}>
          <Download className="h-4 w-4 mr-2" />
          Download Report
        </Button>
      </div>
    </div>
  );
};

export default DashboardPage;
