import { apiClient, publicClient } from "./client";
import type { Family, FamilyCreateRequest, FamilyCreateResponse } from "../types/user";

export async function createFamily(data: FamilyCreateRequest): Promise<FamilyCreateResponse> {
  return publicClient.post("api/v1/families", { json: data }).json<FamilyCreateResponse>();
}

export async function getFamily(familyId: string): Promise<Family> {
  return apiClient.get(`api/v1/families/${familyId}`).json<Family>();
}

export async function updateFamily(
  familyId: string,
  data: { name?: string; family_size?: number },
): Promise<Family> {
  return apiClient.put(`api/v1/families/${familyId}`, { json: data }).json<Family>();
}

export async function deleteFamily(familyId: string, password: string): Promise<void> {
  await apiClient.delete(`api/v1/families/${familyId}`, { json: { password } });
}

export async function exportFamilyData(familyId: string): Promise<unknown> {
  return apiClient.get(`api/v1/families/${familyId}/export`).json();
}
