import { Metadata } from "next";
import MemoryDashboard from "@/components/memory/MemoryDashboard";

export const metadata: Metadata = {
  title: "Memory Dashboard",
  description: "Explore your interaction history and manage memory preferences",
};

export default function MemoryPage() {
  return <MemoryDashboard />;
} 