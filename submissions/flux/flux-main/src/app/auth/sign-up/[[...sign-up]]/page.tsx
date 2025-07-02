'use client';

import React from 'react';
import { SignIn } from "@clerk/nextjs";
import { BorderBeam } from "@/components/magicui/border-beam";

export default function SignUpPage() {
  return (
    <div className="flex items-center justify-center min-h-screen ">
      <div className="relative p-1 rounded-lg">
        {/* Animated, thicker, slower beam border around the sign-in form */}
        <BorderBeam
          size={320}
          initialOffset={10}
          delay={0.5}
          
          className="absolute inset-0 rounded-lg opacity-90"
          colorFrom="#3b82f6"
          colorTo="#8b5cf6"
          transition={{
            type: "tween",
            duration: 3,
            ease: "easeInOut",
          }}
        />
        <SignIn />
      </div>
    </div>
  );
}