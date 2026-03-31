import ky from "ky";
import type { FamilyCreateResponse, LoginRequest, TokenResponse } from "../types/user";

const API_URL = import.meta.env.VITE_API_URL || window.location.origin;

export async function login(data: LoginRequest): Promise<FamilyCreateResponse> {
  return ky.post(`${API_URL}/api/v1/auth/login`, { json: data }).json<FamilyCreateResponse>();
}

export async function refreshTokens(refreshToken: string): Promise<TokenResponse> {
  return ky
    .post(`${API_URL}/api/v1/auth/refresh`, {
      json: { refresh_token: refreshToken },
    })
    .json<TokenResponse>();
}

export async function logout(refreshToken: string): Promise<void> {
  await ky.post(`${API_URL}/api/v1/auth/logout`, {
    json: { refresh_token: refreshToken },
  });
}
