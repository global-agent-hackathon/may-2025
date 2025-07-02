import React from "react";

interface CourseHeaderProps {
  course: {
    description: string;
    title: string;
    created_at: number;
    level: string;
  };
}

const CourseHeader: React.FC<CourseHeaderProps> = ({ course }) => (
  <div className="pb-6 border-b border-gray-100 animate-fade-in">
    <div className="flex items-center gap-3 mb-4">
      <span
        className={`text-xs font-semibold px-3 py-1.5 rounded-full ${
          course.level === "Beginner"
            ? "text-emerald-700 bg-emerald-50 border border-emerald-200"
            : course.level === "Intermediate"
            ? "text-blue-700 bg-blue-50 border border-blue-200"
            : "text-purple-700 bg-purple-50 border border-purple-200"
        }`}
      >
        {course.level}
      </span>
      <span className="text-xs text-gray-400">
        {new Date(course.created_at * 1000).toLocaleDateString()}
      </span>
    </div>
    <h2 className="text-2xl font-bold text-gray-800 mb-2">{course.title}</h2>
    <p className="text-gray-600 leading-relaxed">{course.description}</p>
  </div>
);

export default CourseHeader;
