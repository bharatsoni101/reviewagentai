import type { ReactNode } from 'react'

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white/95">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-5 py-4 sm:px-6">
          <div>
            <p className="text-lg font-bold tracking-tight">reviewagentai</p>
            <p className="text-xs text-slate-500">Customer review experience</p>
          </div>
          <span className="rounded-full bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
            Secure experience
          </span>
        </div>
      </header>
      {children}
    </div>
  )
}
