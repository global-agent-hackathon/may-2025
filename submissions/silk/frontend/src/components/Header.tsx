import React, { useState } from "react";
import { Link } from "react-router";
import { Menu, X } from "lucide-react";

const Header: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const closeMenu = () => {
    setIsMenuOpen(false);
  };

  return (
    <header className="bg-white border-b border-gray-200 p-4 relative z-50">
      <nav className="container mx-auto flex justify-between items-center">
        <Link
          to="/"
          className="text-gray-900 text-xl font-semibold hover:text-gray-700 transition-colors duration-200"
          onClick={closeMenu}
        >
          Silk
        </Link>

        <ul className="hidden md:flex md:space-x-6 font-[300]">
          <li>
            <Link
              to="/"
              className="text-gray-600 text-base font-[300] hover:text-gray-900 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-gray-100"
              onClick={closeMenu}
            >
              Courses
            </Link>
          </li>
          <li>
            <Link
              to="/create"
              className="text-gray-600 text-base font-[300] hover:text-gray-900 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-gray-100"
              onClick={closeMenu}
            >
              Create Course
            </Link>
          </li>
          <li>
            <Link
              to="/analytics"
              className="text-gray-600 text-base font-[300] hover:text-gray-900 transition-colors duration-200 px-3 py-2 rounded-md hover:bg-gray-100"
              onClick={closeMenu}
            >
              Analytics
            </Link>
          </li>
        </ul>

        <button
          className="md:hidden text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-300 rounded-md p-2 transition-colors duration-200"
          onClick={toggleMenu}
          aria-label="Toggle navigation menu"
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </nav>

      {isMenuOpen && (
        <div className="md:hidden fixed inset-0 bg-white bg-opacity-95 z-40 flex flex-col items-center justify-center space-y-8 animate-fade-in-down">
          <button
            className="absolute top-4 right-4 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-gray-300 rounded-md p-2 transition-colors duration-200"
            onClick={toggleMenu}
            aria-label="Close navigation menu"
          >
            <X size={32} />
          </button>
          <ul className="flex flex-col space-y-6 text-center">
            <li>
              <Link
                to="/courses"
                className="text-gray-800 text-2xl font-medium hover:text-indigo-600 transition-colors duration-200"
                onClick={closeMenu}
              >
                Courses
              </Link>
            </li>
            <li>
              <Link
                to="/create"
                className="text-gray-800 text-2xl font-medium hover:text-indigo-600 transition-colors duration-200"
                onClick={closeMenu}
              >
                Create Course
              </Link>
            </li>
            <li>
              <Link
                to="/analytics"
                className="text-gray-800 text-2xl font-medium hover:text-indigo-600 transition-colors duration-200"
                onClick={closeMenu}
              >
                Analytics
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
};

export default Header;
