import React, { useState, useEffect } from "react";
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import {
  BookOpen,
  CheckCircle,
  Clock,
  CalendarDays,
  Table2,
} from "lucide-react";
import { AnalyticsData } from "../../types";

const PIE_COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444"];

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const AnalyticsPage: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        setError(null);
        const response = await fetch(`${API_URL}/analytics`);
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data: AnalyticsData = await response.json();
        setAnalytics(data);
      } catch (err) {
        console.error("Failed to fetch analytics:", err);
        setError(
          `Failed to load data: ${
            (err as Error).message
          }. Ensure backend is running.`
        );
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl text-gray-700">
        Loading analytics...
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl text-red-600">
        Error: {error}
      </div>
    );
  }

  if (!analytics) {
    return (
      <div className="flex items-center justify-center min-h-screen text-xl text-gray-700">
        No analytics data available.
      </div>
    );
  }

  const coursePieData = [
    { name: "Completed Courses", value: analytics.course_counts.completed },
    {
      name: "Incomplete Courses",
      value: analytics.course_counts.total - analytics.course_counts.completed,
    },
  ];

  const sectionPieData = [
    { name: "Completed Sections", value: analytics.section_counts.completed },
    {
      name: "Incomplete Sections",
      value:
        analytics.section_counts.total - analytics.section_counts.completed,
    },
  ];

  const sortedDailyCompletions = [...analytics.daily_section_completions].sort(
    (a, b) =>
      new Date(a.completion_date).getTime() -
      new Date(b.completion_date).getTime()
  );

  const formatPercentage = (value: number) => `${(value * 100).toFixed(2)}%`;

  return (
    <div className="p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto bg-gray-50 min-h-screen">
      <h1 className="text-3xl sm:text-4xl font-extrabold text-gray-900 text-center mb-10 border-b-2 border-indigo-200 pb-4">
        Analytics Dashboard
      </h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-6 rounded-xl shadow-md flex flex-col items-center justify-center text-center transition-transform hover:scale-105 duration-300">
          <BookOpen size={48} className="text-indigo-500 mb-3" />
          <h2 className="text-xl font-semibold text-gray-800 mb-1">Courses</h2>
          <p className="text-3xl font-bold text-indigo-700 mb-2">
            {analytics.course_counts.completed} /{" "}
            {analytics.course_counts.total}
          </p>
          <p className="text-sm text-gray-500">Completed vs. Total</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md flex flex-col items-center justify-center text-center transition-transform hover:scale-105 duration-300">
          <CheckCircle size={48} className="text-emerald-500 mb-3" />
          <h2 className="text-xl font-semibold text-gray-800 mb-1">Sections</h2>
          <p className="text-3xl font-bold text-emerald-700 mb-2">
            {analytics.section_counts.completed} /{" "}
            {analytics.section_counts.total}
          </p>
          <p className="text-sm text-gray-500">Completed vs. Total</p>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md flex flex-col items-center justify-center text-center transition-transform hover:scale-105 duration-300">
          <Clock size={48} className="text-amber-500 mb-3" />
          <h2 className="text-xl font-semibold text-gray-800 mb-1">
            Avg. Completion Time
          </h2>
          <p className="text-3xl font-bold text-amber-700 mb-2">
            {analytics.average_course_completion_time_readable || "N/A"}
          </p>
          <p className="text-sm text-gray-500">Time to complete full courses</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <div className="bg-white p-6 rounded-xl shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 text-left">
            Course Completion Status
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={coursePieData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${formatPercentage(percent)}`
                }
              >
                {coursePieData.map((_, index) => (
                  <Cell
                    key={`cell-course-${index}`}
                    fill={PIE_COLORS[index % PIE_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [value, name]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="bg-white p-6 rounded-xl shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-4 text-left">
            Section Completion Status
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={sectionPieData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                fill="#82ca9d"
                dataKey="value"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name} ${formatPercentage(percent)}`
                }
              >
                {sectionPieData.map((_, index) => (
                  <Cell
                    key={`cell-section-${index}`}
                    fill={PIE_COLORS[index % PIE_COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value, name) => [value, name]} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-md mb-10">
        <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          Daily Section Completions{" "}
          <CalendarDays size={20} className="ml-2 text-indigo-500" />
        </h2>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart
            data={sortedDailyCompletions}
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="completion_date"
              angle={-45}
              textAnchor="end"
              height={60}
            />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar
              dataKey="completed_sections_count"
              fill="#6366F1"
              name="Completed Sections"
            />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-white p-6 rounded-xl shadow-md">
        <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center">
          All Courses Overview{" "}
          <Table2 size={20} className="ml-2 text-indigo-500" />
        </h2>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  Title
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  Completion Rate
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider whitespace-nowrap"
                >
                  Latest Completion Time
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {analytics.courses_table.length > 0 ? (
                analytics.courses_table.map((course) => (
                  <tr key={course.course_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {course.title}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {formatPercentage(course.completion_percentage)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                      {course.latest_completed_at_readable || "N/A"}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td
                    colSpan={3}
                    className="px-6 py-4 text-center text-sm text-gray-500"
                  >
                    No courses found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsPage;
