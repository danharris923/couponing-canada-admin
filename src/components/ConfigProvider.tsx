import React, { ReactNode } from 'react';
import { ConfigContext, useConfigLoader } from '../hooks/useConfig';

interface ConfigProviderProps {
  children: ReactNode;
}

/**
 * ConfigProvider component that loads and provides site configuration to all child components.
 * This enables the entire app to be customizable via the public/config.json file.
 */
export const ConfigProvider: React.FC<ConfigProviderProps> = ({ children }) => {
  const { config, loading, error } = useConfigLoader();
  
  // Show loading state while configuration is being loaded
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading configuration...</p>
        </div>
      </div>
    );
  }
  
  // Show error state if configuration failed to load (but still provide defaults)
  if (error) {
    console.warn('Configuration error:', error);
    // Continue with default config rather than blocking the app
  }
  
  return (
    <ConfigContext.Provider value={{ config, loading, error }}>
      {children}
    </ConfigContext.Provider>
  );
};