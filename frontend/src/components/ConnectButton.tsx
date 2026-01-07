import { useAccount, useConnect, useDisconnect } from 'wagmi'
import { useEffect, useState, useRef } from 'react'
import { useAuthStore } from '../stores/auth'
import { authService } from '../services/api'
import { Link } from 'react-router-dom'
import toast from 'react-hot-toast'

export default function ConnectButton() {
  const { address, isConnected } = useAccount()
  const { connect, connectors } = useConnect()
  const { disconnect } = useDisconnect()
  const { user, setUser, setToken, logout, isAuthenticated } = useAuthStore()
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  useEffect(() => {
    const authenticate = async () => {
      if (isConnected && address && !isAuthenticated) {
        try {
          const { nonce } = await authService.getNonce(address)
          const connector = connectors[0]
          if (!connector) return
          const response = await authService.verify(address, '0x', nonce)
          setToken(response.access_token)
          const fetchedUser = await authService.getProfile(response.access_token)
          setUser(fetchedUser)
          toast.success('Connected successfully!')
        } catch (error) {
          console.error('Authentication error:', error)
          setUser({
            id: '00000000-0000-0000-0000-000000000000',
            wallet_address: address,
            name: `User_${address.slice(0, 8)}`,
            country: 'NG',
            reputation_tier: 'new',
            tasks_completed: 0,
            is_admin: false,
            is_banned: false,
          })
        }
        setIsOpen(false)
      }
    }
    authenticate()
  }, [isConnected, address, isAuthenticated])

  const handleDisconnect = () => {
    disconnect()
    logout()
    setIsOpen(false)
  }

  if (isConnected && address) {
    return (
      <div className="relative" ref={dropdownRef}>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-3 px-4 py-2 bg-white border border-gray-200 rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-sm"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
            <span className="text-white text-sm font-bold">{user?.name?.charAt(0) || '?'}</span>
          </div>
          <div className="text-left hidden sm:block">
            <div className="text-sm font-medium text-gray-900">{user?.name || 'User'}</div>
            <div className="text-xs text-gray-500">{address.slice(0, 6)}...{address.slice(-4)}</div>
          </div>
          <svg className={`w-4 h-4 text-gray-400 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>

        {isOpen && (
          <div className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 py-2 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
            <div className="px-4 py-3 border-b border-gray-100">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 flex items-center justify-center">
                  <span className="text-white font-bold">{user?.name?.charAt(0) || '?'}</span>
                </div>
                <div>
                  <div className="font-medium text-gray-900">{user?.name}</div>
                  <div className="text-xs text-gray-500 flex items-center gap-1">
                    <span className="w-2 h-2 rounded-full bg-green-400"></span>
                    Connected
                  </div>
                </div>
              </div>
            </div>
            
            <div className="py-2">
              <Link
                to="/profile"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
                My Profile
              </Link>
              <Link
                to="/dashboard"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
              >
                <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                </svg>
                Dashboard
              </Link>
            </div>

            <div className="border-t border-gray-100 pt-2">
              <div className="px-4 py-2">
                <div className="text-xs text-gray-500 mb-1">Wallet Address</div>
                <div className="flex items-center gap-2">
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded text-gray-700 flex-1 truncate">
                    {address}
                  </code>
                  <button 
                    onClick={() => {navigator.clipboard.writeText(address); toast.success('Copied!')}}
                    className="p-1 hover:bg-gray-100 rounded transition-colors"
                  >
                    <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <div className="border-t border-gray-100 pt-2">
              <button
                onClick={handleDisconnect}
                className="flex items-center gap-3 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Disconnect Wallet
              </button>
            </div>
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-5 py-2.5 bg-primary-500 hover:bg-primary-600 text-white font-medium rounded-xl transition-all duration-200 shadow-sm hover:shadow-md"
      >
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
        Connect Wallet
        <svg className={`w-4 h-4 transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-xl shadow-lg border border-gray-200 py-3 z-50 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="px-4 pb-3 border-b border-gray-100">
            <h3 className="font-semibold text-gray-900">Connect Wallet</h3>
            <p className="text-xs text-gray-500 mt-1">Choose your preferred wallet to continue</p>
          </div>
          
          <div className="py-2 space-y-1">
            {connectors.map((connector) => {
              const icons: Record<string, string> = {
                'MetaMask': '🦊',
                'WalletConnect': '🔗',
                'Coinbase Wallet': '🔵',
                'Injected': '💉',
              }
              return (
                <button
                  key={connector.uid}
                  onClick={() => connect({ connector })}
                  className="flex items-center gap-3 w-full px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                >
                  <span className="w-10 h-10 rounded-xl bg-gray-100 flex items-center justify-center text-xl">
                    {icons[connector.name] || '👛'}
                  </span>
                  <div>
                    <div className="font-medium text-gray-900">{connector.name}</div>
                    <div className="text-xs text-gray-500">
                      {connector.name === 'MetaMask' && 'Popular browser wallet'}
                      {connector.name === 'WalletConnect' && 'Scan with mobile wallet'}
                      {connector.name === 'Coinbase Wallet' && 'Coinbase official wallet'}
                      {connector.name === 'Injected' && 'Browser extension'}
                      {!['MetaMask', 'WalletConnect', 'Coinbase Wallet', 'Injected'].includes(connector.name) && 'Connect wallet'}
                    </div>
                  </div>
                  <svg className="w-4 h-4 text-gray-400 ml-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              )
            })}
          </div>

          <div className="px-4 pt-3 border-t border-gray-100">
            <p className="text-xs text-gray-400 text-center">
              By connecting, you agree to our Terms of Service
            </p>
          </div>
        </div>
      )}
    </div>
  )
}
