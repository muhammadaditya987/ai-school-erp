import "@testing-library/jest-dom/vitest";
import { render, screen } from "@testing-library/react";
import type { AnchorHTMLAttributes } from "react";
import { describe, expect, it, vi } from "vitest";

import Home from "./page";

vi.mock("next/link", () => ({
  default: ({ children, href }: AnchorHTMLAttributes<HTMLAnchorElement>) => (
    <a href={href}>{children}</a>
  ),
}));

describe("home page", () => {
  it("introduces the school ERP and links to its approach", () => {
    render(<Home />);

    expect(
      screen.getByRole("heading", { name: /make room for a brighter school day/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /explore the approach/i })).toHaveAttribute(
      "href",
      "#approach",
    );
  });
});
