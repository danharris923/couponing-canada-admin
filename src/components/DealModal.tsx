import React from 'react';
import { Deal } from '../types/Deal';
import { getPriceDisplay } from '../utils/dealUtils';
import { getPriceVisibility } from '../utils/priceVisibility';

interface DealModalProps {
  deal: Deal | null;
  isOpen: boolean;
  onClose: () => void;
}

const DealModal: React.FC<DealModalProps> = ({ deal, isOpen, onClose }) => {
  if (!isOpen || !deal) return null;

  const priceDisplay = getPriceDisplay(deal.originalPrice, deal.price, deal.discountPercent);
  const priceVisibility = getPriceVisibility(deal.id);

  return (
    <div 
      className="fixed inset-0 bg-black/60 z-50 flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div 
        className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative">
          <button
            onClick={onClose}
            className="absolute top-4 right-4 w-8 h-8 flex items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200"
            aria-label="Close modal"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
          
          <div className="p-6">
            <div className="flex flex-col md:flex-row gap-6">
              <div className="md:w-1/2">
                <div className="bg-gray-100 rounded-lg p-4">
                  <img 
                    src={deal.imageUrl} 
                    alt={deal.title}
                    className="w-full h-64 object-contain"
                    onError={(e) => {
                      if (process.env.NODE_ENV === 'development') {
                        console.warn('Modal image failed to load:', deal.imageUrl);
                      }
                      e.currentTarget.src = '/placeholder-deal.svg';
                    }}
                    loading="lazy"
                    referrerPolicy="no-referrer"
                  />
                </div>
                {priceDisplay.badge && priceDisplay.badge.primary && (
                  <div className="mt-4 bg-red-500 text-white px-4 py-2 rounded-full text-center font-bold text-lg">
                    {priceDisplay.badge.primary}
                  </div>
                )}
              </div>
              
              <div className="md:w-1/2">
                <div className="mb-2 text-sm text-gray-600">{deal.category}</div>
                <h2 className="text-2xl font-bold text-text-dark mb-4">{deal.title}</h2>
                
                {priceVisibility.showPrice ? (
                  <div className="mb-6">
                    <div className="flex items-baseline gap-3">
                      <p className="text-3xl font-bold text-primary-green">{priceDisplay.current}</p>
                      {priceDisplay.original && (
                        <p className="text-xl text-gray-500 line-through">{priceDisplay.original}</p>
                      )}
                    </div>
                  </div>
                ) : (
                  <div className="mb-6 text-center">
                    <p className="text-lg text-text-dark leading-relaxed">{deal.description}</p>
                  </div>
                )}
                
                
                <a
                  href={deal.affiliateUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`block w-full text-white text-center py-4 px-6 rounded-lg font-bold transition-all transform hover:scale-105 shadow-lg ${
                    priceVisibility.showPrice 
                      ? 'bg-primary-green hover:bg-green-700' 
                      : 'bg-gradient-to-r from-primary-green to-green-600 hover:from-green-600 hover:to-green-700'
                  }`}
                >
                  {priceVisibility.showPrice ? 'Shop Now at Amazon' : priceVisibility.checkPriceMessage}
                </a>
                
                <p className="text-xs text-gray-500 mt-4 text-center">
                  *Prices may vary. Deal added on {new Date(deal.dateAdded).toLocaleDateString()}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DealModal;