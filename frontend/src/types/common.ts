export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ErrorResponse {
  detail: string;
}

export interface PaginationParams {
  page?: number;
  limit?: number;
}
