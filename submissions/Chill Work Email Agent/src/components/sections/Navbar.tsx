'use client';

import Link from 'next/link';

export default function Navbar() {
    return (
        <header className="bg-zinc-900 py-4">
            <div className="container mx-auto flex justify-between items-center">
                <div className='flex space-x-4'>
                    <h1 className="text-2xl font-bold text-white">Email Agent</h1>
                </div>
                <Link href="/sign-in">
                    <button className="border-2 border-zinc-200 text-white font-semibold py-2 px-4 rounded-lg bg-transparent hover:bg-zinc-200 hover:text-zinc-900 transition">
                        Sign In
                    </button>
                </Link>
            </div>
        </header>
    );
}