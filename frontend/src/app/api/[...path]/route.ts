import { NextRequest } from "next/server";

export const dynamic = "force-dynamic";

type RouteContext = { params: Promise<{ path: string[] }> };

async function proxy(request: NextRequest, context: RouteContext): Promise<Response> {
  const { path } = await context.params;
  const configuredApiBase = process.env.API_INTERNAL_URL ?? "http://localhost:8000/api/v1";
  const normalizedApiBase = /^https?:\/\//i.test(configuredApiBase)
    ? configuredApiBase
    : `http://${configuredApiBase.replace(/\/+$/, "")}/api/v1`;
  const apiBase = normalizedApiBase.replace(/\/+$/, "");
  const target = new URL(`${apiBase.replace(/\/+$/, "")}/${path.map(encodeURIComponent).join("/")}`);
  target.search = request.nextUrl.search;

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("connection");
  headers.delete("content-length");

  const method = request.method.toUpperCase();
  const body = method === "GET" || method === "HEAD" ? undefined : await request.arrayBuffer();
  const upstream = await fetch(target, {
    method,
    headers,
    body,
    cache: "no-store",
    signal: request.signal,
  });
  const responseHeaders = new Headers(upstream.headers);
  responseHeaders.delete("connection");
  responseHeaders.delete("transfer-encoding");
  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
