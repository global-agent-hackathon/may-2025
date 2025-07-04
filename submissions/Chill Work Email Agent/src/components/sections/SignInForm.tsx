'use client';

import Link from "next/link";

export default function SignInForm() {
    return (
        <div className="min-h-screen bg-black flex items-center justify-center">
            <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md space-y-6">
                <div className="flex items-center justify-center mb-6">
                    <h1 className="text-2xl font-bold text-black">Email Agent</h1>
                </div>
                <h2 className="text-xl font-semibold text-center text-black">Welcome Back</h2>

                {/* OAuth */}
                <p className="text-center text-gray-500 mb-6">Continue with Google account</p>
                <Link href="http://localhost:8000/login">
                    <button className="border-2 border-zinc-900 text-black font-semibold py-2 px-4 rounded-lg bg-transparent hover:bg-zinc-900 hover:text-zinc-100 transition mx-22">
                        Sign In with Google
                    </button>
                </Link>

                <div className="text-center text-sm mt-10">
                    <span className="text-gray-500">Don&apos;t have an account? </span>
                    <Link href="/sign-up" className="text-zinc-800 hover:underline">
                        Sign up
                    </Link>
                </div>
            </div>
        </div>
    );
}