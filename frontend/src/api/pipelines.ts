import { apiClient } from "./client";
import type {
  NodeTypesResponse,
  PipelineDefinition,
  PipelineListResponse,
  PipelineRunsResponse,
  RunResponse,
  ValidationResponse,
} from "../types/pipeline";

export async function fetchPipelines(): Promise<PipelineListResponse> {
  const { data } = await apiClient.get("/pipelines");
  return data;
}

export async function fetchPipeline(id: string): Promise<PipelineDefinition> {
  const { data } = await apiClient.get(`/pipelines/${id}`);
  return data;
}

export async function fetchNodeTypes(): Promise<NodeTypesResponse> {
  const { data } = await apiClient.get("/pipelines/meta/node-types");
  return data;
}

export async function validatePipeline(id: string): Promise<ValidationResponse> {
  const { data } = await apiClient.post(`/pipelines/${id}/validate`);
  return data;
}

export async function runPipeline(id: string): Promise<RunResponse> {
  const { data } = await apiClient.post(`/pipelines/${id}/run`, {
    triggered_by: "frontend",
  });
  return data;
}

export async function fetchPipelineRuns(id: string): Promise<PipelineRunsResponse> {
  const { data } = await apiClient.get(`/pipelines/${id}/runs`);
  return data;
}

export async function updatePipeline(
  id: string,
  payload: PipelineDefinition
): Promise<PipelineDefinition> {
  const { data } = await apiClient.put(`/pipelines/${id}`, payload);
  return data;
}
