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

const initials: Record<string, string> = {
  FACEBOOK: 'f',
  INSTAGRAM: '◎',
  LINKEDIN: 'in',
  X: '𝕏',
  TWITTER: 't',
  YOUTUBE: '▶',
  WEBSITE: '↗',
}

export function SocialLinks({ links, onClick }: { links: SocialLink[]; onClick: (link: SocialLink) => void }) {
  const enabled = links.filter((link) => link.enabled).sort((a, b) => a.display_order - b.display_order)
  if (!enabled.length) return null

  return (
    <section className="mt-8 border-t border-slate-100 pt-7" aria-label="Social links">
      <div className="text-center">
        <p className="ra-eyebrow">Stay connected</p>
        <h2 className="mt-1 text-sm font-bold text-slate-950">Connect with us</h2>
      </div>
      <div className="mt-4 flex flex-wrap justify-center gap-2.5">
        {enabled.map((link) => {
          const platform = link.platform.toUpperCase()
          return (
            <a
              key={link.id}
              href={link.url}
              target="_blank"
              rel="noreferrer"
              onClick={() => onClick(link)}
              className="ra-button ra-button-secondary min-h-11 px-4"
            >
              <span className="flex h-6 min-w-6 items-center justify-center rounded-full bg-indigo-50 px-1.5 text-xs font-black text-indigo-600" aria-hidden="true">
                {initials[platform] || '↗'}
              </span>
              {labels[platform] || link.platform}
            </a>
          )
        })}
      </div>
    </section>
  )
}
