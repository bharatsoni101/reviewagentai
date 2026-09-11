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

export type CustomerAccess = {
  session_id: string
  business_id: string
  business_slug: string
  business_name: string
  source: 'nfc' | 'qr' | 'direct'
  status: string
  created_at: string
}

export type RatingResponse = {
  session_id: string
  business_id: string
  rating: number
  status: string
  next_step: string
  updated_at: string
}

export type GeneratedReview = {
  id: number
  generated_review: string
  selected: boolean
  created_at: string
}

export type PositiveReviewResponse = {
  session_id: string
  business_id: number
  rating: number
  generation_source: 'groq' | 'fallback' | string
  selected_preferences: string[]
  customer_comment: string | null
  reviews: GeneratedReview[]
}

export type PrivateFeedbackResponse = {
  session_id: string
  business_id: string
  complaint_id: number
  rating: number
  status: string
  acknowledgement: string
  created_at: string
}

export type GoogleSelectionResponse = {
  session_id: string
  business_id: number
  rating: number
  selected_review_id: number
  review_text: string
  google_review_pc_url: string
  google_review_mob_url: string
  google_review_url: string
  device_type: 'desktop' | 'mobile' | string
  status: string
  updated_at: string
}

export type ReviewFlowResponse = {
  session_id: string
  business_id: string
  business_slug: string
  business_name: string
  status: string
  rating: number | null
  next_step: string
  expires_at: string
  expired: boolean
}

export type ApiError = {
  detail?: string | { msg?: string }[]
  code?: string
}
