import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { createBrowserRouter, RouterProvider } from "react-router";
import Chat from "./pages/chat";
import CourseListPage from "./pages/course_list";
import Course from "./pages/course";
import AnalyticsPage from "./pages/analytics";
import Layout from "./components/Layout";

const router = createBrowserRouter([
  {
    path: "/",
    element: <Layout />,
    children: [
      { index: true, element: <CourseListPage /> },
      { path: "courses", element: <CourseListPage /> },
      { path: "create", element: <Chat /> },
      { path: "course/:course_id", element: <Course /> },
      { path: "analytics", element: <AnalyticsPage /> },
    ],
  },
]);

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <RouterProvider router={router} />
  </StrictMode>
);
