import React, { useState } from 'react';
import { useConfig } from '../hooks/useConfig';

interface HeaderProps {
  onSearch?: (query: string) => void;
}

const Header: React.FC<HeaderProps> = ({ onSearch }) => {
  const { config } = useConfig();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const query = e.target.value;
    setSearchQuery(query);
    if (onSearch) {
      onSearch(query);
    }
  };

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (onSearch) {
      onSearch(searchQuery);
    }
  };

  return (
    <header>
      <div className="bg-cyber-black">
        <div className="max-w-container mx-auto px-4 py-4 md:py-6">
          <div className="flex items-center">
            <h1 className="text-2xl md:text-4xl font-bold text-white">
              <a href="/" className="flex items-center">
                <span 
                  className="px-3 py-1 rounded"
                  style={{ 
                    backgroundColor: config.logo?.backgroundColor || '#FFFFFF',
                    color: config.logo?.textColor || config.colors.primary
                  }}
                >
                  {config.logo?.text || config.siteName}
                </span>
              </a>
            </h1>
            <p className="ml-4 text-white text-sm md:text-base hidden md:block">
              {config.tagline}
            </p>
          </div>
        </div>
      </div>
      
      <nav className="bg-white border-b border-gray-200">
        <div className="max-w-container mx-auto px-4">
          <div className="flex items-center justify-between h-14">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="md:hidden p-2"
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            
            <div className="hidden md:flex items-center space-x-6">
              {config.navigation.showHome && (
                <a href="/" className="text-text-dark hover:text-neon-pink font-medium">HOME</a>
              )}
              {config.navigation.showDeals && (
                <a href="/deals" className="text-text-dark hover:text-neon-pink">CONTENT</a>
              )}
              {config.navigation.showCoupons && (
                <a href="/coupons" className="text-text-dark hover:text-neon-pink">COUPONS</a>
              )}
              {config.navigation.showAmazon && (
                <a href="/amazon" className="text-text-dark hover:text-neon-pink">AMAZON</a>
              )}
              {config.navigation.showAbout && (
                <a href="/about" className="text-text-dark hover:text-neon-pink">ABOUT</a>
              )}
              {config.navigation.customLinks?.map((link, index) => (
                <a 
                  key={index}
                  href={link.href}
                  className="text-text-dark hover:text-neon-pink"
                  target={link.external ? '_blank' : undefined}
                  rel={link.external ? 'noopener noreferrer' : undefined}
                >
                  {link.label.toUpperCase()}
                </a>
              ))}
            </div>
            
            <form onSubmit={handleSearchSubmit} className="flex items-center">
              <input
                type="search"
                placeholder={config.content.searchPlaceholder}
                value={searchQuery}
                onChange={handleSearchChange}
                className="border border-gray-300 rounded px-3 py-1.5 text-sm w-32 md:w-48 focus:outline-none focus:border-neon-pink"
              />
              <button type="submit" className="ml-2 p-1.5">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </form>
          </div>
          
          {mobileMenuOpen && (
            <div className="md:hidden py-3 border-t">
              {config.navigation.showHome && (
                <a href="/" className="block py-2 text-text-dark hover:text-neon-pink font-medium">HOME</a>
              )}
              {config.navigation.showDeals && (
                <a href="/deals" className="block py-2 text-text-dark hover:text-neon-pink">CONTENT</a>
              )}
              {config.navigation.showCoupons && (
                <a href="/coupons" className="block py-2 text-text-dark hover:text-neon-pink">COUPONS</a>
              )}
              {config.navigation.showAmazon && (
                <a href="/amazon" className="block py-2 text-text-dark hover:text-neon-pink">AMAZON</a>
              )}
              {config.navigation.showAbout && (
                <a href="/about" className="block py-2 text-text-dark hover:text-neon-pink">ABOUT</a>
              )}
              {config.navigation.customLinks?.map((link, index) => (
                <a 
                  key={index}
                  href={link.href}
                  className="block py-2 text-text-dark hover:text-neon-pink"
                  target={link.external ? '_blank' : undefined}
                  rel={link.external ? 'noopener noreferrer' : undefined}
                >
                  {link.label.toUpperCase()}
                </a>
              ))}
            </div>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;