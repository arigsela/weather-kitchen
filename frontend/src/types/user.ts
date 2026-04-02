export interface Family {
  id: string;
  name: string;
  family_size: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface User {
  id: string;
  family_id: string;
  name: string;
  emoji: string | null;
  created_at: string;
  updated_at: string;
}

export interface FamilyCreateRequest {
  name: string;
  family_size: number;
  password: string;
  beta_code?: string;
}

export interface LoginRequest {
  name: string;
  password: string;
  beta_code?: string;
}

export interface FamilyCreateResponse {
  id: string;
  name: string;
  family_size: number;
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}
