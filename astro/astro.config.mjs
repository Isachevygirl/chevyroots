// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  site: process.env.SITE_URL || 'https://chevyroots.com',
  integrations: [
    mdx(),
    sitemap({
      filter: (page) => !page.includes('/admin') && !page.includes('/drafts'),
      changefreq: 'weekly',
      priority: 0.7,
    }),
  ],
  build: {
    format: 'directory',
  },
  markdown: {
    shikiConfig: {
      theme: 'github-dark-dimmed',
      wrap: true,
    },
  },
});
