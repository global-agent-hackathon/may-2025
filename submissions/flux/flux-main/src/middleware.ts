import { clerkMiddleware, createRouteMatcher } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

// Protect all dashboard routes and API routes
const isProtectedRoute = createRouteMatcher([
  "/dashboard(.*)",
  "/api/workspace(.*)",
  "/api/forms/(.*)", // All form routes are protected by default
  "/api/user(.*)",
  "/api/favorites(.*)"
]);

// Public form routes that don't require authentication
const isPublicFormRoute = createRouteMatcher([
  "/forms/(.*)$", // Public form view
  "/api/forms/(.*)" // Form API routes can be public with proper params
]);

export default clerkMiddleware((auth, req) => {
  const url = new URL(req.url);
  const path = url.pathname;
  const isPublicParam = url.searchParams.get('public') === 'true';
  
  // Special case for form API with public=true parameter
  if (path.startsWith('/api/forms/') && isPublicParam) {
    return NextResponse.next();
  }
  
  // Special case for form responses
  if (path.includes('/api/forms/') && path.includes('/responses')) {
    return NextResponse.next();
  }

  // Check if the route is protected
  if (isProtectedRoute(req)) {
    auth.protect();
  }

  // Allow public form routes
  if (isPublicFormRoute(req)) {
    return NextResponse.next();
  }

  return NextResponse.next();
});

export const config = {
  matcher: [
    // Skip Next.js internals and all static files, unless found in search params
    '/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)',
    // Always run for API routes
    '/(api|trpc)(.*)',
  ],
};