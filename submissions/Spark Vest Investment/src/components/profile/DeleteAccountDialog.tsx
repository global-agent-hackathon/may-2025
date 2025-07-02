import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '@/integrations/supabase/client';
import { useAuth } from '@/contexts/AuthContext';
import { useToast } from '@/components/ui/use-toast';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { 
  InputOTP, 
  InputOTPGroup, 
  InputOTPSlot 
} from '@/components/ui/input-otp';

enum DeleteSteps {
  CONFIRM,
  SEND_OTP,
  VERIFY_OTP
}

const DeleteAccountDialog = () => {
  const [step, setStep] = useState<DeleteSteps>(DeleteSteps.CONFIRM);
  const [loading, setLoading] = useState(false);
  const [otp, setOtp] = useState('');
  const [open, setOpen] = useState(false);
  const { user, signOut } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  const handleSendOTP = async () => {
    if (!user?.email) return;
    
    setLoading(true);
    try {
      
      toast({
        title: "OTP Sent",
        description: `A verification code has been sent to ${user.email}`,
      });
      
      setStep(DeleteSteps.VERIFY_OTP);
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || "Failed to send verification code",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setLoading(true);
    try {
      const { error } = await supabase.auth.admin.deleteUser(user?.id || '');
      
      if (error) throw error;
      
      toast({
        title: "Account Deleted",
        description: "Your account has been successfully deleted",
      });
      
      await signOut();
      setOpen(false);
      navigate('/');
    } catch (error: any) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error.message || "Failed to delete account",
      });
    } finally {
      setLoading(false);
    }
  };

  const resetDialog = () => {
    setStep(DeleteSteps.CONFIRM);
    setOtp('');
  };

  return (
    <Dialog open={open} onOpenChange={(newOpen) => {
      setOpen(newOpen);
      if (!newOpen) resetDialog();
    }}>
      <DialogTrigger asChild>
        <Button variant="destructive">Delete Account</Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-md">
        {step === DeleteSteps.CONFIRM && (
          <>
            <DialogHeader>
              <DialogTitle>Delete Account</DialogTitle>
              <DialogDescription>
                This action cannot be undone. This will permanently delete your account and remove your data from our servers.
              </DialogDescription>
            </DialogHeader>
            <DialogFooter className="mt-4 flex flex-col-reverse sm:flex-row gap-2">
              <Button 
                variant="outline" 
                onClick={() => setOpen(false)}
                className="sm:mt-0"
              >
                Cancel
              </Button>
              <Button 
                variant="destructive" 
                onClick={() => setStep(DeleteSteps.SEND_OTP)}
              >
                Continue
              </Button>
            </DialogFooter>
          </>
        )}

        {step === DeleteSteps.SEND_OTP && (
          <>
            <DialogHeader>
              <DialogTitle>Verify Email</DialogTitle>
              <DialogDescription>
                To continue, we need to verify it's you. We'll send a verification code to your email.
              </DialogDescription>
            </DialogHeader>
            <div className="py-4">
              <p className="text-sm text-muted-foreground">
                A verification code will be sent to: <span className="font-semibold text-foreground">{user?.email}</span>
              </p>
            </div>
            <DialogFooter className="gap-2 flex-col-reverse sm:flex-row">
              <Button 
                variant="outline" 
                onClick={() => setStep(DeleteSteps.CONFIRM)}
              >
                Back
              </Button>
              <Button 
                variant="destructive" 
                onClick={handleSendOTP}
                disabled={loading}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Send Code
              </Button>
            </DialogFooter>
          </>
        )}

        {step === DeleteSteps.VERIFY_OTP && (
          <>
            <DialogHeader>
              <DialogTitle>Enter Verification Code</DialogTitle>
              <DialogDescription>
                Enter the 6-digit code we sent to your email
              </DialogDescription>
            </DialogHeader>
            <div className="py-4 flex flex-col items-center space-y-4">
              <InputOTP 
                maxLength={6} 
                value={otp} 
                onChange={setOtp}
                className="gap-2"
              >
                <InputOTPGroup>
                  <InputOTPSlot index={0} />
                  <InputOTPSlot index={1} />
                  <InputOTPSlot index={2} />
                  <InputOTPSlot index={3} />
                  <InputOTPSlot index={4} />
                  <InputOTPSlot index={5} />
                </InputOTPGroup>
              </InputOTP>
              <Button 
                variant="link" 
                className="text-xs" 
                onClick={handleSendOTP}
                disabled={loading}
              >
                Didn't receive a code? Send again
              </Button>
            </div>
            <DialogFooter className="gap-2 flex-col-reverse sm:flex-row">
              <Button 
                variant="outline" 
                onClick={() => setStep(DeleteSteps.SEND_OTP)}
              >
                Back
              </Button>
              <Button 
                variant="destructive" 
                onClick={handleDeleteAccount}
                disabled={loading || otp.length !== 6}
              >
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Delete My Account
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default DeleteAccountDialog;
