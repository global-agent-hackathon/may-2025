
import React from 'react';
import { FileText, Code, BarChart } from 'lucide-react';
import { NavLink } from 'react-router-dom';
import {
  SidebarContent,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarTrigger,
  useSidebar,
} from "@/components/ui/sidebar";

const AppSidebar = () => {
  const { state } = useSidebar();
  const collapsed = state === "collapsed";

  // Menu item definitions
  const menuItems = [
    {
      icon: FileText,
      title: "Manual Testing",
      path: "/manual-testing"
    },
    {
      icon: Code,
      title: "Automation Testing",
      path: "/automation-testing"
    },
    {
      icon: BarChart,
      title: "Result Dashboard",
      path: "/dashboard"
    }
  ];

  return (
    <>
      <SidebarHeader>
        <div className="flex items-center justify-between">
          {!collapsed && <h2 className="font-semibold text-xl">QA-T Agent</h2>}
          <SidebarTrigger />
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {menuItems.map((item) => (
                <SidebarMenuItem key={item.path}>
                  <SidebarMenuButton asChild tooltip={collapsed ? item.title : undefined}>
                    <NavLink 
                      to={item.path}
                      className="flex items-center gap-2"
                    >
                      <item.icon className="h-4 w-4" />
                      {!collapsed && <span>{item.title}</span>}
                    </NavLink>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </>
  );
};

export default AppSidebar;
