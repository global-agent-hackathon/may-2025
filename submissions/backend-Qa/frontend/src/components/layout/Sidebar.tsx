
import React from 'react';
import { Home, FileText, Code, BarChart } from 'lucide-react';
import { cn } from '@/lib/utils';
import { NavLink } from 'react-router-dom';

interface SidebarItemProps {
  icon: React.ElementType;
  text: string;
  to: string;
  collapsed?: boolean;
}

const SidebarItem = ({ icon: Icon, text, to, collapsed = false }: SidebarItemProps) => {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          'flex items-center gap-3 px-4 py-3 rounded-lg transition-all',
          'hover:bg-sidebar-accent hover:text-sidebar-accent-foreground',
          isActive 
            ? 'bg-sidebar-accent text-sidebar-accent-foreground font-medium' 
            : 'text-sidebar-foreground',
          collapsed && 'justify-center px-2'
        )
      }
    >
      <Icon className="h-5 w-5 shrink-0" />
      {!collapsed && <span>{text}</span>}
    </NavLink>
  );
};

const Sidebar = () => {
  // In a real app, you would use a state to control the collapse state
  const collapsed = false;

  return (
    <aside className="bg-sidebar h-full border-r border-sidebar-border">
      <div className="py-4">
        <div className="px-4 mb-6 flex items-center">
          {!collapsed && (
            <h2 className="text-lg font-semibold ml-2 text-sidebar-foreground">QA-T Agent</h2>
          )}
        </div>

        <div className="space-y-1 px-2">
          <SidebarItem
            icon={FileText}
            text="Manual Testing"
            to="/manual-testing"
            collapsed={collapsed}
          />
          <SidebarItem
            icon={Code}
            text="Automation Testing"
            to="/automation-testing"
            collapsed={collapsed}
          />
          <SidebarItem
            icon={BarChart}
            text="Result Dashboard"
            to="/dashboard"
            collapsed={collapsed}
          />
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
