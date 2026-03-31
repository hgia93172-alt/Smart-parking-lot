import type { ArticleCategoryItem, ArticleCommentItem, ArticleItem, ArticleStatus, OperationLogItem, UserFileItem } from "@/types/utils"
import { downloadBlob, requestR, requestRForm } from "@/api/http"
import type { Paged } from "@/types/api"

export async function uploadUserFile(file: File): Promise<UserFileItem> {
  const fd = new FormData()
  fd.append("file", file)
  return requestRForm<UserFileItem>("/api/utils/files/upload/", "POST", fd)
}

export async function listUserFiles(): Promise<UserFileItem[]> {
  return requestR<UserFileItem[]>("/api/utils/files/list/", { method: "GET" })
}

export async function listUserFilesPaged(page: number, pageSize: number): Promise<Paged<UserFileItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString()
  return requestR<Paged<UserFileItem>>(`/api/utils/files/list/?${qs}`, { method: "GET" })
}

export async function deleteUserFile(fileId: number): Promise<null> {
  return requestR<null>(`/api/utils/files/${fileId}/`, { method: "DELETE" })
}

export async function downloadUserFile(fileId: number): Promise<{ blob: Blob; filename: string }> {
  return downloadBlob(`/api/utils/files/${fileId}/download/`)
}

export async function listAdminFiles(): Promise<UserFileItem[]> {
  return requestR<UserFileItem[]>("/api/utils/admin/files/list/", { method: "GET" })
}

export async function listAdminFilesPaged(page: number, pageSize: number): Promise<Paged<UserFileItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString()
  return requestR<Paged<UserFileItem>>(`/api/utils/admin/files/list/?${qs}`, { method: "GET" })
}

export async function deleteAdminFile(fileId: number): Promise<null> {
  return requestR<null>(`/api/utils/admin/files/${fileId}/`, { method: "DELETE" })
}

export async function listAdminLogsPaged(page: number, pageSize: number): Promise<Paged<OperationLogItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString()
  return requestR<Paged<OperationLogItem>>(`/api/utils/admin/logs/list/?${qs}`, { method: "GET" })
}

export async function deleteAdminLog(logId: number): Promise<null> {
  return requestR<null>(`/api/utils/admin/logs/${logId}/`, { method: "DELETE" })
}

/**
 * 清空所有操作日志（后端会保留本次清空操作产生的新日志记录）。
 */
export async function clearAdminLogs(): Promise<{ deleted: number }> {
  return requestR<{ deleted: number }>("/api/utils/admin/logs/clear/", { method: "DELETE" })
}

/**
 * 管理端：分页查询文章分类。
 */
export async function listAdminArticleCategoriesPaged(page: number, pageSize: number, keyword?: string): Promise<Paged<ArticleCategoryItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
  if (keyword) qs.set("keyword", keyword)
  return requestR<Paged<ArticleCategoryItem>>(`/api/utils/admin/article-categories/list/?${qs.toString()}`, { method: "GET" })
}

/**
 * 管理端：创建文章分类。
 */
export async function createAdminArticleCategory(payload: Partial<ArticleCategoryItem>): Promise<ArticleCategoryItem> {
  return requestR<ArticleCategoryItem>("/api/utils/admin/article-categories/list/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
}

/**
 * 管理端：更新文章分类（PATCH）。
 */
export async function patchAdminArticleCategory(categoryId: number, payload: Partial<ArticleCategoryItem>): Promise<ArticleCategoryItem> {
  return requestR<ArticleCategoryItem>(`/api/utils/admin/article-categories/${categoryId}/`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
}

/**
 * 管理端：删除文章分类。
 */
export async function deleteAdminArticleCategory(categoryId: number): Promise<null> {
  return requestR<null>(`/api/utils/admin/article-categories/${categoryId}/`, { method: "DELETE" })
}

/**
 * 管理端：分页查询文章列表。
 */
export async function listAdminArticlesPaged(
  page: number,
  pageSize: number,
  opts?: { keyword?: string; category_id?: number | null; status?: ArticleStatus | "" }
): Promise<Paged<ArticleItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
  if (opts?.keyword) qs.set("keyword", opts.keyword)
  if (opts?.category_id) qs.set("category_id", String(opts.category_id))
  if (opts?.status) qs.set("status", opts.status)
  return requestR<Paged<ArticleItem>>(`/api/utils/admin/articles/list/?${qs.toString()}`, { method: "GET" })
}

/**
 * 管理端：创建文章（multipart，支持封面上传）。
 */
export async function createAdminArticle(form: {
  title: string
  summary?: string
  content?: string
  status?: ArticleStatus
  category_id?: number | null
  cover?: File | null
}): Promise<ArticleItem> {
  const fd = new FormData()
  fd.append("title", form.title)
  if (form.summary !== undefined) fd.append("summary", form.summary)
  if (form.content !== undefined) fd.append("content", form.content)
  if (form.status) fd.append("status", form.status)
  if (form.category_id !== undefined) {
    if (form.category_id === null) fd.append("category_id", "0")
    else fd.append("category_id", String(form.category_id))
  }
  if (form.cover) fd.append("cover", form.cover)
  return requestRForm<ArticleItem>("/api/utils/admin/articles/list/", "POST", fd)
}

/**
 * 管理端：更新文章（multipart，支持封面上传）。
 */
export async function patchAdminArticle(
  articleId: number,
  form: {
    title?: string
    summary?: string
    content?: string
    status?: ArticleStatus
    category_id?: number | null
    cover?: File | null
    remove_cover?: boolean
  }
): Promise<ArticleItem> {
  const fd = new FormData()
  if (form.title !== undefined) fd.append("title", form.title)
  if (form.summary !== undefined) fd.append("summary", form.summary)
  if (form.content !== undefined) fd.append("content", form.content)
  if (form.status !== undefined) fd.append("status", form.status)
  if (form.category_id !== undefined) {
    if (form.category_id === null) fd.append("category_id", "0")
    else fd.append("category_id", String(form.category_id))
  }
  if (form.remove_cover) fd.append("remove_cover", "1")
  if (form.cover) fd.append("cover", form.cover)
  return requestRForm<ArticleItem>(`/api/utils/admin/articles/${articleId}/`, "PATCH", fd)
}

/**
 * 管理端：删除文章。
 */
export async function deleteAdminArticle(articleId: number): Promise<null> {
  return requestR<null>(`/api/utils/admin/articles/${articleId}/`, { method: "DELETE" })
}

/**
 * 用户端：分页查询已发布文章列表。
 */
export async function listPublicArticlesPaged(page: number, pageSize: number, opts?: { keyword?: string; category_id?: number | null }): Promise<Paged<ArticleItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) })
  if (opts?.keyword) qs.set("keyword", opts.keyword)
  if (opts?.category_id) qs.set("category_id", String(opts.category_id))
  return requestR<Paged<ArticleItem>>(`/api/utils/articles/list/?${qs.toString()}`, { method: "GET" })
}

/**
 * 用户端：查询启用的文章分类列表。
 */
export async function listPublicArticleCategories(): Promise<ArticleCategoryItem[]> {
  return requestR<ArticleCategoryItem[]>("/api/utils/articles/categories/list/", { method: "GET" })
}

/**
 * 用户端：获取文章详情（会触发浏览数 +1）。
 */
export async function getPublicArticleDetail(articleId: number): Promise<ArticleItem> {
  return requestR<ArticleItem>(`/api/utils/articles/${articleId}/`, { method: "GET" })
}

/**
 * 用户端：分页查询文章评论。
 */
export async function listArticleCommentsPaged(articleId: number, page: number, pageSize: number): Promise<Paged<ArticleCommentItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString()
  return requestR<Paged<ArticleCommentItem>>(`/api/utils/articles/${articleId}/comments/?${qs}`, { method: "GET" })
}

/**
 * 用户端：发表评论。
 */
export async function createArticleComment(articleId: number, payload: { content: string; parent_id?: number | null }): Promise<ArticleCommentItem> {
  return requestR<ArticleCommentItem>(`/api/utils/articles/${articleId}/comments/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  })
}

/**
 * 用户端：点赞/取消点赞。
 */
export async function toggleArticleLike(articleId: number): Promise<{ liked: boolean; like_count: number }> {
  return requestR<{ liked: boolean; like_count: number }>(`/api/utils/articles/${articleId}/like/`, { method: "POST" })
}

/**
 * 用户端：收藏/取消收藏。
 */
export async function toggleArticleFavorite(articleId: number): Promise<{ favorited: boolean; favorite_count: number }> {
  return requestR<{ favorited: boolean; favorite_count: number }>(`/api/utils/articles/${articleId}/favorite/`, { method: "POST" })
}

/**
 * 用户端：分页查询我的收藏文章列表。
 */
export async function listMyFavoriteArticlesPaged(page: number, pageSize: number): Promise<Paged<ArticleItem>> {
  const qs = new URLSearchParams({ page: String(page), page_size: String(pageSize) }).toString()
  return requestR<Paged<ArticleItem>>(`/api/utils/me/favorite-articles/list/?${qs}`, { method: "GET" })
}
