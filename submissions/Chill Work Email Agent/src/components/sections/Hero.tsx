'use client';

import Link from "next/link";

export default function Hero() {
    return (
        <section className="min-h-screen bg-zinc-900 py-20">
            <div className="container mx-auto text-center mt-20">
                <h1 className="text-4xl font-bold text-white mb-4">Email Agent</h1>
                <p className="text-xl text-white mb-8 mt-20">Simplify your email experience with AI Agent</p>
                <Link href="/sign-in">
                    <button className="bg-white text-black font-semibold py-2 px-6 rounded-lg hover:bg-gray-200 transition mt-10">
                        Get Started
                    </button>
                </Link>
            </div>
        </section>
    );
}