export type SocialLink = {
  id: number
  platform: string
  url: string
  display_order: number
  enabled: boolean
}

export type Business = {
  id: number
  slug: string
  name: string
  logo_url: string | null
  description: string | null
  category: string | null
  google_review_pc_url: string
  google_review_mob_url: string
  status: string
  prefer_ai_comments: boolean
  created_at: string
  updated_at: string
  social_links: SocialLink[]
}

export type CustomerAccessResponse = {
  session_id: string
  business_id: string
  business_slug: string
  business_name: string
  source: string
  status: string
  created_at: string
}

export type ApiError = {
  detail?: string
  code?: string
}
