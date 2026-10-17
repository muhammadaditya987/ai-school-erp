import { describe, expect, it } from "vitest";

import authReducer, { clearAccessToken, setAccessToken } from "./authSlice";

describe("authentication state", () => {
  it("stores and clears the access token", () => {
    const authenticated = authReducer(undefined, setAccessToken("access-token"));
    expect(authenticated.accessToken).toBe("access-token");

    const signedOut = authReducer(authenticated, clearAccessToken());
    expect(signedOut.accessToken).toBeNull();
  });
});
