"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";
import { ArrowUpRight, Heart } from "lucide-react";
import { Github, Linkedin, X } from "lucide-react";

export default function Footer() {
  const year = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  return (
    <div className="flex justify-center w-full mb-7">
      <footer className="z-20 mt-16 flex max-h-fit min-h-[12rem] flex-col justify-between gap-10 rounded-xl border-2 border-blue-500/50 bg-gradient-to-br from-blue-50/40 to-blue-200/30 p-8 backdrop-blur-md md:flex-row md:items-center w-full max-w-[70%] shadow-lg">
        <section className="flex-1">
          <aside className="flex flex-col gap-[10px]">
            <div className="flex items-center gap-3">
              <Image src="/logo.png" alt="FLUX Logo" width={38} height={38} className="rounded" />
              <p className="font-secondary text-xl font-extrabold tracking-tight md:text-4xl text-gray-900">
                FLUX
                <span className="text-blue-600">.</span>
              </p>
            </div>
            <p className="text-sm text-gray-700">
              Superintelligent forms & insights, powered by AI.
            </p>
          </aside>

          <aside className="mt-6 flex flex-wrap items-center gap-6">
            <div className="flex items-center gap-4">
              <Link
                href="https://github.com/srthkdev/"
                className="group rounded-full p-2 transition-colors hover:bg-blue-200/50 text-gray-800"
                target="_blank"
                rel="noopener"
              >
                <Github className="h-5 w-5 transition-transform group-hover:scale-110" />
              </Link>
              <Link
                href="https://x.com/sarthxk20/"
                className="group rounded-full p-2 transition-colors hover:bg-blue-200/50 text-gray-800"
                target="_blank"
                rel="noopener"
              >
                <X className="h-5 w-5 transition-transform group-hover:scale-110" />
              </Link>
              <Link
                href="https://www.linkedin.com/in/sarthak-jain-32b114228/"
                className="group rounded-full p-2 transition-colors hover:bg-blue-200/50 text-gray-800"
                target="_blank"
                rel="noopener"
              >
                <Linkedin className="h-5 w-5 transition-transform group-hover:scale-110" />
              </Link>
            </div>

            <div className="h-4 w-px bg-blue-300/50"></div>

            <p className="text-sm text-gray-700">
              Made with <Heart className="inline h-3 w-3 text-red-500" /> by{" "}
              <Link
                href="https://github.com/srthkdev/"
                className="font-medium text-gray-900 hover:text-blue-600 transition-colors"
                target="_blank"
                rel="noopener"
              >
                Sarthak
              </Link>
            </p>
          </aside>

          <aside className="mt-6 flex flex-col md:flex-row md:flex-wrap gap-4 text-sm text-gray-700">
            <Link
              href="/#"
              className="hover:text-blue-700 transition-colors"
            >
              Privacy Policy
            </Link>
            <span className="hidden md:inline text-blue-400">•</span>
            <Link href="/#" className="hover:text-blue-700 transition-colors">
              Terms of Service
            </Link>
            <span className="hidden md:inline text-blue-400">•</span>
            <p>&copy; {year} | All Rights Reserved.</p>
          </aside>
        </section>

        <section
          onClick={scrollToTop}
          className="group flex h-[8rem] w-full cursor-pointer items-center justify-center rounded-xl border-2 border-blue-500 bg-blue-500/80 text-white transition-all duration-300 hover:bg-blue-400 md:w-[12rem] shadow-md"
        >
          <div className="relative">
            <ArrowUpRight className="h-16 w-16 rotate-45 transition-transform duration-300 ease-out group-hover:rotate-0" />
            <span className="absolute -bottom-6 left-1/2 w-max -translate-x-1/2 text-xs font-medium opacity-0 transition-opacity duration-300 group-hover:opacity-100">
              Back to top
            </span>
          </div>
        </section>
      </footer>
    </div>
  );
} 