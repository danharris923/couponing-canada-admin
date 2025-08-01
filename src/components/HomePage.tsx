import React, { useState, useEffect } from 'react';
import { AnimatePresence } from 'framer-motion';
import DealCard from './DealCard';
import DealModal from './DealModal';
import BottomSheet from './BottomSheet';
import Sidebar from './Sidebar';
import { Deal } from '../types/Deal';
import { useIsMobile } from '../utils/useIsMobile';
import { useConfig } from '../hooks/useConfig';

interface HomePageProps {
  onSearch?: (query: string) => void;
  searchQuery?: string;
}

const HomePage: React.FC<HomePageProps> = ({ searchQuery: propSearchQuery = '' }) => {
  const { config } = useConfig();
  const [deals, setDeals] = useState<Deal[]>([]);
  const [selectedDeal, setSelectedDeal] = useState<Deal | null>(null);
  const [modalOpen, setModalOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState(propSearchQuery);
  const isMobile = useIsMobile();

  useEffect(() => {
    setSearchQuery(propSearchQuery);
  }, [propSearchQuery]);

  useEffect(() => {
    fetch(config.content.dataFile)
      .then(res => res.json())
      .then(data => {
        setDeals(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading content:', err);
        setLoading(false);
      });
  }, [config.content.dataFile]);

  const handleDealClick = (deal: Deal) => {
    setSelectedDeal(deal);
    setModalOpen(true);
  };

  const handleCloseModal = () => {
    setModalOpen(false);
    setTimeout(() => setSelectedDeal(null), 300);
  };

  // Note: handleSearch is used for potential future functionality
  // const handleSearch = (query: string) => {
  //   setSearchQuery(query);
  // };

  const filteredDeals = deals.filter(deal => 
    deal.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const topDeals = filteredDeals
    .filter(deal => deal.featured)
    .sort((a, b) => b.discountPercent - a.discountPercent)
    .slice(0, config.content.featuredItemsCount);

  const mainDeals = filteredDeals.sort((a, b) => 
    new Date(b.dateAdded).getTime() - new Date(a.dateAdded).getTime()
  );

  return (
    <>
      <main className="max-w-container mx-auto px-4 py-6">
        <div className="flex flex-col lg:flex-row gap-6">
          <div className="flex-1">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-text-dark mb-1">
                {searchQuery ? `Search Results for "${searchQuery}"` : 'Latest Content'}
              </h2>
              <p className="text-gray-600">
                {searchQuery 
                  ? `Found ${mainDeals.length} items matching your search`
                  : 'Discover curated content powered by AI enhancement'
                }
              </p>
            </div>
            
            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {[...Array(6)].map((_, i) => (
                  <div key={i} className="h-80 bg-gray-200 rounded-lg animate-pulse" />
                ))}
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {mainDeals.map((deal, index) => (
                  <DealCard
                    key={deal.id}
                    deal={deal}
                    onClick={() => handleDealClick(deal)}
                    colorIndex={index}
                  />
                ))}
              </div>
            )}
          </div>
          
          {config.content.showFeaturedSidebar && (
            <Sidebar 
              topDeals={topDeals}
              onDealClick={handleDealClick}
            />
          )}
        </div>
      </main>
      
      {/* Desktop: Modal, Mobile: Bottom Sheet */}
      <AnimatePresence exitBeforeEnter>
        {modalOpen && (
          isMobile ? (
            <BottomSheet
              key="bottom-sheet"
              deal={selectedDeal}
              isOpen={modalOpen}
              onClose={handleCloseModal}
            />
          ) : (
            <DealModal
              key="desktop-modal"
              deal={selectedDeal}
              isOpen={modalOpen}
              onClose={handleCloseModal}
            />
          )
        )}
      </AnimatePresence>
    </>
  );
};

export default HomePage;