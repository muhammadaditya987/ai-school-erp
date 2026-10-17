import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from "@reduxjs/toolkit/query/react";

import type { RootState } from "./store";
import { clearAccessToken } from "./authSlice";

export interface SchoolRegistration {
  school_name: string;
  school_slug: string;
  full_name: string;
  email: string;
  password: string;
}

export interface CurrentUser {
  id: string;
  school_id: string;
  email: string;
  full_name: string;
  role: "school_admin" | "teacher" | "student" | "parent";
  created_at: string;
}

export interface AsyncJob {
  id: string;
  status: string;
}

export interface KnowledgeDocument extends AsyncJob {
  filename: string;
}

interface AskResult {
  id: string;
  status: string;
  answer?: string;
  provider?: string;
  error?: string;
}

interface AccessTokenResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
}

const rawBaseQuery = fetchBaseQuery({
  baseUrl: process.env.NEXT_PUBLIC_API_URL ?? "/api",
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.accessToken;
    if (token) {
      headers.set("authorization", `Bearer ${token}`);
    }
    return headers;
  },
});

const baseQuery: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  const result = await rawBaseQuery(args, api, extraOptions);
  if (result.error?.status === 401) {
    api.dispatch(clearAccessToken());
  }
  return result;
};

export const authApi = createApi({
  reducerPath: "authApi",
  baseQuery,
  tagTypes: ["CurrentUser", "KnowledgeDocuments"],
  endpoints: (builder) => ({
    registerSchool: builder.mutation<CurrentUser, SchoolRegistration>({
      query: (body) => ({ url: "/auth/register", method: "POST", body }),
    }),
    createAccessToken: builder.mutation<
      AccessTokenResponse,
      { email: string; password: string }
    >({
      query: ({ email, password }) => ({
        url: "/auth/token",
        method: "POST",
        body: new URLSearchParams({ username: email, password }),
        headers: { "content-type": "application/x-www-form-urlencoded" },
      }),
    }),
    getCurrentUser: builder.query<CurrentUser, void>({
      query: () => "/auth/me",
      providesTags: ["CurrentUser"],
    }),
    uploadKnowledgeDocument: builder.mutation<AsyncJob, File>({
      query: (file) => {
        const body = new FormData();
        body.append("document", file);
        return { url: "/ai/documents", method: "POST", body };
      },
      invalidatesTags: ["KnowledgeDocuments"],
    }),
    getKnowledgeDocuments: builder.query<KnowledgeDocument[], void>({
      query: () => "/ai/documents",
      providesTags: ["KnowledgeDocuments"],
    }),
    askAssistant: builder.mutation<AsyncJob, string>({
      query: (question) => ({ url: "/ai/ask", method: "POST", body: { question } }),
    }),
    getAiJob: builder.query<AskResult, string>({
      query: (id) => `/ai/jobs/${id}`,
    }),
  }),
});

export const {
  useRegisterSchoolMutation,
  useCreateAccessTokenMutation,
  useGetCurrentUserQuery,
  useUploadKnowledgeDocumentMutation,
  useGetKnowledgeDocumentsQuery,
  useAskAssistantMutation,
  useGetAiJobQuery,
} = authApi;
