
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BookOpen, Users, Shield, TrendingUp, Linkedin, Twitter, Github } from 'lucide-react';
import { teamMembers } from "@/data/teamMembers";

const About = () => {
  return (
    <div className="py-12 max-w-6xl mx-auto px-4">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">About Spark Vest</h1>
        <p className="text-xl text-muted-foreground">
          Your intelligent investment companion powered by advanced AI technology
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-8 mb-12">
        <Card className="glass-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-400" />
              Our Mission
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              To democratize investing by providing cutting-edge AI tools and market insights to investors of all levels.
            </p>
          </CardContent>
        </Card>

        <Card className="glass-panel">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-green-400" />
              Our Values
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              We believe in transparency, security, and providing reliable investment insights backed by data.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card className="glass-panel mb-12">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-purple-400" />
            What We Offer
          </CardTitle>
        </CardHeader>
        <CardContent className="grid md:grid-cols-3 gap-6">
          <div>
            <h3 className="text-lg font-semibold mb-2">AI-Powered Insights</h3>
            <p className="text-muted-foreground">
              Get personalized investment recommendations and market analysis from our advanced AI system.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">Real-Time Data</h3>
            <p className="text-muted-foreground">
              Access up-to-the-minute market data and trends to make informed decisions.
            </p>
          </div>
          <div>
            <h3 className="text-lg font-semibold mb-2">Portfolio Management</h3>
            <p className="text-muted-foreground">
              Track and manage your investments with our intuitive portfolio tools.
            </p>
          </div>
        </CardContent>
      </Card>

      <div className="space-y-6">
        <h2 className="text-3xl font-bold text-center mb-8">Meet Our Team</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {teamMembers.map((member) => (
            <Card key={member.id} className="glass-panel hover:scale-105 transition-transform duration-300">
              <div className="p-4 space-y-4">
                <div className="w-48 h-48 mx-auto overflow-hidden rounded-lg">
                  <img 
                    src={member.image || "https://media-hosting.imagekit.io//4cd2278a98dc48b7/avatartion.png?Expires=1834756133&Key-Pair-Id=K2ZIVPTIP2VGHC&Signature=C22MhmrFRMR7CvIFLEiKPJXpMajmfNCx1qck~A5IntB83b5frqFUZ0PazWm8sfdmG2BMTSL9QNzode5Wf2H3K9BP5UeSjrf23g5TBC7OD3LkBqWcgIAsAlvEzOhqaeUdYBxCLZxPdpyccoLUTA8VRU78YTd-qHiLc9jVyLuwY2jw6m6pSFQFv6BPe0Kc3CXzy4D9IF3ik9-8aLpMp6epx~ny18zfpjy1moYl1e4OQV8JC4A4L0Cn4qCyAPqtvYpZvYOLehrpnFp9VdOhdSK70TMg8SoxjQm4cXjnmQPZw-069tztsZucIlSEWDlMcByL0zDmAmigCMnxrLM3vGKUog__"} 
                    alt={member.name} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="text-center">
                  <h3 className="text-xl font-semibold">{member.name}</h3>
                  <p className="text-muted-foreground mt-1">{member.role}</p>
                </div>
                {Object.keys(member.socialLinks).length > 0 && (
                  <div className="flex justify-center gap-4 pt-2">
                    {member.socialLinks.linkedin && (
                      <a 
                        href={member.socialLinks.linkedin}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <Linkedin className="h-5 w-5" />
                      </a>
                    )}
                    {member.socialLinks.twitter && (
                      <a 
                        href={member.socialLinks.twitter}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <Twitter className="h-5 w-5" />
                      </a>
                    )}
                    {member.socialLinks.github && (
                      <a 
                        href={member.socialLinks.github}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-muted-foreground hover:text-foreground transition-colors"
                      >
                        <Github className="h-5 w-5" />
                      </a>
                    )}
                  </div>
                )}
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};

export default About;
