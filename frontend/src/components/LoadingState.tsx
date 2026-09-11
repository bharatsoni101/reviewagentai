export function LoadingState({ label = 'Loading your experience…' }: { label?: string }) {
  return (
    <div className="flex min-h-[260px] items-center justify-center" role="status" aria-live="polite">
      <div className="flex items-center gap-3 text-slate-600">
        <span className="h-5 w-5 animate-spin rounded-full border-2 border-slate-300 border-t-slate-900" />
        <span>{label}</span>
      </div>
    </div>
  )
}
