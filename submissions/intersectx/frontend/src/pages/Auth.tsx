import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { EnvelopeIcon, LockClosedIcon, UserIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../lib/api-client';

interface SignUpForm {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
}

interface LoginForm {
  email: string;
  password: string;
}

type UserType = 'vc' | 'founder';

interface VCSignUpForm extends SignUpForm {
  portfolio: string;
  companiesInvested: string;
  description?: string;
  websiteUrl?: string;
  linkedinUrl: string;
}

export default function Auth() {
  const [isLogin, setIsLogin] = useState(true);
  const [userType, setUserType] = useState<UserType>('vc');
  const [signUpForm] = useState<SignUpForm>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
  });
  const [loginForm, setLoginForm] = useState<LoginForm>({
    email: '',
    password: '',
  });
  const [authError, setAuthError] = useState<string | null>(null);
  const { login: loginUser } = useAuth();
  const navigate = useNavigate();
  const [vcSignUpForm, setVcSignUpForm] = useState<VCSignUpForm>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    portfolio: '',
    companiesInvested: '',
    description: '',
    websiteUrl: '',
    linkedinUrl: '',
  });

  const handleSignUp = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      if (userType === 'vc') {
        const payload = {
          first_name: vcSignUpForm.firstName,
          last_name: vcSignUpForm.lastName,
          email: vcSignUpForm.email,
          password: vcSignUpForm.password,
          user_type: userType,
          portfolio: parseInt(vcSignUpForm.portfolio, 10),
          companies_invested: parseInt(vcSignUpForm.companiesInvested, 10),
          description: vcSignUpForm.description,
          website_url: vcSignUpForm.websiteUrl,
          linkedin_url: vcSignUpForm.linkedinUrl,
        };
        await apiClient.post('/auth/vc-signup', payload);
        setIsLogin(true);
      } else {
        const payload = {
          first_name: signUpForm.firstName,
          last_name: signUpForm.lastName,
          email: signUpForm.email,
          password: signUpForm.password,
          user_type: userType,
        };
        await apiClient.post('/auth/signup', payload);
        setIsLogin(true);
      }
    } catch (err: any) {
      setAuthError(err.message || 'Signup failed');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError(null);
    try {
      const payload = {
        email: loginForm.email,
        password: loginForm.password,
      };
      
      interface LoginResponse {
        token: string;
        email: string;
        first_name: string;
        last_name: string;
        user_type?: 'vc' | 'founder';
      }
      
      const data = await apiClient.post<LoginResponse>('/auth/login', payload);
      
      if (data.token && data.email && data.first_name && data.last_name) {
        loginUser({
          email: data.email,
          first_name: data.first_name,
          last_name: data.last_name,
          token: data.token,
          user_type: data.user_type || 'vc',
        });
        navigate('/');
      }
    } catch (err: any) {
      setAuthError(err.message || 'Login failed');
    }
  };

  const handleFounderSignUp = () => {
    navigate('/founder-signup');
  };

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <a href="/" className="text-3xl font-bold text-purple hover:text-purple-dark transition-colors">
            Intersectx
          </a>
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-gray-900">
            {isLogin ? 'Sign in to your account' : 'Create your account'}
          </h2>
          <p className="mt-2 text-sm text-gray-600">
            {isLogin ? (
              <>
                Or{' '}
                <button
                  onClick={() => setIsLogin(false)}
                  className="font-medium text-indigo-600 hover:text-indigo-500"
                >
                  create a new account
                </button>
              </>
            ) : (
              <>
                Already have an account?{' '}
                <button
                  onClick={() => setIsLogin(true)}
                  className="font-medium text-indigo-600 hover:text-indigo-500"
                >
                  Sign in
                </button>
              </>
            )}
          </p>
        </div>

        {/* User Type Selection */}
        <div className="flex justify-center space-x-4">
          <button
            onClick={() => setUserType('vc')}
            className={`px-4 py-2 rounded-md transition-colors ${userType === 'vc' ? 'bg-purple text-white hover:bg-purple-dark' : 'bg-gray-100 text-primary hover:bg-purple-light/10'}`}
          >
            Venture Capitalist
          </button>
          <button
            onClick={() => setUserType('founder')}
            className={`px-4 py-2 rounded-md transition-colors ${userType === 'founder' ? 'bg-purple text-white hover:bg-purple-dark' : 'bg-gray-100 text-primary hover:bg-purple-light/10'}`}
          >
            Founder
          </button>
        </div>

        {/* Forms */}
        <div className="mt-8 bg-white py-8 px-4 shadow-sm border border-purple-light/20 sm:rounded-lg sm:px-10">
          {authError && (
            <div className="mb-4 text-red-500 text-center text-sm font-medium bg-red-50 p-2 rounded-md border border-red-100">{authError}</div>
          )}
          {isLogin ? (
            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email address
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <EnvelopeIcon className="h-5 w-5 text-purple-light" aria-hidden="true" />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={loginForm.email}
                    onChange={(e) => setLoginForm({ ...loginForm, email: e.target.value })}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="you@example.com"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                  Password
                </label>
                <div className="mt-1 relative rounded-md shadow-sm">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <LockClosedIcon className="h-5 w-5 text-purple-light" aria-hidden="true" />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    required
                    value={loginForm.password}
                    onChange={(e) => setLoginForm({ ...loginForm, password: e.target.value })}
                    className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="••••••••"
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900">
                    Remember me
                  </label>
                </div>

                <div className="text-sm">
                  <a href="#" className="font-medium text-indigo-600 hover:text-indigo-500">
                    Forgot your password?
                  </a>
                </div>
              </div>

              <div>
                <button
                  type="submit"
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple hover:bg-purple-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple transition-colors"
                >
                  Sign in
                </button>
              </div>
            </form>
          ) : (
            userType === 'vc' ? (
              <form onSubmit={handleSignUp} className="space-y-6">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="firstName" className="block text-sm font-medium text-primary">
                      First name
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <UserIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                      </div>
                      <input
                        id="firstName"
                        name="firstName"
                        type="text"
                        required
                        value={vcSignUpForm.firstName}
                        onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, firstName: e.target.value })}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="John"
                      />
                    </div>
                  </div>

                  <div>
                    <label htmlFor="lastName" className="block text-sm font-medium text-primary">
                      Last name
                    </label>
                    <div className="mt-1 relative rounded-md shadow-sm">
                      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <UserIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                      </div>
                      <input
                        id="lastName"
                        name="lastName"
                        type="text"
                        required
                        value={vcSignUpForm.lastName}
                        onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, lastName: e.target.value })}
                        className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                        placeholder="Doe"
                      />
                    </div>
                  </div>
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                    Email address
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <EnvelopeIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    </div>
                    <input
                      id="email"
                      name="email"
                      type="email"
                      autoComplete="email"
                      required
                      value={vcSignUpForm.email}
                      onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, email: e.target.value })}
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="you@example.com"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                    Password
                  </label>
                  <div className="mt-1 relative rounded-md shadow-sm">
                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <LockClosedIcon className="h-5 w-5 text-gray-400" aria-hidden="true" />
                    </div>
                    <input
                      id="password"
                      name="password"
                      type="password"
                      autoComplete="new-password"
                      required
                      value={vcSignUpForm.password}
                      onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, password: e.target.value })}
                      className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="••••••••"
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="portfolio" className="block text-sm font-medium text-gray-700">
                    Investment Value Portfolio (USD)
                  </label>
                  <div className="relative mt-1 rounded-md shadow-sm">
                    <span className="absolute inset-y-0 left-0 pl-3 flex items-center text-gray-400 text-sm">$</span>
                    <input
                      id="portfolio"
                      name="portfolio"
                      type="number"
                      min="0"
                      value={vcSignUpForm.portfolio}
                      onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, portfolio: e.target.value })}
                      className="block w-full pl-7 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="10,000,000"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="companiesInvested" className="block text-sm font-medium text-gray-700">
                    Number of Companies Invested In
                  </label>
                  <input
                    id="companiesInvested"
                    name="companiesInvested"
                    type="number"
                    min="0"
                    value={vcSignUpForm.companiesInvested}
                    onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, companiesInvested: e.target.value })}
                    className="block w-full mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2"
                    placeholder="e.g. 15"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                    Description
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    value={vcSignUpForm.description}
                    onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, description: e.target.value })}
                    className="block w-full mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2"
                    placeholder="Tell us about your VC firm..."
                    rows={3}
                  />
                </div>

                <div>
                  <label htmlFor="websiteUrl" className="block text-sm font-medium text-gray-700">
                    Website URL
                  </label>
                  <input
                    id="websiteUrl"
                    name="websiteUrl"
                    type="url"
                    value={vcSignUpForm.websiteUrl}
                    onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, websiteUrl: e.target.value })}
                    className="block w-full mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2"
                    placeholder="https://yourvc.com"
                  />
                </div>

                <div>
                  <label htmlFor="linkedinUrl" className="block text-sm font-medium text-gray-700">
                    LinkedIn URL
                  </label>
                  <input
                    id="linkedinUrl"
                    name="linkedinUrl"
                    type="url"
                    value={vcSignUpForm.linkedinUrl}
                    onChange={(e) => setVcSignUpForm({ ...vcSignUpForm, linkedinUrl: e.target.value })}
                    className="block w-full mt-1 border border-gray-300 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm px-3 py-2"
                    placeholder="https://linkedin.com/in/yourprofile"
                    required
                  />
                </div>

                <div>
                  <button
                    type="submit"
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Create account
                  </button>
                </div>
              </form>
            ) : (
              <div className="text-center space-y-6">
                <p className="text-gray-700">
                  To create a founder account, we need some additional information about your company and funding needs.
                </p>
                <button
                  onClick={handleFounderSignUp}
                  className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Continue to Founder Registration
                </button>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
} 