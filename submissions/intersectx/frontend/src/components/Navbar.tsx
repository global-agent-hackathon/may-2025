import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Disclosure, Menu } from '@headlessui/react';
import { Bars3Icon, XMarkIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../context/AuthContext';
import { useEffect, useState } from 'react';

const navigation = [
  { name: 'Home', href: '/' },
  { name: 'IntersectX Chat', href: '/intersectx-chat' },
];

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ');
}

export default function Navbar() {
  const location = useLocation();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);
  
  useEffect(() => {
    const handleScroll = () => {
      const isScrolled = window.scrollY > 10;
      if (isScrolled !== scrolled) {
        setScrolled(isScrolled);
      }
    };
    
    window.addEventListener('scroll', handleScroll);
    return () => {
      window.removeEventListener('scroll', handleScroll);
    };
  }, [scrolled]);

  const handleLogout = () => {
    logout();
    navigate('/auth');
  };
  
  const initials = user && user.first_name && user.last_name
    ? `${user.first_name[0] ?? ''}${user.last_name[0] ?? ''}`.toUpperCase()
    : '';

  return (
    <Disclosure as="nav" className={`fixed w-full top-0 z-[100] transition-all duration-300 ${scrolled ? 'bg-white shadow-sm' : 'bg-transparent backdrop-blur-sm'}`}>
      {({ open }) => (
        <>
          <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
            <div className="flex h-16 justify-between">
              <div className="flex">
                <div className="flex flex-shrink-0 items-center">
                  <Link to="/" className="flex flex-row items-center gap-2">
                    {/* Logo image - increased size and added margin-right for spacing */}
                    <img src="/logo.png" alt="VentureInsights Logo" className="w-14 h-14" />
                    {/* Text to the right of the logo */}
                    <span className="text-lg font-medium text-primary">Intersectx</span>
                  </Link>
                </div>
                
                <div className="hidden sm:ml-6 sm:flex sm:space-x-4">
                  {navigation.map((item) => (
                    <Link
                      key={item.name}
                      to={item.href}
                      className={classNames(
                        location.pathname === item.href
                          ? 'text-purple-dark font-semibold'
                          : 'font-medium text-secondary hover:text-primary',
                        'inline-flex items-center px-3 py-2 text-base transition-colors duration-200'
                      )}
                    >
                      {item.name}
                    </Link>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center gap-4">
                
                {user ? (
                  <Menu as="div" className="relative">
                    <Menu.Button className="flex items-center justify-center w-10 h-10 rounded-full bg-purple-dark text-white font-bold text-lg shadow hover:bg-purple transition-colors focus:outline-none">
                      {initials}
                    </Menu.Button>
                    <Menu.Items className="absolute right-0 mt-2 w-32 origin-top-right rounded-md bg-white shadow-lg ring-1 ring-purple-light ring-opacity-10 focus:outline-none z-50">
                      <div className="py-1">
                        <Menu.Item>
                          {({ active }) => (
                            <button
                              onClick={handleLogout}
                              className={classNames(
                                active ? 'bg-purple-light/10' : '',
                                'block w-full px-4 py-2 text-left text-sm text-primary'
                              )}
                            >
                              Logout
                            </button>
                          )}
                        </Menu.Item>
                      </div>
                    </Menu.Items>
                  </Menu>
                ) : (
                  <Link
                    to="/auth"
                    className="inline-flex items-center justify-center rounded-md border border-transparent bg-purple-dark px-4 py-2 text-base font-medium text-white hover:bg-purple transition-colors"
                  >
                    Sign in
                  </Link>
                )}
              </div>
              
              <div className="-mr-2 flex items-center sm:hidden">
                {/* Mobile menu button */}
                <Disclosure.Button className="inline-flex items-center justify-center rounded-md p-2 text-secondary hover:bg-purple-light/10 hover:text-primary focus:outline-none focus:ring-2 focus:ring-inset focus:ring-purple-primary">
                  <span className="sr-only">Open main menu</span>
                  {open ? (
                    <XMarkIcon className="block h-6 w-6" aria-hidden="true" />
                  ) : (
                    <Bars3Icon className="block h-6 w-6" aria-hidden="true" />
                  )}
                </Disclosure.Button>
              </div>
            </div>
          </div>

          <Disclosure.Panel className="sm:hidden">
            <div className="space-y-1 pb-3 pt-2 bg-off-white">
              {navigation.map((item) => (
                <Disclosure.Button
                  key={item.name}
                  as={Link}
                  to={item.href}
                  className={classNames(
                    location.pathname === item.href
                      ? 'bg-purple-light/20 border-purple-dark text-purple-dark font-semibold'
                      : 'border-transparent text-secondary hover:bg-purple-light/10 hover:border-purple-primary hover:text-primary',
                    'block border-l-4 py-3 pl-3 pr-4 text-base font-medium'
                  )}
                >
                  {item.name}
                </Disclosure.Button>
              ))}
              

            </div>
          </Disclosure.Panel>
        </>
      )}
    </Disclosure>
  );
}