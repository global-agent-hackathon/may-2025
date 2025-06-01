import { useEffect, useState, useMemo } from "react";
import { Link, useNavigate } from "react-router";
import { Toaster, toast } from "sonner";
import { CourseSchema } from "../../types";
import { ArrowRight, Search } from "lucide-react";
import LevelDropdown from "./components/LevelDropDown";

const API_BASE_URL = import.meta.env.VITE_API_URL;

const greetings = [
  "Happy Learning!",
  "Welcome Back!",
  "Ready to learn something new?",
  "Let's dive into your courses.",
  "Keep up the great work!",
];

const LevelBadge = ({ level }: { level: string }) => {
  const levelStyles = {
    beginner: "bg-green-100 text-green-800",
    intermediate: "bg-sky-100 text-sky-800",
    advanced: "bg-purple-100 text-purple-800",
    default: "bg-slate-100 text-slate-800",
  };

  const style =
    levelStyles[level.toLowerCase() as keyof typeof levelStyles] ||
    levelStyles.default;

  return (
    <span
      className={`px-2.5 py-1 text-xs font-medium rounded-full tracking-wide ${style}`}
    >
      {level}
    </span>
  );
};

const ProgressBar = ({ percentage }: { percentage: number }) => (
  <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
    <div
      className={`${
        percentage === 100 ? "bg-green-600" : " bg-indigo-500"
      } h-1.5 rounded-full transition-all duration-500 ease-out`}
      style={{ width: `${percentage}%` }}
    />
  </div>
);

const CourseCard = ({
  course,
  index,
}: {
  course: CourseSchema;
  index: number;
}) => {
  const navigate = useNavigate();

  return (
    <div
      onClick={() => navigate(`/course/${course.course_id}`)}
      className="group bg-white rounded-xl border border-slate-200/80 p-5 flex flex-col justify-between
                 transition-all duration-300 ease-in-out
                 hover:shadow-lg hover:border-indigo-300 hover:-translate-y-1 cursor-pointer"
      style={{
        animation: `card-fade-in 0.5s ease-out ${index * 100}ms backwards`,
      }}
    >
      <div>
        <div className="flex justify-between items-start mb-3">
          <h3 className="text-lg font-semibold text-slate-800 pr-4">
            {course.title}
          </h3>
          <LevelBadge level={course.level} />
        </div>
        <p className="text-slate-500 text-sm mb-6 line-clamp-2">
          {course.description}
        </p>
      </div>
      <div className="mt-auto">
        <div className="flex justify-between items-center mb-2">
          <span
            className={`text-sm font-medium ${
              course.completion_percentage === 1
                ? "text-green-600"
                : "text-indigo-600"
            }`}
          >
            {(course.completion_percentage * 100).toFixed(1)}% Complete
          </span>
          <div className="text-slate-400 group-hover:text-indigo-600 transition-colors duration-300 opacity-0 group-hover:opacity-100">
            <ArrowRight size={14} />
          </div>
        </div>
        <ProgressBar percentage={course.completion_percentage * 100} />
      </div>
    </div>
  );
};

export default function CourseListPage() {
  const [courses, setCourses] = useState<CourseSchema[]>([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [greeting] = useState(
    greetings[Math.floor(Math.random() * greetings.length)]
  );

  useEffect(() => {
    const fetchCourses = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await fetch(`${API_BASE_URL}/courses`);
        if (!response.ok) {
          throw new Error(`Failed to fetch: ${response.statusText}`);
        }
        let data: CourseSchema[] = await response.json();
        data = data.map((c) => ({
          ...c,
          completion_percentage:
            c.completion_percentage ?? Math.floor(Math.random() * 100),
        }));
        setCourses(data);
      } catch (err) {
        const errorMessage =
          err instanceof Error ? err.message : "An unknown error occurred";
        setError(errorMessage);
        toast.error(errorMessage);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, []);

  const filteredCourses = useMemo(() => {
    return courses
      .filter((course) =>
        course.title.toLowerCase().includes(searchTerm.toLowerCase())
      )
      .filter((course) =>
        selectedLevel
          ? course.level.toLowerCase() === selectedLevel.toLowerCase()
          : true
      );
  }, [courses, searchTerm, selectedLevel]);

  const uniqueLevels = useMemo(
    () => Array.from(new Set(courses.map((c) => c.level))).sort(),
    [courses]
  );

  return (
    <div className="min-h-screen bg-slate-50 font-sans">
      <Toaster richColors position="top-right" />
      <div className="max-w-6xl mx-auto p-4 sm:p-6 md:p-8">
        <header className="flex flex-col sm:flex-row justify-between items-center my-8 md:my-12">
          <div>
            <h1 className="text-4xl font-bold text-slate-800">{greeting}</h1>
            <p className="text-slate-500 mt-1">
              Let's continue your learning journey.
            </p>
          </div>
          <Link
            to="/create"
            className="mt-4 sm:mt-0 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg
                       flex items-center gap-2 shadow-sm
                       transition-all duration-300 ease-in-out transform hover:scale-105"
          >
            <svg
              className="w-5 h-5"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 20 20"
              fill="currentColor"
            >
              <path d="M10.75 4.75a.75.75 0 00-1.5 0v4.5h-4.5a.75.75 0 000 1.5h4.5v4.5a.75.75 0 001.5 0v-4.5h4.5a.75.75 0 000-1.5h-4.5v-4.5z" />
            </svg>
            New Course
          </Link>
        </header>

        <div className="mb-8 flex flex-col sm:flex-row items-center gap-3">
          <div className="relative w-full sm:w-auto flex-grow">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search size={16} />
            </div>
            <input
              type="text"
              placeholder="Search courses..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white text-slate-700"
            />
          </div>
          <LevelDropdown
            selectedLevel={selectedLevel}
            setSelectedLevel={setSelectedLevel}
            levels={uniqueLevels}
          />
        </div>

        {loading && (
          <div className="text-center text-slate-500 py-10">Loading...</div>
        )}
        {error && (
          <div className="text-center text-red-600 py-10">Error: {error}</div>
        )}

        {!loading &&
          !error &&
          (filteredCourses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredCourses.map((course, index) => (
                <CourseCard
                  key={course.course_id}
                  course={course}
                  index={index}
                />
              ))}
            </div>
          ) : (
            <div className="text-center py-16 px-8 bg-white rounded-xl border border-slate-200">
              <h3 className="text-xl font-semibold text-slate-700">
                {courses.length > 0 ? "No courses found" : "Let's begin!"}
              </h3>
              <p className="text-slate-500 mt-2">
                {courses.length > 0
                  ? "Try adjusting your search or create a new course to get started."
                  : "Let's start with making some cool courses"}
              </p>
            </div>
          ))}
      </div>
    </div>
  );
}
