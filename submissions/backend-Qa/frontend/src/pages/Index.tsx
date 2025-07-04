
import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardFooter, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import { FileText, Code, BarChart } from 'lucide-react';

const Index = () => {
  const navigate = useNavigate();

  const features = [
    {
      title: "Manual Testing",
      description: "Generate test plans and manual test cases from requirements",
      icon: FileText,
      path: "/manual-testing",
      color: "bg-blue-100 dark:bg-blue-900",
    },
    {
      title: "Automation Testing",
      description: "Create Gherkin scenarios, Selenium scripts, and API tests",
      icon: Code,
      path: "/automation-testing",
      color: "bg-purple-100 dark:bg-purple-900",
    },
    {
      title: "Result Dashboard",
      description: "View test results, statistics and generate reports",
      icon: BarChart,
      path: "/dashboard",
      color: "bg-green-100 dark:bg-green-900",
    },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold tracking-tight sm:text-5xl mb-2">
          Welcome to QA-T Agent
        </h1>
        <p className="text-xl text-muted-foreground">
          Quality Automation Testing Agent
        </p>
      </div>

      <div className="grid gap-8 md:grid-cols-3">
        {features.map((feature) => (
          <Card key={feature.title} className="border shadow-sm transition-all hover:shadow-md">
            <CardHeader>
              <div className={`w-12 h-12 rounded-full ${feature.color} flex items-center justify-center mb-4`}>
                <feature.icon className="h-6 w-6" />
              </div>
              <CardTitle>{feature.title}</CardTitle>
              <CardDescription>{feature.description}</CardDescription>
            </CardHeader>
            <CardFooter>
              <Button onClick={() => navigate(feature.path)} className="w-full">
                Get Started
              </Button>
            </CardFooter>
          </Card>
        ))}
      </div>

      <div className="mt-16 p-8 bg-muted rounded-xl text-center">
        <h2 className="text-2xl font-bold mb-4">How QA-T Agent Works</h2>
        <p className="text-muted-foreground mb-6">
          QA-T Agent uses advanced artificial intelligence to help QA teams generate test artifacts, 
          automate test scripts, and track results - all in one place.
        </p>
        
        <div className="grid gap-6 md:grid-cols-3 max-w-4xl mx-auto">
          <div className="flex flex-col items-center">
            <div className="rounded-full bg-primary/10 p-3 mb-3">
              <FileText className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-medium">Upload Requirements</h3>
            <p className="text-sm text-muted-foreground">
              Upload your requirements or specifications
            </p>
          </div>
          <div className="flex flex-col items-center">
            <div className="rounded-full bg-primary/10 p-3 mb-3">
              <Code className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-medium">Generate Tests</h3>
            <p className="text-sm text-muted-foreground">
              Generate test cases, scripts or scenarios
            </p>
          </div>
          <div className="flex flex-col items-center">
            <div className="rounded-full bg-primary/10 p-3 mb-3">
              <BarChart className="h-6 w-6 text-primary" />
            </div>
            <h3 className="font-medium">Analyze Results</h3>
            <p className="text-sm text-muted-foreground">
              Track test execution and analyze metrics
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Index;
