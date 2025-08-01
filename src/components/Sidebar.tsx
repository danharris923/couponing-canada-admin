import React from 'react';
import { Deal } from '../types/Deal';
import { getPriceDisplay } from '../utils/dealUtils';
import { getPriceVisibility } from '../utils/priceVisibility';

interface SidebarProps {
  topDeals: Deal[];
  onDealClick: (deal: Deal) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ topDeals, onDealClick }) => {
  return (
    <aside className="w-full lg:w-80">
      <div className="bg-white rounded-lg shadow-sm p-4">
        <div className="flex items-center mb-4">
          <div className="bg-accent-yellow px-3 py-1 rounded flex items-center">
            <svg className="w-5 h-5 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
            </svg>
            <span className="font-bold text-text-dark">TOP DEALS</span>
          </div>
        </div>
        
        <div className="space-y-4">
          {topDeals.map((deal, index) => {
            const priceDisplay = getPriceDisplay(deal.originalPrice, deal.price, deal.discountPercent);
            const priceVisibility = getPriceVisibility(deal.id);
            return (
              <div
                key={deal.id}
                onClick={() => onDealClick(deal)}
                className="cursor-pointer group"
              >
                <div className="flex gap-3 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                  <div className="w-20 h-20 flex-shrink-0 bg-gray-100 rounded overflow-hidden">
                    <img 
                      src={deal.imageUrl} 
                      alt={deal.title}
                      className="w-full h-full object-contain p-1"
                      onError={(e) => {
                        e.currentTarget.src = '/placeholder-deal.svg';
                      }}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-sm text-text-dark line-clamp-2 group-hover:text-primary-green">
                      {deal.title}
                    </h4>
                    {priceVisibility.showPrice ? (
                      <div className="mt-1">
                        <div className="flex items-baseline gap-2">
                          <span className="text-lg font-bold text-primary-green">{priceDisplay.current}</span>
                          {priceDisplay.original && (
                            <span className="text-xs text-gray-500 line-through">{priceDisplay.original}</span>
                          )}
                        </div>
                      </div>
                    ) : (
                      <div className="mt-1">
                        <span className="text-xs text-primary-green font-bold bg-accent-yellow px-2 py-1 rounded">
                          {priceVisibility.checkPriceMessage}
                        </span>
                      </div>
                    )}
                    {priceDisplay.badge && priceDisplay.badge.primary && (
                      <span className="inline-block mt-1 text-xs bg-red-500 text-white px-2 py-0.5 rounded">
                        {priceDisplay.badge.primary}
                      </span>
                    )}
                  </div>
                </div>
                {index < topDeals.length - 1 && <hr className="mt-2" />}
              </div>
            );
          })}
        </div>
        
        <div className="mt-6 pt-4 border-t">
          <h3 className="font-semibold text-text-dark mb-3">Latest News</h3>
          <div className="space-y-3 text-sm">
            <a href="https://amzn.to/3IWEXO0" className="block hover:text-primary-green">
              <p className="font-medium line-clamp-2">New Amazon Prime Day Deals Coming Soon</p>
              <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
            </a>
            <a href="https://amzn.to/41gQZYM" className="block hover:text-primary-green">
              <p className="font-medium line-clamp-2">Best Back-to-School Savings This Week</p>
              <p className="text-xs text-gray-500 mt-1">5 hours ago</p>
            </a>
            <a href="https://amzn.to/4mlLZds" className="block hover:text-primary-green">
              <p className="font-medium line-clamp-2">Flash Sale: 50% Off Electronics Today Only</p>
              <p className="text-xs text-gray-500 mt-1">1 day ago</p>
            </a>
          </div>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;