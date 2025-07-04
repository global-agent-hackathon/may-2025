'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/router';

export default function AuthButton() {
    const router = useRouter();

    const handleLogin = async () => {
        try {
            const response = await fetch('/api/proxy/login', {
                method: 'GET',
                credentials: 'include'
            });
            if (response.redirected) {
                window.location.href = response.url;
            }
        } catch (error) {
            console.error('Login failed:', error);
        }
    };

    return (
        <button
            onClick={handleLogin}
            className="oauth-button"
        >
            Sign In with Google
        </button>
    );
}
