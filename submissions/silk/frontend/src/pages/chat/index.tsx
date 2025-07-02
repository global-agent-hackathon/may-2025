import { useCallback, useEffect, useRef, useState } from "react";
import { BookOpen, X, CheckCircle, Save, Trash2 } from "lucide-react";
import { io, Socket } from "socket.io-client";
import { toast, Toaster } from "sonner";

import CourseHeader from "./components/CourseHeader";
import SectionToggle from "./components/SectionToggle";
import Modal from "./components/Modal";
import InputForm from "./components/InputForm";
import {
  ChatErrorMessage,
  CourseSchema,
  SectionSchema,
  SessionSchema,
} from "../../types";

function Chat() {
  const [userInputDescription, setUserInputDescription] = useState("");
  const [selectedLevel, setSelectedLevel] = useState("Beginner");
  const [session, setSession] = useState<SessionSchema | null>(null);
  const [course, setCourse] = useState<CourseSchema | null>(null);
  const [sections, setSections] = useState<SectionSchema[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [openSections, setOpenSections] = useState<Set<string>>(new Set());
  const [modalSection, setModalSection] = useState<SectionSchema | null>(null);
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const socketRef = useRef<Socket | null>(null);
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

  const scrollToBottom = useCallback(() => {
    window.scrollTo({
      top: document.documentElement.scrollHeight,
      behavior: "smooth",
    });
  }, []);

  useEffect(() => {
    socketRef.current = io(`${API_BASE_URL}/create`);

    socketRef.current.on("connect", () =>
      console.log("Connected to WebSocket server")
    );
    socketRef.current.on("disconnect", () =>
      console.log("Disconnected from WebSocket server")
    );

    socketRef.current.on("connect_error", (err) => {
      console.error("WebSocket connection error:", err);
      const connError =
        "Failed to connect to the course service. Please check your internet connection and try again.";
      setError(connError);
      toast.error(connError);
      setSession(null);
    });

    socketRef.current.on("session_update", async (data) => {
      setSession(data);

      if (data.course_id) {
        try {
          await fetchCourseData(data.course_id);
        } catch (fetchErr) {
          const errMessage =
            fetchErr instanceof Error
              ? fetchErr.message
              : "Failed to load course data.";
          setError(errMessage);
          toast.error(`${errMessage}`);
        }
      }

      if (data.progress === "in_progress") {
        setError(null);
      } else if (data.progress === "success") {
        if (data.course_id) {
          toast.success("🎉 Your amazing course is ready!");
          setError(null);
        } else {
          const errMsg =
            "Course creation was successful, but we couldn't retrieve the course ID.";
          setError(errMsg);
          toast.error(errMsg);
          setCourse(null);
          setSections([]);
        }
      } else if (data.progress === "failed") {
        const errMsg =
          data.error_message || "Oops! Course creation couldn't be completed.";
        setError(errMsg);
        toast.error(errMsg);
        setCourse(null);
        setSections([]);
      }

      scrollToBottom();
    });

    socketRef.current.on("error", (data: ChatErrorMessage) => {
      const errorMessage =
        data.error || "An unexpected issue occurred with the service.";
      toast.error(errorMessage);
      setError(errorMessage);
      setSession(null);
      setCourse(null);
      setSections([]);
    });

    return () => {
      if (socketRef.current) socketRef.current.disconnect();
    };
  }, [API_BASE_URL, course]);

  const fetchCourseData = async (courseId: string) => {
    if (!courseId) {
      const noIdError = "Course ID is missing, cannot fetch details.";
      setError(noIdError);
      toast.error(noIdError);
      setSession(
        (prev) =>
          ({
            ...(prev || {
              progress: "in_progress",
              actions: [],
              course_id: null,
            }),
            progress: "error",
          } as SessionSchema)
      );
      throw new Error(noIdError);
    }
    try {
      const courseResponse = await fetch(
        `${API_BASE_URL}/course?id=${courseId}`
      );
      if (!courseResponse.ok)
        throw new Error(
          `Failed to fetch course: ${courseResponse.statusText} (${courseResponse.status})`
        );
      const courseData: CourseSchema = await courseResponse.json();
      setCourse(courseData);

      const sectionsResponse = await fetch(
        `${API_BASE_URL}/sections?course_id=${courseId}`
      );
      if (!sectionsResponse.ok)
        throw new Error(
          `Failed to fetch sections: ${sectionsResponse.statusText} (${sectionsResponse.status})`
        );
      const sectionsData: SectionSchema[] = await sectionsResponse.json();
      setSections(sectionsData);
      setError(null);
    } catch (error) {
      console.error("Error fetching course data:", error);
      const errorMessage =
        error instanceof Error ? error.message : "Failed to load course data.";
      setError(errorMessage);
      toast.error(`Data Load Failed: ${errorMessage}`);
      setSession(
        (prev) =>
          ({
            ...(prev || { progress: "idle", actions: [], course_id: null }),
            progress: "error",
          } as SessionSchema)
      );
      throw error;
    }
  };

  const handleSendMessage = (
    e: React.FormEvent<HTMLFormElement> | React.MouseEvent<HTMLButtonElement>
  ) => {
    e.preventDefault();
    const trimmedDescription = userInputDescription.trim();
    if (!trimmedDescription || session?.progress === "in_progress") return;

    setError(null);
    setCourse(null);
    setSections([]);
    setSession({
      session_id: crypto.randomUUID(),
      description: trimmedDescription,
      level: selectedLevel,
      progress: "in_progress",
      actions: ["Initializing course creation..."],
    });

    socketRef.current!.emit("start_creation", {
      description: trimmedDescription,
      level: selectedLevel,
    });
  };

  const toggleSection = (sectionId: string) => {
    const newOpenSections = new Set(openSections);
    if (newOpenSections.has(sectionId)) {
      newOpenSections.delete(sectionId);
    } else {
      newOpenSections.add(sectionId);
    }
    setOpenSections(newOpenSections);
  };

  const openModal = (section: SectionSchema) => {
    setModalSection(section);
  };

  const closeModal = () => {
    setModalSection(null);
  };

  const resetStateForNewAttempt = () => {
    setError(null);
    setSession(null);
    setUserInputDescription("");
    setCourse(null);
    setSections([]);
    setOpenSections(new Set());
    setIsDeleting(false);
  };

  const handleSaveAndProceed = () => {
    if (course?.course_id) {
      window.location.href = `/course/${course.course_id}`;
    } else {
      toast.error("Cannot proceed, course ID is missing.");
    }
  };

  const handleDeleteCourse = async () => {
    if (!course?.course_id || isDeleting) return;

    setIsDeleting(true);
    toast.loading("Deleting course...", { id: "delete-course-toast" });

    try {
      const response = await fetch(
        `${API_BASE_URL}/course?id=${course.course_id}`,
        {
          method: "DELETE",
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.message || `Failed to delete course: ${response.statusText}`
        );
      }

      toast.success("Course deleted successfully!", {
        id: "delete-course-toast",
      });
      resetStateForNewAttempt();
    } catch (err) {
      const errMessage =
        err instanceof Error ? err.message : "Something wen't wrong";
      console.error("Error deleting course:", err);
      toast.error(errMessage || "Failed to delete course.", {
        id: "delete-course-toast",
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const isProcessing = session?.progress === "in_progress";
  const courseCreatedSuccessfully =
    session?.progress === "success" && course !== null;
  const currentAction =
    session?.actions && session.actions.length > 0
      ? session.actions[session.actions.length - 1]
      : null;
  const displayError = error && session?.progress === "error";

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/30">
      <Toaster />

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div
          className={`${
            !course && !isProcessing && !courseCreatedSuccessfully
              ? "min-h-[80vh] flex flex-col justify-center"
              : ""
          }`}
        >
          <InputForm
            description={userInputDescription}
            setDescription={setUserInputDescription}
            selectedLevel={selectedLevel}
            setSelectedLevel={setSelectedLevel}
            handleSendMessage={handleSendMessage}
            isProcessing={courseCreatedSuccessfully || isProcessing}
          />

          {(course || isProcessing || displayError) && (
            <div className={`mt-8`}>
              {" "}
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
                {course && !displayError && (
                  <div className="p-6 space-y-6">
                    <CourseHeader course={course} />

                    {sections.length > 0 && (
                      <div className="space-y-4">
                        <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                          <BookOpen className="w-5 h-5" />
                          Course Curriculum
                        </h3>
                        <div className="space-y-3">
                          {sections
                            .sort((a, b) => a.section_order - b.section_order)
                            .map((section) => (
                              <SectionToggle
                                key={section.section_id}
                                section={section}
                                isOpen={openSections.has(section.section_id)}
                                onToggle={() =>
                                  toggleSection(section.section_id)
                                }
                                onOpenModal={() => openModal(section)}
                              />
                            ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {isProcessing && (
                  <div
                    className={`p-6 ${
                      course ? "border-t border-gray-100" : ""
                    }`}
                  >
                    <div className="flex items-center justify-center gap-3 text-blue-600">
                      <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                      <p className="font-medium">Creating your course...</p>
                    </div>
                    {currentAction && (
                      <p className="text-center text-gray-600 text-sm mt-2">
                        {currentAction}
                      </p>
                    )}
                  </div>
                )}

                {courseCreatedSuccessfully && (
                  <div className="p-6 border-t border-gray-100 text-center space-y-4">
                    <div className="flex items-center justify-center gap-2 text-emerald-600">
                      <CheckCircle className="w-6 h-6" />
                      <p className="font-semibold text-lg">
                        Course Created Successfully!
                      </p>
                    </div>
                    <p className="text-gray-600">
                      What would you like to do next?
                    </p>
                    <div className="flex flex-col sm:flex-row justify-center gap-3">
                      <button
                        onClick={handleSaveAndProceed}
                        className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors duration-200 font-semibold shadow-md hover:shadow-lg active:scale-[0.98]"
                      >
                        <Save className="w-5 h-5" />
                        Save & Proceed
                      </button>
                      <button
                        onClick={handleDeleteCourse}
                        disabled={isDeleting}
                        className="flex items-center justify-center gap-2 px-6 py-3 bg-red-50 text-red-700 rounded-xl border border-red-200 hover:bg-red-100 transition-colors duration-200 font-semibold shadow-sm hover:shadow-md active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {isDeleting ? (
                          <div className="w-5 h-5 border-2 border-red-700 border-t-transparent rounded-full animate-spin" />
                        ) : (
                          <Trash2 className="w-5 h-5" />
                        )}
                        {isDeleting ? "Deleting..." : "Delete Course"}
                      </button>
                    </div>
                  </div>
                )}

                {displayError && (
                  <div className="p-6 text-center">
                    <div className="text-red-500 mb-4">
                      <X className="w-12 h-12 mx-auto mb-2" />
                      <p className="font-semibold">Something went wrong</p>
                      <p className="text-sm text-gray-600 mt-1">{error}</p>
                    </div>
                    <button
                      onClick={resetStateForNewAttempt}
                      className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
                    >
                      Try Again
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={!!modalSection}
        onClose={closeModal}
        section={modalSection}
      />
    </div>
  );
}

export default Chat;
