"use client"

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useUser } from "@clerk/nextjs"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Switch } from "@/components/ui/switch"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Loader2 } from 'lucide-react'

export default function SettingsPage() {
  const router = useRouter()
  const { user, isLoaded } = useUser()
  const [saving, setSaving] = useState(false)
  const [activeTab, setActiveTab] = useState("account")

  // You'd implement actual settings saving logic in a real app
  const handleSave = async () => {
    setSaving(true)
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000))
    setSaving(false)
  }

  if (!isLoaded) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  return (
    <div className="container mx-auto py-8">
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground">Manage your account settings and preferences.</p>
        </div>

        <Tabs defaultValue={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="mb-8">
            <TabsTrigger value="account">Account</TabsTrigger>
            
            <TabsTrigger value="api">API Keys</TabsTrigger>
          </TabsList>

          {/* Account Settings */}
          <TabsContent value="account" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>
                  Update your profile information and email address.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="flex flex-col md:flex-row gap-8 items-start">
                  <div className="flex flex-col items-center gap-3">
                    <Avatar className="h-24 w-24">
                      <AvatarImage src={user?.imageUrl} alt={user?.fullName || "User"} />
                      <AvatarFallback className="text-2xl">
                        {user?.firstName?.[0]}{user?.lastName?.[0]}
                      </AvatarFallback>
                    </Avatar>
                    <Button variant="outline" size="sm" onClick={() => window.open("https://accounts.clerk.dev", "_blank")}>
                      Change Photo
                    </Button>
                  </div>
                  
                  <div className="space-y-4 flex-1">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <Label htmlFor="firstName">First Name</Label>
                        <Input 
                          id="firstName" 
                          defaultValue={user?.firstName || ""} 
                          readOnly
                        />
                      </div>
                      <div className="space-y-2">
                        <Label htmlFor="lastName">Last Name</Label>
                        <Input 
                          id="lastName" 
                          defaultValue={user?.lastName || ""} 
                          readOnly
                        />
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input 
                        id="email" 
                        defaultValue={user?.emailAddresses[0].emailAddress || ""} 
                        readOnly
                      />
                    </div>
                    
                    <p className="text-sm text-muted-foreground">
                      Your profile is managed by Clerk. <a href="https://accounts.clerk.dev" className="text-primary underline" target="_blank" rel="noreferrer">Click here</a> to edit your profile.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Notifications</CardTitle>
                <CardDescription>
                  Configure how you receive notifications.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Email Notifications</p>
                    <p className="text-sm text-muted-foreground">Receive emails about your form submissions</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                
                <Separator />
                
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Summary Reports</p>
                    <p className="text-sm text-muted-foreground">Receive weekly summary of your form activity</p>
                  </div>
                  <Switch />
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          

          {/* API Keys */}
          <TabsContent value="api" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>AI API Keys</CardTitle>
                <CardDescription>
                  Connect your AI service provider accounts to enhance your forms with AI capabilities.
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="openaiKey">OpenAI API Key</Label>
                    <div className="flex gap-2">
                      <Input 
                        id="openaiKey" 
                        type="password"
                        placeholder="sk-..."
                        className="font-mono"
                      />
                      <Button variant="outline" size="sm" className="shrink-0">Save</Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Get this from <a href="https://platform.openai.com/api-keys" className="text-primary underline" target="_blank" rel="noreferrer">OpenAI API Keys</a>.
                    </p>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    <Label htmlFor="claudeKey">Anthropic Claude API Key</Label>
                    <div className="flex gap-2">
                      <Input 
                        id="claudeKey" 
                        type="password"
                        placeholder="sk-ant-..."
                        className="font-mono"
                      />
                      <Button variant="outline" size="sm" className="shrink-0">Save</Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Get this from <a href="https://console.anthropic.com/keys" className="text-primary underline" target="_blank" rel="noreferrer">Anthropic Console</a>.
                    </p>
                  </div>
                  
                  <Separator />
                  
                  <div className="space-y-2">
                    <Label htmlFor="geminiKey">Google Gemini API Key</Label>
                    <div className="flex gap-2">
                      <Input 
                        id="geminiKey" 
                        type="password"
                        placeholder="AIza..."
                        className="font-mono"
                      />
                      <Button variant="outline" size="sm" className="shrink-0">Save</Button>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Get this from <a href="https://ai.google.dev/" className="text-primary underline" target="_blank" rel="noreferrer">Google AI Studio</a>.
                    </p>
                  </div>
                </div>
                
                <div className="mt-4 bg-muted p-3 rounded-md">
                  <p className="text-sm text-muted-foreground">
                    Your API keys are securely encrypted and stored. We never log or share your API keys.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
} 