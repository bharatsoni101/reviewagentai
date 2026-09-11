import type { SocialLink } from '../types/api'

const labels: Record<string, string> = {
  FACEBOOK: 'Facebook',
  INSTAGRAM: 'Instagram',
  LINKEDIN: 'LinkedIn',
  X: 'X',
  TWITTER: 'Twitter',
  YOUTUBE: 'YouTube',
  WEBSITE: 'Website',
}

export function SocialLinks({ links, onClick }: { links: SocialLink[]; onClick: (link: SocialLink) => void }) {
  const enabled = links.filter((link) => link.enabled).sort((a, b) => a.display_order - b.display_order)
  if (!enabled.length) return null

  return (
    <section className="mt-8 border-t border-slate-200 pt-7" aria-label="Social links">
      <h2 className="text-sm font-semibold text-slate-950">Connect with us</h2>
      <div className="mt-3 flex flex-wrap gap-2">
        {enabled.map((link) => (
          <a
            key={link.id}
            href={link.url}
            target="_blank"
            rel="noreferrer"
            onClick={() => onClick(link)}
            className="rounded-full border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:border-slate-300 hover:bg-slate-50 focus:outline-none focus:ring-4 focus:ring-slate-100"
          >
            {labels[link.platform.toUpperCase()] || link.platform}
          </a>
        ))}
      </div>
    </section>
  )
}
