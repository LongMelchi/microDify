/**
 * Common shared types — aligned with ``app/core/schemas.py``.
 */

/** Paginated response from the backend ``PageResult<T>``. */
export interface PaginatedResponse<T> {
  code: number;
  message: string;
  data: T[];
  total: number;
  page: number;
  size: number;
}
