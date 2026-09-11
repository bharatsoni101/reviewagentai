type Props = { value: number | null; onChange: (rating: number) => void; disabled?: boolean }

export function RatingStars({ value, onChange, disabled }: Props) {
  return (
    <div className="flex justify-center gap-1 sm:gap-2" role="radiogroup" aria-label="Choose a rating from 1 to 5">
      {[1, 2, 3, 4, 5].map((rating) => {
        const active = value !== null && rating <= value
        return (
          <button
            key={rating}
            type="button"
            disabled={disabled}
            role="radio"
            aria-checked={value === rating}
            aria-label={`${rating} out of 5 stars`}
            onClick={() => onChange(rating)}
            className={`rounded-2xl p-2 text-4xl leading-none transition hover:scale-105 focus:outline-none focus:ring-4 focus:ring-slate-200 disabled:cursor-not-allowed sm:text-5xl ${active ? 'text-amber-400' : 'text-slate-300'}`}
          >
            ★
          </button>
        )
      })}
    </div>
  )
}
