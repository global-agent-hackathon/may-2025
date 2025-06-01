'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUser, useClerk } from '@clerk/nextjs';
import { ChevronDown, LogOut, User, Settings, ChevronRight } from 'lucide-react';

import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';

export function UserProfile() {
  const { user, isLoaded } = useUser();
  const { signOut } = useClerk();
  const router = useRouter();

  // Show loading state while Clerk is initializing
  if (!isLoaded) {
    return (
      <div className="flex items-center gap-2">
        <div className="h-7 w-7 rounded-full bg-gray-100 animate-pulse" />
        <div className="h-4 w-24 bg-gray-100 rounded animate-pulse" />
      </div>
    );
  }

  // Maintain the same height even when no user
  if (!user) {
    return <div className="h-10" />;
  }

  const userInitials = user.firstName && user.lastName
    ? `${user.firstName[0]}${user.lastName[0]}`
    : user.firstName?.[0] || 'U';

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="p-0 h-auto w-full justify-start gap-2 hover:bg-gray-50 rounded-md">
          <Avatar className="h-7 w-7">
            <AvatarImage src={user.imageUrl} alt={user.fullName || 'User'} />
            <AvatarFallback className="text-xs bg-gray-200 text-gray-700">{userInitials}</AvatarFallback>
          </Avatar>
          <span className="text-sm font-medium text-gray-900 truncate flex-1 text-left">{user.fullName || user.username || 'User'}</span>
          <ChevronDown className="h-3.5 w-3.5 text-gray-400" />
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-56" align="start">
        <div className="flex items-center justify-start gap-2 p-2">
          <div className="flex flex-col space-y-1 leading-none">
            <p className="font-medium">{user.fullName || user.username}</p>
            {user.emailAddresses && user.emailAddresses.length > 0 && (
              <p className="text-xs text-muted-foreground">{user.emailAddresses[0].emailAddress}</p>
            )}
          </div>
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuItem 
          className="flex cursor-pointer items-center gap-2 py-1.5"
          onClick={() => router.push('/dashboard/settings/profile')}
        >
          <User className="h-4 w-4" />
          <span>Profile</span>
        </DropdownMenuItem>
        <DropdownMenuItem 
          className="flex cursor-pointer items-center gap-2 py-1.5"
          onClick={() => router.push('/dashboard/settings')}
        >
          <Settings className="h-4 w-4" />
          <span>Settings</span>
        </DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem 
          className="flex cursor-pointer items-center gap-2 py-1.5 text-destructive focus:text-destructive"
          onClick={() => signOut(() => router.push('/'))}
        >
          <LogOut className="h-4 w-4" />
          <span>Log out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
} 