import type { ReactNode } from 'react'

export function AppShell({ children, businessName }: { children: ReactNode; businessName?: string }) {
  return (
    <div className="min-h-screen overflow-x-hidden bg-slate-50 text-slate-950">
      <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/90 backdrop-blur-xl">
        <div className="mx-auto flex max-w-3xl items-center justify-between px-4 py-4 sm:px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-600 to-blue-600 text-sm font-black text-white shadow-md shadow-indigo-200" aria-hidden="true">
              r
            </div>
            <div>
              <p className="text-lg font-extrabold tracking-tight text-slate-950">reviewagentai</p>
              <p className="text-xs font-medium text-slate-500">Customer review experience</p>
            </div>
          </div>
          {businessName && (
            <span className="max-w-[42%] truncate rounded-full bg-indigo-50 px-3 py-1.5 text-right text-xs font-bold text-indigo-700">
              {businessName}
            </span>
          )}
        </div>
      </header>
      <main className="relative mx-auto max-w-3xl px-4 py-6 sm:px-6 sm:py-10">
        <div className="pointer-events-none absolute -left-24 top-10 h-48 w-48 rounded-full bg-indigo-200/20 blur-3xl" aria-hidden="true" />
        <div className="pointer-events-none absolute -right-24 top-40 h-56 w-56 rounded-full bg-blue-200/20 blur-3xl" aria-hidden="true" />
        <div className="relative">{children}</div>
      </main>
      <footer className="mx-auto max-w-3xl px-4 pb-8 text-center text-xs font-medium text-slate-400 sm:px-6">
        Your feedback helps businesses improve.
      </footer>
    </div>
  )
}
