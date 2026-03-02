import { useState } from 'react'
import { Rocket, Key, X } from 'lucide-react'
import { setApiKey } from '../api/client'

export function DemoBanner() {
  const [showKeyInput, setShowKeyInput] = useState(false)
  const [key, setKey] = useState('')

  function handleConnect(e: React.FormEvent) {
    e.preventDefault()
    if (key.trim()) setApiKey(key.trim())
  }

  return (
    <div className="bg-gradient-to-r from-red-950/80 via-red-900/60 to-red-950/80 border-b border-red-800/50">
      <div className="flex items-center justify-between px-6 py-2.5">
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 bg-red-500/20 text-red-400 text-xs font-semibold px-2 py-0.5 rounded-full uppercase tracking-wider">
            <span className="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse" />
            Demo
          </div>
          <span className="text-sm text-gray-300">
            You're viewing sample data.
          </span>
        </div>

        <div className="flex items-center gap-3">
          {showKeyInput ? (
            <form onSubmit={handleConnect} className="flex items-center gap-2">
              <input
                type="password"
                value={key}
                onChange={e => setKey(e.target.value)}
                placeholder="bwk_..."
                autoFocus
                className="px-3 py-1 bg-gray-900 border border-gray-700 rounded text-xs text-gray-200 placeholder-gray-600 focus:outline-none focus:border-red-500 font-mono w-48"
              />
              <button
                type="submit"
                disabled={!key.trim()}
                className="px-3 py-1 bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-xs text-gray-200 rounded transition-colors"
              >
                Connect
              </button>
              <button
                type="button"
                onClick={() => setShowKeyInput(false)}
                className="p-1 text-gray-500 hover:text-gray-300"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </form>
          ) : (
            <>
              <button
                onClick={() => setShowKeyInput(true)}
                className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-gray-200 transition-colors"
              >
                <Key className="w-3 h-3" />
                Have an API key?
              </button>
              <a
                href="https://bulwark.live"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 bg-red-600 hover:bg-red-500 text-white text-xs font-medium rounded-lg transition-colors"
              >
                <Rocket className="w-3.5 h-3.5" />
                Request Early Access
              </a>
            </>
          )}
        </div>
      </div>
    </div>
  )
}
