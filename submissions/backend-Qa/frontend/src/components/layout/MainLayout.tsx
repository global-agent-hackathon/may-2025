
import React from 'react';
import { Outlet } from 'react-router-dom';
import { SidebarProvider, Sidebar, SidebarContent, SidebarInset } from '@/components/ui/sidebar';
import AppSidebar from './Sidebar';
import Navbar from './Navbar';

const MainLayout = () => {
  return (
    <SidebarProvider defaultOpen={true}>
      <div className="flex min-h-svh w-full">
        <Sidebar variant="inset" side="left">
          <SidebarContent>
            <AppSidebar />
          </SidebarContent>
        </Sidebar>
        
        <SidebarInset className="flex flex-col">
          <Navbar />
          <div className="flex-1 p-4 md:p-6 overflow-auto">
            <Outlet />
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
};

export default MainLayout;
