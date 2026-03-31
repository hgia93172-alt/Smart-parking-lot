export interface UserFileItem {
  id: number
  original_name: string
  size: number
  content_type: string
  created_at: string
}

export interface OperationLogItem {
  id: number
  operator_username: string | null
  action: string
  remark: string
  path: string
  method: string
  ip: string | null
  status_code: number | null
  response_code: number | null
  success: boolean
  detail: string
  created_at: string
}

export interface ArticleCategoryItem {
  id: number
  name: string
  description: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export type ArticleStatus = "draft" | "published" | "archived"

export interface ArticleItem {
  id: number
  title: string
  summary: string
  content?: string
  status?: ArticleStatus
  published_at: string | null
  view_count: number
  author_id?: number | null
  category_id: number | null
  category_name: string | null
  cover_url: string
  like_count: number
  favorite_count: number
  comment_count: number
  created_at: string
  updated_at: string
  liked?: boolean
  favorited?: boolean
}

export interface ArticleCommentItem {
  id: number
  article_id: number
  user_id: number | null
  username: string | null
  parent_id: number | null
  content: string
  created_at: string
  updated_at: string
}

