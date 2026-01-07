import { Link } from 'react-router-dom'

export default function Home() {
  return (
    <div className="-mt-8 -mx-4 sm:-mx-6 lg:-mx-8">
      {/* Hero Section */}
      <div className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23479BE0%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
        <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-primary-500/20 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-primary-400/10 rounded-full blur-3xl translate-y-1/2 -translate-x-1/2"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-sm text-primary-300 mb-6">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Now live on Base Network
              </div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight">
                Earn by Powering
                <span className="block text-primary-400">AI Research</span>
              </h1>
              <p className="mt-6 text-lg text-slate-300 leading-relaxed max-w-xl">
                Join a global network of knowledge workers contributing to AI-assisted academic research. 
                Verify outputs, add expertise, and earn crypto rewards.
              </p>
              <div className="mt-10 flex flex-wrap gap-4">
                <Link 
                  to="/tasks" 
                  className="inline-flex items-center gap-2 px-8 py-4 bg-primary-500 hover:bg-primary-400 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30 hover:-translate-y-0.5"
                >
                  Start Earning
                  <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </Link>
                <Link 
                  to="/tasks" 
                  className="inline-flex items-center gap-2 px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl backdrop-blur-sm transition-all duration-200"
                >
                  Browse Tasks
                </Link>
              </div>
            </div>
            
            <div className="hidden lg:block relative">
              <div className="absolute inset-0 bg-gradient-to-r from-slate-900 via-transparent to-transparent z-10"></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-4">
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/10">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-xl bg-amber-500/20 flex items-center justify-center">
                        <span className="text-xl">⛏️</span>
                      </div>
                      <div>
                        <div className="text-white font-medium">Data Extraction</div>
                        <div className="text-slate-400 text-sm">₦45,000</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-1 bg-blue-500/20 text-blue-300 text-xs rounded-md">Open</span>
                      <span className="text-slate-500 text-xs">2 hours ago</span>
                    </div>
                  </div>
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/10 translate-x-8">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-xl bg-green-500/20 flex items-center justify-center">
                        <span className="text-xl">✅</span>
                      </div>
                      <div>
                        <div className="text-white font-medium">Review Complete</div>
                        <div className="text-green-400 text-sm">+₦22,500 earned</div>
                      </div>
                    </div>
                  </div>
                </div>
                <div className="space-y-4 mt-8">
                  <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-5 border border-white/10">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-xl bg-purple-500/20 flex items-center justify-center">
                        <span className="text-xl">🔍</span>
                      </div>
                      <div>
                        <div className="text-white font-medium">Discovery Task</div>
                        <div className="text-slate-400 text-sm">₦30,000</div>
                      </div>
                    </div>
                    <div className="w-full bg-slate-700 rounded-full h-2">
                      <div className="bg-primary-500 h-2 rounded-full" style={{width: '65%'}}></div>
                    </div>
                    <div className="text-slate-400 text-xs mt-2">65% complete</div>
                  </div>
                  <div className="bg-gradient-to-br from-primary-500/20 to-primary-600/20 backdrop-blur-sm rounded-2xl p-5 border border-primary-500/30">
                    <div className="text-primary-300 text-sm mb-1">Your Balance</div>
                    <div className="text-white text-2xl font-bold">₦127,500</div>
                    <div className="text-green-400 text-sm mt-1">↑ 12% this week</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="bg-white border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900">₦2.5M+</div>
              <div className="text-sm text-gray-500 mt-1">Total Paid Out</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900">150+</div>
              <div className="text-sm text-gray-500 mt-1">Active Workers</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900">89%</div>
              <div className="text-sm text-gray-500 mt-1">Approval Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl sm:text-4xl font-bold text-gray-900">&lt;24h</div>
              <div className="text-sm text-gray-500 mt-1">Avg. Payment Time</div>
            </div>
          </div>
        </div>
      </div>

      {/* How It Works */}
      <div className="bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              How It Works
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Start earning in three simple steps. No experience required.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 relative">
            <div className="hidden md:block absolute top-24 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary-200 via-primary-400 to-primary-200"></div>
            
            <div className="relative bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg hover:border-primary-100 transition-all duration-300">
              <div className="w-14 h-14 bg-primary-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-primary-500/25">
                <span className="text-2xl text-white font-bold">1</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Connect & Browse</h3>
              <p className="text-gray-600 leading-relaxed">
                Connect your wallet and browse available research tasks. Filter by skills, budget, and deadline to find perfect matches.
              </p>
              <div className="mt-6 flex flex-wrap gap-2">
                <span className="px-3 py-1 bg-slate-100 text-slate-600 text-sm rounded-full">Data Collection</span>
                <span className="px-3 py-1 bg-slate-100 text-slate-600 text-sm rounded-full">Analysis</span>
                <span className="px-3 py-1 bg-slate-100 text-slate-600 text-sm rounded-full">Review</span>
              </div>
            </div>
            
            <div className="relative bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg hover:border-primary-100 transition-all duration-300">
              <div className="w-14 h-14 bg-primary-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-primary-500/25">
                <span className="text-2xl text-white font-bold">2</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Complete Tasks</h3>
              <p className="text-gray-600 leading-relaxed">
                Use AI-powered tools to help with research synthesis. Follow clear guidelines and submit your work for review.
              </p>
              <div className="mt-6 p-4 bg-slate-50 rounded-xl">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-primary-100 flex items-center justify-center">
                    <span className="text-primary-600">🤖</span>
                  </div>
                  <div className="text-sm">
                    <div className="font-medium text-gray-900">AI Assistant</div>
                    <div className="text-gray-500">Powered by Claude</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="relative bg-white rounded-2xl p-8 shadow-sm border border-gray-100 hover:shadow-lg hover:border-primary-100 transition-all duration-300">
              <div className="w-14 h-14 bg-primary-500 rounded-2xl flex items-center justify-center mb-6 shadow-lg shadow-primary-500/25">
                <span className="text-2xl text-white font-bold">3</span>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">Get Paid</h3>
              <p className="text-gray-600 leading-relaxed">
                Once approved, receive instant payment in cNGN to your connected wallet. Build reputation for higher-paying tasks.
              </p>
              <div className="mt-6 flex items-center gap-4">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center text-white text-xs font-bold border-2 border-white">₦</div>
                  <div className="w-8 h-8 rounded-full bg-primary-500 flex items-center justify-center text-white text-xs border-2 border-white">⚡</div>
                </div>
                <span className="text-sm text-gray-600">Instant crypto payments</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Why Choose Flow?
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Built for knowledge workers who want meaningful work with fair compensation.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="group p-6 rounded-2xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/50 transition-all duration-300">
              <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-2xl">💰</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Instant Payments</h3>
              <p className="text-gray-600">Receive cNGN directly to your wallet within minutes of approval. No waiting for bank transfers.</p>
            </div>
            
            <div className="group p-6 rounded-2xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/50 transition-all duration-300">
              <div className="w-12 h-12 bg-purple-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🤖</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">AI-Powered Tools</h3>
              <p className="text-gray-600">Access Claude AI to help discover papers, extract claims, and synthesize research efficiently.</p>
            </div>
            
            <div className="group p-6 rounded-2xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/50 transition-all duration-300">
              <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-2xl">⭐</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Build Reputation</h3>
              <p className="text-gray-600">Complete tasks to increase your reputation tier and unlock higher-paying opportunities.</p>
            </div>
            
            <div className="group p-6 rounded-2xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/50 transition-all duration-300">
              <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-2xl">📈</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Royalty Income</h3>
              <p className="text-gray-600">Earn ongoing royalties from knowledge artifacts you helped create when they're licensed.</p>
            </div>
            
            <div className="group p-6 rounded-2xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/50 transition-all duration-300">
              <div className="w-12 h-12 bg-rose-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🔒</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Secure Escrow</h3>
              <p className="text-gray-600">All task payments are held in smart contract escrow until work is approved. No payment disputes.</p>
            </div>
            
            <div className="group p-6 rounded-2xl border border-gray-200 hover:border-primary-200 hover:bg-primary-50/50 transition-all duration-300">
              <div className="w-12 h-12 bg-teal-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                <span className="text-2xl">🌍</span>
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">Work Anywhere</h3>
              <p className="text-gray-600">All you need is internet access. Work from anywhere in the world on your own schedule.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Task Types */}
      <div className="bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900">
              Types of Tasks
            </h2>
            <p className="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">
              Choose from various task types based on your skills and interests.
            </p>
          </div>
          
          <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-4">
            <div className="bg-white rounded-2xl p-6 text-center border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="w-16 h-16 bg-blue-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔍</span>
              </div>
              <h3 className="font-bold text-gray-900">Discovery</h3>
              <p className="text-sm text-gray-500 mt-2">Find relevant papers and sources</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 text-center border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="w-16 h-16 bg-amber-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⛏️</span>
              </div>
              <h3 className="font-bold text-gray-900">Extraction</h3>
              <p className="text-sm text-gray-500 mt-2">Extract key data and claims</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 text-center border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="w-16 h-16 bg-green-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🗺️</span>
              </div>
              <h3 className="font-bold text-gray-900">Mapping</h3>
              <p className="text-sm text-gray-500 mt-2">Build knowledge graphs</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 text-center border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="w-16 h-16 bg-purple-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔧</span>
              </div>
              <h3 className="font-bold text-gray-900">Assembly</h3>
              <p className="text-sm text-gray-500 mt-2">Compile research artifacts</p>
            </div>
            
            <div className="bg-white rounded-2xl p-6 text-center border border-gray-100 hover:shadow-lg hover:-translate-y-1 transition-all duration-300">
              <div className="w-16 h-16 bg-rose-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">✍️</span>
              </div>
              <h3 className="font-bold text-gray-900">Narrative</h3>
              <p className="text-sm text-gray-500 mt-2">Write synthesis reports</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('data:image/svg+xml,%3Csvg width=%2260%22 height=%2260%22 viewBox=%220 0 60 60%22 xmlns=%22http://www.w3.org/2000/svg%22%3E%3Cg fill=%22none%22 fill-rule=%22evenodd%22%3E%3Cg fill=%22%23479BE0%22 fill-opacity=%220.05%22%3E%3Cpath d=%22M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z%22/%3E%3C/g%3E%3C/g%3E%3C/svg%3E')] opacity-40"></div>
        <div className="absolute top-0 left-1/2 w-[500px] h-[500px] bg-primary-500/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2"></div>
        
        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
          <h2 className="text-3xl sm:text-4xl font-bold text-white mb-6">
            Ready to Start Earning?
          </h2>
          <p className="text-lg text-slate-300 mb-10 max-w-2xl mx-auto">
            Join hundreds of knowledge workers already earning on Flow. Connect your wallet and claim your first task in minutes.
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link 
              to="/tasks" 
              className="inline-flex items-center gap-2 px-8 py-4 bg-primary-500 hover:bg-primary-400 text-white font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-primary-500/25 hover:shadow-xl hover:shadow-primary-500/30"
            >
              View Available Tasks
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </Link>
          </div>
          
          <div className="mt-12 flex flex-wrap justify-center gap-8 text-sm text-slate-400">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              No fees to join
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Instant payouts
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Work from anywhere
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
