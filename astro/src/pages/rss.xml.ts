import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';
import type { APIContext } from 'astro';

export async function GET(context: APIContext) {
  const guides = await getCollection('guides', (entry) => !entry.data.noindex);

  const items = guides
    .sort((a, b) => b.data.published.getTime() - a.data.published.getTime())
    .map((guide) => ({
      title: guide.data.title,
      pubDate: guide.data.published,
      description: guide.data.description,
      link: `/guides/${guide.id}/`,
      author: guide.data.author,
      categories: [guide.data.cluster, ...guide.data.tags],
    }));

  return rss({
    title: 'ChevyRoots — Independent Chevrolet Resource',
    description:
      'Honest Chevy buyer\'s guides, build features, event coverage, and the weekly editorial column from Crystal — founder, editor-in-chief, and ZR2 driver.',
    site: context.site ?? 'https://chevyroots.com',
    items,
    customData: '<language>en-us</language>',
    stylesheet: '/rss-styles.xsl',
  });
}
