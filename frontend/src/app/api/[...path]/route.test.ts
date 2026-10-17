import { afterEach, describe, expect, it, vi } from "vitest";
import { NextRequest } from "next/server";

import { GET, POST } from "./route";

describe("API proxy route", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    delete process.env.API_INTERNAL_URL;
  });

  it("forwards API paths, query strings, and bearer credentials", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "content-type": "application/json" },
      }),
    );
    vi.stubGlobal("fetch", fetchMock);
    process.env.API_INTERNAL_URL = "http://backend:8000/api/v1";
    const request = new NextRequest("http://localhost/api/auth/me?fields=id", {
      headers: { Authorization: "Bearer test-token" },
    });

    const response = await GET(request, {
      params: Promise.resolve({ path: ["auth", "me"] }),
    });

    const [target, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(target).toEqual(new URL("http://backend:8000/api/v1/auth/me?fields=id"));
    expect(init.method).toBe("GET");
    expect(init.cache).toBe("no-store");
    expect(new Headers(init.headers).get("authorization")).toBe("Bearer test-token");
    expect(response.status).toBe(200);
  });

  it("forwards multipart bodies without rewriting their content type", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(null, { status: 202 }));
    vi.stubGlobal("fetch", fetchMock);
    const form = new FormData();
    form.append("document", new File(["school policy"], "policy.txt", { type: "text/plain" }));
    const request = new NextRequest("http://localhost/api/ai/documents", {
      method: "POST",
      body: form,
    });

    await POST(request, { params: Promise.resolve({ path: ["ai", "documents"] }) });

    const [target, init] = fetchMock.mock.calls[0] as [URL, RequestInit];
    expect(target).toEqual(new URL("http://localhost:8000/api/v1/ai/documents"));
    expect(init.method).toBe("POST");
    expect(new Headers(init.headers).get("content-type")).toContain("multipart/form-data");
    expect(init.body).toBeInstanceOf(ArrayBuffer);
  });
});
