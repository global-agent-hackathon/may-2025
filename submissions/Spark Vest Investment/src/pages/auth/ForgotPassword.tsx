
import { useState } from 'react';
import { Link } from 'react-router-dom';
import { supabase } from '@/integrations/supabase/client';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, ArrowLeft } from 'lucide-react';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { toast } = useToast();

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email, {
        redirectTo: `${window.location.origin}/reset-password`,
      });
      
      if (error) throw error;
      
      setSubmitted(true);
      toast({
        title: "Reset link sent",
        description: "Check your email for the password reset link",
      });
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || "Failed to send reset link",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md glass-panel">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">Reset Password</CardTitle>
          <CardDescription>
            {!submitted 
              ? "Enter your email to receive a password reset link" 
              : "Check your email for the reset link"}
          </CardDescription>
        </CardHeader>
        
        {!submitted ? (
          <form onSubmit={handleResetPassword}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Input
                  type="email"
                  placeholder="Email address"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="w-full"
                />
              </div>
            </CardContent>
            <CardFooter className="flex flex-col gap-4">
              <Button 
                type="submit" 
                className="w-full" 
                disabled={loading || !email}
              >
                {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                Send Reset Link
              </Button>
              <Link to="/login" className="flex items-center text-sm text-muted-foreground hover:text-primary">
                <ArrowLeft className="mr-2 h-4 w-4" /> Back to login
              </Link>
            </CardFooter>
          </form>
        ) : (
          <CardContent className="space-y-4">
            <div className="rounded-lg bg-primary/10 p-4 text-center">
              <p className="text-sm text-muted-foreground">
                A password reset link has been sent to <span className="font-semibold text-foreground">{email}</span>
              </p>
            </div>
            <Button asChild className="w-full mt-4">
              <Link to="/login">Return to Login</Link>
            </Button>
          </CardContent>
        )}
      </Card>
    </div>
  );
};

export default ForgotPassword;
