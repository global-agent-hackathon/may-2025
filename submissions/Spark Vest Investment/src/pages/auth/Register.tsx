import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Loader2, Upload } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { supabase } from '@/integrations/supabase/client';
const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [username, setUsername] = useState('');
  const [gender, setGender] = useState('');
  const [profilePicture, setProfilePicture] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const {
    signUp
  } = useAuth();
  const navigate = useNavigate();
  const {
    toast
  } = useToast();
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setProfilePicture(e.target.files[0]);
    }
  };
  const uploadProfilePicture = async (userId: string): Promise<string | null> => {
    if (!profilePicture) return null;
    const fileExt = profilePicture.name.split('.').pop();
    const filePath = `${userId}/profile.${fileExt}`;
    const {
      data,
      error
    } = await supabase.storage.from('profile_pictures').upload(filePath, profilePicture, {
      upsert: true
    });
    if (error) {
      throw error;
    }
    const {
      data: {
        publicUrl
      }
    } = supabase.storage.from('profile_pictures').getPublicUrl(filePath);
    return publicUrl;
  };
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (!username || !gender) {
        throw new Error('Please fill in all required fields');
      }
      const {
        data: {
          user
        },
        error: signUpError
      } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            username,
            gender
          }
        }
      });
      if (signUpError) throw signUpError;
      if (!user) throw new Error('Signup failed');

      // Upload profile picture if selected
      let profilePictureUrl = null;
      if (profilePicture) {
        profilePictureUrl = await uploadProfilePicture(user.id);
      }

      // Update profile with additional data
      const {
        error: updateError
      } = await supabase.from('profiles').update({
        username,
        gender,
        profile_picture_url: profilePictureUrl
      }).eq('id', user.id);
      if (updateError) throw updateError;
      toast({
        title: "Success",
        description: "Please check your email to verify your account"
      });
      navigate('/login');
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create account"
      });
    } finally {
      setLoading(false);
    }
  };
  return <div className="min-h-screen flex items-center justify-center px-4">
      <div className="glass-panel p-8 rounded-lg w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Create Account</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <Input type="text" placeholder="Username" value={username} onChange={e => setUsername(e.target.value)} required />
          </div>
          <div>
            <Input type="email" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
          <div>
            <Input type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <div>
            <Select value={gender} onValueChange={setGender}>
              <SelectTrigger>
                <SelectValue placeholder="Select Gender" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="male">Male</SelectItem>
                <SelectItem value="female">Female</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div>
            <label className="block mb-2 text-sm text-muted-foreground">
              Profile Picture
            </label>
            <Input type="file" accept="image/*" onChange={handleFileChange} className="file:mr-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-primary file:text-primary-foreground hover:file:bg-primary/90 my-[10px] mx-0 px-[19px] py-[8px]" />
          </div>
          <Button className="w-full" disabled={loading}>
            {loading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
            Sign Up
          </Button>
        </form>
        <p className="mt-4 text-center text-sm text-muted-foreground">
          Already have an account?{" "}
          <Link to="/login" className="text-primary hover:underline">
            Sign in
          </Link>
        </p>
      </div>
    </div>;
};
export default Register;