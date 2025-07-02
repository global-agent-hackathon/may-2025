import { useEffect, useState } from "react";
import { useParams } from "react-router";
import ReactMarkdown from "react-markdown";
import rehypeRaw from "rehype-raw";

import { ArrowLeft, ArrowRight, CheckCircle, Menu, X } from "lucide-react";
import { CourseSchema, SectionSchema } from "../../types";

export default function Course() {
  const params = useParams();
  const [course, setCourse] = useState<CourseSchema | null>(null);
  const [sections, setSections] = useState<SectionSchema[]>([]);
  const [currentSectionIndex, setCurrentSectionIndex] = useState<number | null>(
    null
  );
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    fetch(`${import.meta.env.VITE_API_URL}/course?id=${params.course_id}`)
      .then((res) => res.json())
      .then((data: CourseSchema) => setCourse(data));

    fetch(
      `${import.meta.env.VITE_API_URL}/sections?course_id=${params.course_id}`
    )
      .then((res) => res.json())
      .then((data: SectionSchema[]) => {
        const sortedSections = data.sort(
          (a, b) => a.section_order - b.section_order
        );
        setSections(sortedSections);
        setCurrentSectionIndex(null);
      });
  }, [params.course_id]);

  const currentSection =
    currentSectionIndex !== null && currentSectionIndex < sections.length
      ? sections[currentSectionIndex]
      : null;

  const handleNextSection = () => {
    if (currentSectionIndex === null) {
      setCurrentSectionIndex(0);
    } else if (currentSectionIndex < sections.length - 1) {
      setCurrentSectionIndex(currentSectionIndex + 1);
    }
  };

  const handlePrevSection = () => {
    if (currentSectionIndex === 0) {
      setCurrentSectionIndex(null);
    } else if (currentSectionIndex !== null && currentSectionIndex > 0) {
      setCurrentSectionIndex(currentSectionIndex - 1);
    }
  };

  const selectSectionAndCloseSidebar = (index: number | null) => {
    setCurrentSectionIndex(index);
    setIsSidebarOpen(false);
  };

  const handleMarkSectionComplete = async (
    sectionId: string,
    isChecked: boolean
  ) => {
    if (isChecked) {
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/section/complete`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ section_id: sectionId }),
          }
        );

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        setSections((prevSections) =>
          prevSections.map((sec) =>
            sec.section_id === sectionId ? { ...sec, is_completed: 1 } : sec
          )
        );

        fetch(`${import.meta.env.VITE_API_URL}/course?id=${params.course_id}`)
          .then((res) => res.json())
          .then((data: CourseSchema) => setCourse(data));
      } catch (error) {
        console.error(`Failed to mark section ${sectionId} complete:`, error);
        alert(`Failed to mark section complete. Please try again.`);
      }
    }
  };

  if (!course)
    return (
      <div className="p-8 text-center text-gray-600">
        Loading course details...
      </div>
    );

  return (
    <div className="flex min-h-screen bg-gray-50 relative">
      <button
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-full bg-blue-600 text-white shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        onClick={() => setIsSidebarOpen(!isSidebarOpen)}
      >
        {isSidebarOpen ? (
          <X className="h-6 w-6" />
        ) : (
          <Menu className="h-6 w-6" />
        )}
      </button>

      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={() => setIsSidebarOpen(false)}
        ></div>
      )}

      <aside
        className={`fixed sidebar-scrollbar-hidden top-0 max-h-[100dvh] overflow-auto inset-y-0 left-0 z-50 w-72 bg-white border-r border-gray-200 p-6 flex flex-col shadow-lg
                   transform transition-transform duration-300 ease-in-out lg:static lg:translate-x-0
                   ${isSidebarOpen ? "translate-x-0" : "-translate-x-full"}`}
      >
        <h1 className="text-xl font-bold text-gray-900 mb-6 tracking-tight">
          {course.title}
        </h1>

        <nav className="flex-grow space-y-2 overflow-y-auto pr-2 -mr-2">
          <button
            onClick={() => selectSectionAndCloseSidebar(null)}
            className={`block text-left w-full p-3 rounded-lg transition-colors duration-200 ease-in-out ${
              currentSectionIndex === null
                ? "bg-blue-600 text-white font-semibold shadow-md"
                : "text-gray-700 hover:bg-gray-100"
            }`}
          >
            Course Overview
          </button>
          {sections.map((section, index) => (
            <button
              key={section.section_id}
              onClick={() => selectSectionAndCloseSidebar(index)}
              className={`flex items-center justify-between w-full p-3 rounded-lg transition-colors duration-200 ease-in-out ${
                currentSectionIndex === index
                  ? "bg-blue-100 text-blue-800 font-medium"
                  : "text-gray-700 hover:bg-gray-100"
              }`}
            >
              <span className="text-left w-[90%]">{section.title}</span>
              {section.is_completed === 1 && (
                <CheckCircle className="text-green-500 size-4" />
              )}
            </button>
          ))}
        </nav>
      </aside>

      <main className="flex-1 p-6 flex flex-col max-h-dvh overflow-auto">
        <div className="">
          <div className="p-4 rounded-xl border border-gray-100">
            {currentSectionIndex === null ? (
              <div className="text-center py-16">
                <h2 className="text-3xl md:text-5xl font-extrabold text-gray-900 mb-6 leading-tight">
                  Welcome to <br />
                  <span className="text-blue-600">{course.title}</span>
                </h2>
                <p className="text-lg text-gray-700 w-[80%] mx-auto mb-10 leading-relaxed">
                  {course.description}
                </p>
                <button
                  onClick={handleNextSection}
                  className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-semibold rounded-full shadow-lg text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-4 focus:ring-blue-500 focus:ring-opacity-50 transition transform hover:-translate-y-1"
                >
                  Start Learning
                  <svg
                    className="ml-3 -mr-1 w-5 h-5"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                    xmlns="http://www.w3.org/2000/svg"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10.293 15.707a1 1 0 010-1.414L14.586 10l-4.293-4.293a1 1 0 111.414-1.414l5 5a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0z"
                      clipRule="evenodd"
                    ></path>
                  </svg>
                </button>
              </div>
            ) : currentSection ? (
              <article className="prose prose-sm md:prose-lg mx-auto">
                <ReactMarkdown rehypePlugins={[rehypeRaw]}>
                  {currentSection.content}
                </ReactMarkdown>

                <div className="flex items-center mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <input
                    type="checkbox"
                    id={`sectionComplete-${currentSection.section_id}`}
                    className="form-checkbox h-5 w-5 text-blue-600 rounded cursor-pointer"
                    checked={currentSection.is_completed === 1}
                    onChange={(e) =>
                      handleMarkSectionComplete(
                        currentSection.section_id,
                        e.target.checked
                      )
                    }
                    disabled={currentSection.is_completed === 1}
                  />
                  <label
                    htmlFor={`sectionComplete-${currentSection.section_id}`}
                    className="ml-3 cursor-pointer text-lg font-medium text-gray-900"
                  >
                    Mark this section as complete
                  </label>
                  {currentSection.is_completed === 1 && (
                    <span className="ml-2 text-green-600 text-sm">
                      (Completed!)
                    </span>
                  )}
                </div>
              </article>
            ) : (
              <div className="text-center py-16 text-gray-600">
                No content available for this section.
              </div>
            )}
          </div>

          <div className="flex justify-between mt-8 max-w-4xl mx-auto pb-4">
            <button
              onClick={handlePrevSection}
              disabled={
                currentSectionIndex === null || currentSectionIndex === 0
              }
              className="inline-flex gap-2 items-center px-6 py-3 border border-gray-300 text-base font-medium rounded-full shadow-sm text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              <ArrowLeft size={16} />
              Previous
            </button>

            <button
              onClick={handleNextSection}
              disabled={
                currentSectionIndex !== null &&
                currentSectionIndex >= sections.length - 1
              }
              className="inline-flex gap-2 items-center px-6 py-3 border border-transparent text-base font-medium rounded-full shadow-sm text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              Next Section
              <ArrowRight size={16} />
            </button>
          </div>
        </div>
      </main>
    </div>
  );
}
