
import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { Link } from 'react-router-dom';
import { LogOut, User, CalendarDays, Mail, AtSign, Upload, Loader2 } from 'lucide-react';
import { supabase } from '@/integrations/supabase/client';
import DeleteAccountDialog from '@/components/profile/DeleteAccountDialog';
import { format } from 'date-fns';

interface ProfileData {
  username: string;
  gender: string;
  profile_picture_url: string | null;
  email: string;
  created_at?: string;
}

const Profile = () => {
  const { user, signOut } = useAuth();
  const { toast } = useToast();
  const [loading, setLoading] = useState(true);
  const [updating, setUpdating] = useState(false);
  const [profileData, setProfileData] = useState<ProfileData | null>(null);
  const [editedUsername, setEditedUsername] = useState('');
  const [editedGender, setEditedGender] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [uploadingImage, setUploadingImage] = useState(false);

  useEffect(() => {
    const fetchProfileData = async () => {
      if (!user) return;

      try {
        const { data, error } = await supabase
          .from('profiles')
          .select('username, gender, profile_picture_url, email, created_at')
          .eq('id', user.id)
          .single();

        if (error) throw error;
        setProfileData(data);
        setEditedUsername(data.username || '');
        setEditedGender(data.gender || '');
      } catch (error) {
        console.error('Error fetching profile:', error);
        toast({
          variant: "destructive",
          title: "Error",
          description: "Failed to load profile data",
        });
      } finally {
        setLoading(false);
      }
    };

    fetchProfileData();
  }, [user, toast]);

  const handleSignOut = async () => {
    try {
      await signOut();
    } catch (error) {
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to sign out",
      });
    }
  };

  const handleSaveProfile = async () => {
    if (!user) return;
    
    setUpdating(true);
    try {
      const { error } = await supabase
        .from('profiles')
        .update({
          username: editedUsername,
          gender: editedGender,
        })
        .eq('id', user.id);

      if (error) throw error;
      
      setProfileData(prev => prev ? {
        ...prev,
        username: editedUsername,
        gender: editedGender
      } : null);
      
      setIsEditing(false);
      
      toast({
        title: "Profile Updated",
        description: "Your profile has been successfully updated",
      });
    } catch (error) {
      console.error('Error updating profile:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to update profile",
      });
    } finally {
      setUpdating(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files || files.length === 0 || !user) return;
    
    const file = files[0];
    const fileExt = file.name.split('.').pop();
    const fileName = `${user.id}-${Math.random().toString(36).substring(2)}.${fileExt}`;
    
    setUploadingImage(true);
    try {
      // Upload file to Supabase Storage
      const { error: uploadError } = await supabase.storage
        .from('avatars')
        .upload(fileName, file);
        
      if (uploadError) throw uploadError;
      
      // Get public URL
      const { data } = supabase.storage
        .from('avatars')
        .getPublicUrl(fileName);
        
      // Update profile with new image URL
      const { error: updateError } = await supabase
        .from('profiles')
        .update({ profile_picture_url: data.publicUrl })
        .eq('id', user.id);
        
      if (updateError) throw updateError;
      
      // Update state
      setProfileData(prev => prev ? {
        ...prev,
        profile_picture_url: data.publicUrl
      } : null);
      
      toast({
        title: "Image Uploaded",
        description: "Your profile picture has been updated",
      });
    } catch (error) {
      console.error('Error uploading image:', error);
      toast({
        variant: "destructive",
        title: "Error",
        description: "Failed to upload profile picture",
      });
    } finally {
      setUploadingImage(false);
    }
  };

  // Get user initials for avatar fallback
  const getUserInitials = () => {
    if (!profileData?.username) return 'U';
    
    const nameParts = profileData.username.split(' ');
    if (nameParts.length === 1) return nameParts[0].charAt(0).toUpperCase();
    
    return (nameParts[0].charAt(0) + nameParts[nameParts.length - 1].charAt(0)).toUpperCase();
  };

  if (loading) {
    return (
      <div className="py-12 flex justify-center items-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="py-8 container max-w-4xl mx-auto px-4 sm:px-6">
      <div className="grid gap-8 md:grid-cols-3">
        {/* Profile Card */}
        <Card className="glass-panel h-fit md:col-span-1">
          <CardHeader className="text-center pb-2">
            <div className="relative mx-auto mb-4">
              <Avatar className="h-24 w-24 border-4 border-background">
                {profileData?.profile_picture_url ? (
                  <AvatarImage 
                    src={profileData.profile_picture_url} 
                    alt={profileData.username || 'Profile'} 
                  />
                ) : (
                  <AvatarFallback className="text-xl bg-primary/10">
                    {getUserInitials()}
                  </AvatarFallback>
                )}
              </Avatar>
              <div className="absolute -bottom-2 -right-2">
                <label 
                  htmlFor="avatar-upload" 
                  className={`rounded-full p-1.5 bg-primary text-primary-foreground hover:bg-primary/90 cursor-pointer flex items-center justify-center ${uploadingImage ? 'animate-pulse' : ''}`}
                >
                  {uploadingImage ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <Upload className="h-4 w-4" />
                  )}
                  <span className="sr-only">Upload avatar</span>
                </label>
                <input 
                  id="avatar-upload" 
                  type="file" 
                  className="hidden" 
                  accept="image/*" 
                  onChange={handleFileUpload}
                  disabled={uploadingImage}
                />
              </div>
            </div>
            <CardTitle className="text-xl">
              {profileData?.username || 'User'}
            </CardTitle>
            <CardDescription className="flex items-center justify-center gap-1 mt-1">
              <Mail className="h-3 w-3" />
              {profileData?.email || user?.email}
            </CardDescription>
          </CardHeader>
          <CardContent className="py-4 space-y-4">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CalendarDays className="h-4 w-4" />
              <span>
                Joined {profileData?.created_at 
                  ? format(new Date(profileData.created_at), 'MMMM d, yyyy')
                  : 'Recently'}
              </span>
            </div>
            {profileData?.gender && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <User className="h-4 w-4" />
                <span>{profileData.gender}</span>
              </div>
            )}
          </CardContent>
          <CardFooter className="flex flex-col gap-3 pt-2">
            <Button 
              variant="outline" 
              className="w-full" 
              onClick={handleSignOut}
            >
              <LogOut className="mr-2 h-4 w-4" /> Sign Out
            </Button>
            <DeleteAccountDialog />
          </CardFooter>
        </Card>

        {/* Account Details Card */}
        <Card className="glass-panel md:col-span-2">
          <CardHeader>
            <CardTitle>Account Details</CardTitle>
            <CardDescription>
              Manage your personal information
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" value={profileData?.email || ''} disabled />
              <p className="text-xs text-muted-foreground">
                Need to change your email? <Link to="/login" className="text-primary underline underline-offset-2">Contact support</Link>
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="username">Username</Label>
                {!isEditing && (
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => setIsEditing(true)}
                  >
                    Edit
                  </Button>
                )}
              </div>
              {isEditing ? (
                <Input 
                  id="username" 
                  value={editedUsername} 
                  onChange={(e) => setEditedUsername(e.target.value)} 
                />
              ) : (
                <Input id="username" value={profileData?.username || ''} disabled />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="gender">Gender</Label>
              {isEditing ? (
                <select 
                  id="gender" 
                  value={editedGender} 
                  onChange={(e) => setEditedGender(e.target.value)}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-base ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm"
                >
                  <option value="">Select gender</option>
                  <option value="Male">Male</option>
                  <option value="Female">Female</option>
                  <option value="Other">Other</option>
                  <option value="Prefer not to say">Prefer not to say</option>
                </select>
              ) : (
                <Input id="gender" value={profileData?.gender || ''} disabled />
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value="************" disabled />
              <p className="text-xs text-muted-foreground">
                <Link to="/forgot-password" className="text-primary underline underline-offset-2">
                  Reset your password
                </Link>
              </p>
            </div>
          </CardContent>
          {isEditing && (
            <CardFooter className="flex justify-between">
              <Button 
                variant="outline" 
                onClick={() => {
                  setIsEditing(false);
                  setEditedUsername(profileData?.username || '');
                  setEditedGender(profileData?.gender || '');
                }}
              >
                Cancel
              </Button>
              <Button 
                onClick={handleSaveProfile}
                disabled={updating}
              >
                {updating && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Save Changes
              </Button>
            </CardFooter>
          )}
        </Card>
      </div>
    </div>
  );
};

export default Profile;
