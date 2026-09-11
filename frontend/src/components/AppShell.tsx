import type { ReactNode } from 'react'

export function AppShell({ children, businessName }: { children: ReactNode; businessName?: string }) {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-950">
      <header className="border-b border-slate-200 bg-white/95 backdrop-blur">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4 sm:px-6">
          <div>
            <p className="text-lg font-extrabold tracking-tight">reviewagentai</p>
            <p className="text-xs text-slate-500">Customer review experience</p>
          </div>
          {businessName && <span className="max-w-[45%] truncate text-right text-sm font-medium text-slate-600">{businessName}</span>}
        </div>
      </header>
      <main className="mx-auto max-w-3xl px-4 py-6 sm:px-6 sm:py-10">{children}</main>
      <footer className="mx-auto max-w-3xl px-4 pb-8 text-center text-xs text-slate-400 sm:px-6">
        Your feedback helps businesses improve.
      </footer>
    </div>
  )
}
