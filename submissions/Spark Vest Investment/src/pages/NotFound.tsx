import { useLocation } from "react-router-dom";
import { useEffect } from "react";
import { Link } from "react-router-dom";

const NotFound = () => {
  const location = useLocation();

  useEffect(() => {
    console.error(
      "404 Error: User attempted to access non-existent route:",
      location.pathname
    );
  }, [location.pathname]);

    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <h1 className="text-6xl font-bold text-red-500 mb-4">404</h1>
          <p className="text-xl text-gray-600 mb-4">Oops! Page does not exist.</p>
          <p className="text-gray-500 mb-6">
            What can we say, the developer is really lazy. But he might get it
            done if you are willing to contribute and{" "}
            <span className="relative inline-block">
              <span className="relative z-10 text-blue-500 cursor-pointer hover:text-white transition duration-300">
                <span className="absolute inset-0 bg-blue-500 rounded-lg scale-105 opacity-0 hover:opacity-100 transition duration-300"></span>
                <a href="https://github.com/sponsors/yashksaini-coder" target="_blank" className="relative px-2 py-1">help cover his cloud charges by sponsoring him on GitHub.</a>
              </span>
            </span>
            .
          </p>
          <a href="/" className="text-blue-500 hover:text-blue-700 underline">
            Return to Home
          </a>
        </div>
      </div>
    );
};

export default NotFound;
