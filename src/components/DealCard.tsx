import React from 'react';
import { Deal } from '../types/Deal';
import { getPriceDisplay } from '../utils/dealUtils';
import { getPriceVisibility } from '../utils/priceVisibility';

interface DealCardProps {
  deal: Deal;
  onClick: () => void;
  variant?: 'default' | 'featured';
  colorIndex?: number;
}

const DealCard: React.FC<DealCardProps> = ({ deal, onClick, variant = 'default', colorIndex = 0 }) => {
  const bgColors = ['bg-card-pink', 'bg-card-blue', 'bg-card-yellow'];
  const bgColor = bgColors[colorIndex % bgColors.length];
  
  const isLarge = variant === 'featured';
  const priceDisplay = getPriceDisplay(deal.originalPrice, deal.price, deal.discountPercent);
  const priceVisibility = getPriceVisibility(deal.id);
  
  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement>) => {
    if (process.env.NODE_ENV === 'development') {
      console.warn('Image failed to load:', deal.imageUrl);
    }
    e.currentTarget.src = '/placeholder-deal.svg';
  };
  
  return (
    <div 
      className={`${bgColor} rounded-lg overflow-hidden cursor-pointer transform transition-transform hover:scale-105 ${
        isLarge ? 'h-96' : 'h-80'
      }`}
      onClick={onClick}
    >
      <div className="relative h-full flex flex-col">
        {priceDisplay.badge && priceDisplay.badge.primary && (
          <div className="absolute top-2 left-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold z-10 shadow-md">
            {priceDisplay.badge.primary}
          </div>
        )}
        
        
        <div className={`relative ${isLarge ? 'h-64' : 'h-48'} overflow-hidden`}>
          <img 
            src={deal.imageUrl} 
            alt={deal.title}
            className="w-full h-full object-contain p-4"
            onError={handleImageError}
            loading="lazy"
            referrerPolicy="no-referrer"
          />
        </div>
        
        <div className="flex-1 p-4 bg-white/90 flex flex-col justify-between">
          <h3 className={`font-semibold text-text-dark ${isLarge ? 'text-lg' : 'text-base'} line-clamp-2 mb-2`}>
            {deal.title}
          </h3>
          
          <div className="flex items-end justify-between">
            {priceVisibility.showPrice ? (
              // Show price for ~10% of deals
              <>
                <div>
                  <div className="flex items-baseline gap-2">
                    <p className="text-2xl font-bold text-primary-green">{priceDisplay.current}</p>
                    {priceDisplay.original && (
                      <p className="text-sm text-gray-500 line-through">{priceDisplay.original}</p>
                    )}
                  </div>
                </div>
                <button 
                  onClick={(e) => {
                    e.stopPropagation();
                    window.open(deal.affiliateUrl, '_blank');
                  }}
                  className="bg-primary-green text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-green-700 transition-colors shadow-sm"
                >
                  Shop Now
                </button>
              </>
            ) : (
              // Show "Check Price" button for ~80% of deals (badge already shown at top)
              <div className="w-full">
                <div className="text-center mb-3">
                  <p className="text-sm text-text-dark leading-tight">{deal.description}</p>
                </div>
                <a
                  href={deal.affiliateUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="block w-full bg-gradient-to-r from-primary-green to-green-600 text-white py-3 px-4 rounded-lg text-center font-bold hover:from-green-600 hover:to-green-700 transition-all transform hover:scale-105 shadow-lg"
                >
                  {priceVisibility.checkPriceMessage}
                </a>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DealCard;