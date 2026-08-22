import type { MetadataRoute } from "next";
import { products } from "@/data/products";

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL || "https://www.toruscoffeecompany.com";

export default function sitemap(): MetadataRoute.Sitemap {
  const staticRoutes = [
    "",
    "/shop",
    "/blog",
    "/blog/the-orbit-report",
    "/blog/the-orbit-workshop",
    "/blog/the-orbit-kitchen",
    "/about",
    "/find-us",
    "/contact",
    "/wholesale",
    "/privacy-policy",
    "/terms-and-conditions",
    "/refund-returns-policy",
    "/shipping-policy",
    "/accessibility-statement",
  ];

  const productRoutes = products.map((product) => `/shop/${product.slug}`);

  return [...staticRoutes, ...productRoutes].map((route) => ({
    url: `${siteUrl}${route}`,
    lastModified: new Date(),
  }));
}
