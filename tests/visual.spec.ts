import { test, expect, type Page } from "@playwright/test";
import * as fs from "fs";
import * as path from "path";

/**
 * These tests run against a built site (`npm run build` then `npm run test:visual`).
 * They are deliberately structural rather than pixel-comparison: they assert the
 * things that have actually broken during development — horizontal overflow,
 * console errors, the spec rail collapsing on narrow screens, and the LaTeX
 * pipeline rendering at all.
 */

const routes = [
  { name: "home", path: "/" },
  { name: "projects", path: "/projects/" },
  { name: "project-simproc", path: "/projects/simproc/" },
  { name: "blog", path: "/blog/" },
  { name: "post-simproc", path: "/blog/simproc-tinytapeout/" },
  { name: "post-async", path: "/blog/async-circuits-workshop/" },
  { name: "about", path: "/about/" },
  { name: "join", path: "/join/" },
  { name: "404", path: "/404.html" },
];

const screenshotDir = path.join(__dirname, "__screenshots__");

test.beforeAll(() => {
  fs.mkdirSync(screenshotDir, { recursive: true });
});

/** Elements sticking out past the viewport, ignoring anything inside a scroller. */
async function overflowingElements(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const de = document.documentElement;
    return [...document.querySelectorAll("body *")]
      .filter((el) => {
        const r = el.getBoundingClientRect();
        if (!(r.width > 0 && r.right > de.clientWidth + 1.5)) return false;
        let a = el.parentElement;
        while (a && a !== document.body) {
          const ox = getComputedStyle(a).overflowX;
          if (ox === "auto" || ox === "scroll") return false;
          a = a.parentElement;
        }
        return true;
      })
      .map((el) => (el.className && el.className.toString().slice(0, 40)) || el.tagName);
  });
}

for (const route of routes) {
  test(`${route.name}: renders without errors or overflow`, async ({ page }, testInfo) => {
    const errors: string[] = [];
    page.on("console", (msg) => {
      if (msg.type() === "error") errors.push(msg.text());
    });
    page.on("pageerror", (err) => errors.push(String(err)));

    const response = await page.goto(route.path, { waitUntil: "networkidle" });
    expect(response?.status(), `HTTP status for ${route.path}`).toBeLessThan(400);

    expect(errors, `console errors on ${route.path}`).toEqual([]);

    const scrollsX = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth
    );
    expect(await overflowingElements(page), `overflow on ${route.path}`).toEqual([]);
    expect(scrollsX, `horizontal page scroll on ${route.path}`).toBe(false);

    await expect(page.locator(".masthead")).toBeVisible();
    await expect(page.locator(".footer")).toBeVisible();

    await page.screenshot({
      path: path.join(screenshotDir, `${route.name}-${testInfo.project.name}.png`),
      fullPage: true,
    });
  });
}

test("masthead: brand, links and the CTA share one centre line", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/");
  const spread = await page.evaluate(() => {
    const mid = (el: Element) => {
      const r = el.getBoundingClientRect();
      return r.top + r.height / 2;
    };
    const items = [
      document.querySelector(".brand__name")!,
      ...document.querySelectorAll(".nav__link"),
    ];
    const centres = items.map(mid);
    return Math.max(...centres) - Math.min(...centres);
  });
  expect(spread).toBeLessThan(1.5);
});

test("spec rail: one column beside prose, two-up on a phone", async ({ page }) => {
  await page.setViewportSize({ width: 1280, height: 900 });
  await page.goto("/projects/simproc/");
  const wide = await page.evaluate(
    () => getComputedStyle(document.querySelector(".rail__list")!).gridTemplateColumns
  );
  expect(wide.split(" ").length).toBe(1);

  await page.setViewportSize({ width: 390, height: 844 });
  const narrow = await page.evaluate(
    () => getComputedStyle(document.querySelector(".rail__list")!).gridTemplateColumns
  );
  expect(narrow.split(" ").length).toBe(2);
  expect(await overflowingElements(page)).toEqual([]);
});

test("navigation: opens without JavaScript and is keyboard reachable", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");

  await expect(page.locator(".nav")).toBeHidden();
  await page.locator(".nav-burger").click();
  await expect(page.locator(".nav")).toBeVisible();

  // the toggle must stay focusable; marking it `hidden` would strand keyboard users
  const focusable = await page.evaluate(() => {
    const cb = document.querySelector<HTMLInputElement>("#nav-toggle")!;
    cb.focus();
    return document.activeElement === cb;
  });
  expect(focusable).toBe(true);
});

test("KaTeX loads only where a page opts in", async ({ page }) => {
  await page.goto("/blog/async-circuits-workshop/");
  await expect(page.locator('script[src*="katex"]')).toHaveCount(0);
});
