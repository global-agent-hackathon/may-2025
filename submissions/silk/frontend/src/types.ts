export type SessionProgress = "in_progress" | "success" | "error";

export interface SessionSchema {
  session_id: string;
  actions: string[];
  description: string;
  level: string;
  progress: SessionProgress;
}

export interface CourseSchema {
  course_id: string;
  session_id: string;
  title: string;
  description: string;
  level: string;
  created_at: number;
  completion_percentage: number;
}

export interface SectionSchema {
  section_id: string;
  course_id: string;
  title: string;
  description: string;
  content: string;
  section_order: number;
  created_at: number;
  is_completed: number;
  completed_at: number | null;
}

export interface ChatErrorMessage {
  error: string;
  session_id: string;
}

interface CourseAnalytic {
  course_id: string;
  title: string;
  completion_percentage: number;
  latest_completed_at: number | null;
  latest_completed_at_readable: string | null;
}

interface DailyCompletion {
  completion_date: string;
  completed_sections_count: number;
}

export interface AnalyticsData {
  average_course_completion_time_readable: string | null;
  average_course_completion_time_seconds: number | null;
  course_counts: {
    completed: number;
    total: number;
  };
  courses_table: CourseAnalytic[];
  daily_section_completions: DailyCompletion[];
  section_counts: {
    completed: number;
    total: number;
  };
}
