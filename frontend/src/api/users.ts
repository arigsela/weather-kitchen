import { apiClient } from "./client";
import type { User } from "../types/user";

export async function listUsers(): Promise<User[]> {
  const res = await apiClient.get("api/v1/users").json<{ users: User[]; total: number }>();
  return res.users;
}

export async function createUser(data: { name: string; emoji?: string }): Promise<User> {
  return apiClient.post("api/v1/users", { json: data }).json<User>();
}

export async function getUser(userId: string): Promise<User> {
  return apiClient.get(`api/v1/users/${userId}`).json<User>();
}
