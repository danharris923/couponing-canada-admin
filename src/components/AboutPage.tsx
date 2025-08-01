import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-green to-green-600 text-white">
        <div className="max-w-container mx-auto px-4 py-16">
          <div className="text-center">
            <h1 className="text-4xl md:text-6xl font-bold mb-6">
              Canada's #1 Savings Destination
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-green-100">
              Welcome to SavingsGuru.cc - Where Smart Canadians Save Big!
            </p>
            <div className="flex flex-wrap justify-center gap-4 text-sm md:text-base">
              <div className="bg-white/20 px-4 py-2 rounded-full">
                🍁 Proudly Canadian
              </div>
              <div className="bg-white/20 px-4 py-2 rounded-full">
                💰 Millions Saved Daily
              </div>
              <div className="bg-white/20 px-4 py-2 rounded-full">
                ⚡ Real-Time Deal Updates
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        
        {/* Our Story Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            The Ultimate Deal-Finding Experience
          </h2>
          
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                🔥 We're Obsessed with Savings
              </h3>
              <p className="text-gray-700 mb-4 leading-relaxed">
                At SavingsGuru.cc, we're not just another coupon site - we're Canada's most passionate team of deal hunters! 
                Our enthusiastic experts scour the internet 24/7 to bring you the hottest deals, deepest discounts, and 
                exclusive offers you won't find anywhere else.
              </p>
              <p className="text-gray-700 mb-4 leading-relaxed">
                From coast to coast, over <strong>1 million Canadian shoppers</strong> trust us to find them incredible 
                savings every single day. Whether you're shopping for electronics, fashion, home goods, or everyday essentials, 
                we've got the deals that matter most to your wallet.
              </p>
            </div>
            
            <div className="bg-white p-8 rounded-2xl shadow-lg">
              <h4 className="text-xl font-bold text-gray-900 mb-4">Why Canadians Choose Us:</h4>
              <ul className="space-y-3">
                <li className="flex items-center">
                  <span className="text-green-500 mr-3">✅</span>
                  <span>Verified deals updated every hour</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-3">✅</span>
                  <span>Exclusive Canadian retailer partnerships</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-3">✅</span>
                  <span>Price tracking & alerts</span>
                </li>
                <li className="flex items-center">
                  <span className="text-green-500 mr-3">✅</span>
                  <span>Mobile-optimized experience</span>
                </li>
              </ul>
            </div>
          </div>
        </div>

        {/* New Website Features */}
        <div className="mb-16 bg-white p-8 rounded-2xl shadow-lg">
          <h2 className="text-3xl font-bold text-gray-900 mb-6 text-center">
            🚀 Our Brand New Website Experience
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">⚡</span>
              </div>
              <h3 className="text-xl font-bold mb-2">Lightning Fast</h3>
              <p className="text-gray-600">
                Our completely rebuilt platform loads deals instantly, so you never miss out on time-sensitive offers.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-green-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">📱</span>
              </div>
              <h3 className="text-xl font-bold mb-2">Mobile First</h3>
              <p className="text-gray-600">
                Designed for how Canadians actually shop - seamless experience on every device with native app-like feel.
              </p>
            </div>
            
            <div className="text-center">
              <div className="bg-purple-100 w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4">
                <span className="text-2xl">🎯</span>
              </div>
              <h3 className="text-xl font-bold mb-2">Smart Deals</h3>
              <p className="text-gray-600">
                Advanced algorithms ensure you see the best deals first, personalized to your shopping preferences.
              </p>
            </div>
          </div>
        </div>

        {/* What We Do */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            How We Save You Money
          </h2>
          
          <div className="bg-gradient-to-r from-blue-50 to-green-50 p-8 rounded-2xl">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">🕵️ Professional Deal Hunters</h3>
                <p className="text-gray-700 mb-4">
                  Our dedicated team of savings experts work around the clock, monitoring hundreds of Canadian retailers 
                  and international brands to uncover the absolute best deals before anyone else.
                </p>
                <p className="text-gray-700">
                  We don't just post random sales - every deal is hand-picked, verified, and tested to ensure 
                  you're getting genuine value that saves you real money.
                </p>
              </div>
              
              <div>
                <h3 className="text-2xl font-bold text-gray-900 mb-4">🤖 Cutting-Edge Technology</h3>
                <p className="text-gray-700 mb-4">
                  Our proprietary deal-discovery system scans millions of products daily, tracks price histories, 
                  and identifies the perfect moment when items hit their lowest prices.
                </p>
                <p className="text-gray-700">
                  From flash sales to seasonal clearances, we catch deals the moment they go live and get them 
                  to you before they sell out.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">
            The Numbers Don't Lie
          </h2>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-green mb-2">1M+</div>
              <div className="text-gray-600">Happy Canadians</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-green mb-2">$20M+</div>
              <div className="text-gray-600">Total Savings</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-green mb-2">100+</div>
              <div className="text-gray-600">Daily New Deals</div>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-primary-green mb-2">24/7</div>
              <div className="text-gray-600">Deal Monitoring</div>
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-primary-green to-green-600 text-white p-8 rounded-2xl text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Saving?</h2>
          <p className="text-xl mb-6 text-green-100">
            Join millions of smart Canadian shoppers who never pay full price again!
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a 
              href="/deals" 
              className="bg-white text-primary-green px-8 py-3 rounded-full font-bold hover:bg-gray-100 transition-all"
            >
              🔥 Browse Hot Deals
            </a>
            <a 
              href="/coupons" 
              className="bg-green-700 text-white px-8 py-3 rounded-full font-bold hover:bg-green-800 transition-all"
            >
              🎫 Get Exclusive Coupons
            </a>
          </div>
        </div>

        {/* Amazon Disclaimer */}
        <div className="bg-gray-100 p-6 rounded-xl">
          <h3 className="text-lg font-bold text-gray-900 mb-3">📋 Important Disclosure</h3>
          <div className="text-sm text-gray-700 space-y-2">
            <p>
              <strong>Amazon Associate Disclosure:</strong> SavingsGuru.cc is a participant in the Amazon Services LLC Associates Program, 
              an affiliate advertising program designed to provide a means for sites to earn advertising fees by advertising and linking to Amazon.ca and Amazon.com.
            </p>
            <p>
              <strong>Pricing & Availability:</strong> All prices and deals are subject to change without notice. Deals may expire or become unavailable at any time. 
              We make every effort to ensure accuracy, but cannot guarantee all information is current. Always verify pricing on the retailer's website before purchasing.
            </p>
            <p>
              <strong>Third-Party Links:</strong> Our site contains links to external websites. We are not responsible for the content, privacy policies, 
              or practices of these third-party sites. Please review their terms before making purchases.
            </p>
            <p>
              <strong>No Warranties:</strong> While we strive to provide accurate deal information, SavingsGuru.cc makes no warranties about the completeness, 
              reliability, or accuracy of this information. Use of our site is at your own risk.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;