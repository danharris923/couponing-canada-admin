import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from './components/ConfigProvider';
import { useConfig } from './hooks/useConfig';
import Header from './components/Header';
import HomePage from './components/HomePage';
import AboutPage from './components/AboutPage';
import CouponsPage from './components/CouponsPage';

function App() {
  return (
    <ConfigProvider>
      <AppContent />
    </ConfigProvider>
  );
}

function AppContent() {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  return (
    <Router>
      <AppRoutes searchQuery={searchQuery} onSearch={handleSearch} />
    </Router>
  );
}

interface AppRoutesProps {
  searchQuery: string;
  onSearch: (query: string) => void;
}

function AppRoutes({ searchQuery, onSearch }: AppRoutesProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header onSearch={onSearch} />
      
      <Routes>
        <Route path="/" element={<HomePage searchQuery={searchQuery} />} />
        <Route path="/deals" element={<HomePage searchQuery={searchQuery} />} />
        <Route path="/about" element={<AboutPage />} />
        <Route path="/coupons" element={<CouponsPage />} />
        <Route path="/amazon" element={<HomePage searchQuery={searchQuery} />} />
        <Route path="/categories" element={<HomePage searchQuery={searchQuery} />} />
      </Routes>
      
      <AppFooter />
    </div>
  );
}

function AppFooter() {
  const { config } = useConfig();
  
  return (
    <footer className="bg-white border-t mt-12">
      <div className="max-w-container mx-auto px-4 py-8">
        <div className="text-center">
          <h3 className="text-xl font-bold text-text-dark mb-2">{config.footer.companyName}</h3>
          <p className="text-gray-600 mb-4">
            {config.footer.tagline}
          </p>
          <p className="text-sm text-gray-500">
            {config.footer.copyright}
          </p>
        </div>
      </div>
    </footer>
  );
}

export default App;
// Force rebuild: 2025-07-31 17:50