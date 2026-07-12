import type { Metadata } from 'next'
import {
  generateSEOMetadata,
  seoPresets,
  generateOrganizationSchema,
  generateCourseSchema,
  generatePersonSchema,
} from '../seo';

const originalBaseUrl = process.env.NEXT_PUBLIC_BASE_URL;

beforeAll(() => {
  process.env.NEXT_PUBLIC_BASE_URL = 'https://mentorhub.com';
});

afterAll(() => {
  if (originalBaseUrl) {
    process.env.NEXT_PUBLIC_BASE_URL = originalBaseUrl;
  } else {
    delete process.env.NEXT_PUBLIC_BASE_URL;
  }
});

describe('generateSEOMetadata', () => {
  it('generates title with site name', () => {
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc' });
    expect(meta.title).toBe('Test | MentorHub');
  });

  it('does not duplicate site name when already present', () => {
    const meta = generateSEOMetadata({ title: 'MentorHub - Test', description: 'Desc' });
    expect(meta.title).toBe('MentorHub - Test');
  });

  it('generates Open Graph metadata', () => {
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc', path: '/test' });
    expect(meta.openGraph).toBeDefined();
    expect(meta.openGraph!.title).toBe('Test | MentorHub');
    expect(meta.openGraph!.description).toBe('Desc');
    expect(meta.openGraph!.url).toBe('https://mentorhub.com/test');
    expect(meta.openGraph!.type).toBe('website');
  });

  it('generates Twitter Card metadata', () => {
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc' });
    expect(meta.twitter).toBeDefined();
    expect(meta.twitter!.card).toBe('summary_large_image');
    expect(meta.twitter!.creator).toBe('@MentorHubApp');
  });

  it('sets noIndex when specified', () => {
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc', noIndex: true });
    expect(meta.robots).toEqual({
      index: false,
      follow: false,
      nocache: true,
      googleBot: { index: false, follow: false },
    });
  });

  it('sets index follow by default', () => {
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc' });
    expect(meta.robots).toEqual({
      index: true,
      follow: true,
      googleBot: {
        index: true,
        follow: true,
        'max-video-preview': -1,
        'max-image-preview': 'large',
        'max-snippet': -1,
      },
    });
  });

  it('generates canonical URL', () => {
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc', path: '/page' });
    expect(meta.alternates).toEqual({ canonical: 'https://mentorhub.com/page' });
  });

  it('sets article-specific metadata for article type', () => {
    const date = '2024-01-15T10:00:00Z';
    const meta = generateSEOMetadata({
      title: 'Article', description: 'Desc',
      type: 'article', publishedTime: date, authors: ['Author'],
    });
    expect(meta.openGraph!.type).toBe('article');
    expect((meta.openGraph as Metadata['openGraph'] & { publishedTime?: string; authors?: string[] }).publishedTime).toBe(date);
    expect((meta.openGraph as Metadata['openGraph'] & { publishedTime?: string; authors?: string[] }).authors).toEqual(['Author']);
  });

  it('handles custom image URL', () => {
    const meta = generateSEOMetadata({
      title: 'Test', description: 'Desc', image: 'https://example.com/img.png',
    });
    const ogImage = (meta.openGraph!.images as { url: string }[])[0];
    expect(ogImage.url).toBe('https://example.com/img.png');
  });

  it('resolves relative image URL', () => {
    const meta = generateSEOMetadata({
      title: 'Test', description: 'Desc', image: '/custom.png',
    });
    const ogImage = (meta.openGraph!.images as { url: string }[])[0];
    expect(ogImage.url).toBe('https://mentorhub.com/custom.png');
  });

  it('includes keywords from tags', () => {
    const meta = generateSEOMetadata({
      title: 'Test', description: 'Desc', tags: ['react', 'typescript'],
    });
    expect(meta.keywords).toEqual(['react', 'typescript']);
  });

  it('includes verification metadata when env vars set', () => {
    process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION = 'google-123';
    process.env.NEXT_PUBLIC_YANDEX_VERIFICATION = 'yandex-456';
    const meta = generateSEOMetadata({ title: 'Test', description: 'Desc' });
    expect(meta.verification).toEqual({
      google: 'google-123',
      yandex: 'yandex-456',
    });
    delete process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION;
    delete process.env.NEXT_PUBLIC_YANDEX_VERIFICATION;
  });
});

describe('seoPresets', () => {
  it('generates home metadata', () => {
    const meta = seoPresets.home();
    expect(meta.title).toContain('MentorHub');
    expect(meta.openGraph!.url).toContain('/');
  });

  it('generates mentors metadata', () => {
    const meta = seoPresets.mentors();
    expect(meta.title).toContain('Каталог менторов');
    expect(meta.openGraph!.url).toContain('/mentors');
  });

  it('generates courses metadata', () => {
    const meta = seoPresets.courses();
    expect(meta.title).toContain('Обучающие курсы');
  });

  it('generates pricing metadata', () => {
    const meta = seoPresets.pricing();
    expect(meta.title).toContain('Тарифы и цены');
  });

  it('generates blog metadata', () => {
    const meta = seoPresets.blog();
    expect(meta.title).toContain('Блог');
  });

  describe('auth presets', () => {
    it('generates login metadata with noIndex', () => {
      const meta = seoPresets.auth.login();
      expect(meta.title).toContain('Вход');
      expect(meta.robots).toBeDefined();
      expect((meta.robots as { index: boolean }).index).toBe(false);
    });

    it('generates register metadata with noIndex', () => {
      const meta = seoPresets.auth.register();
      expect(meta.title).toContain('Регистрация');
      expect((meta.robots as { index: boolean }).index).toBe(false);
    });

    it('generates forgotPassword metadata with noIndex', () => {
      const meta = seoPresets.auth.forgotPassword();
      expect(meta.title).toContain('Восстановление пароля');
      expect((meta.robots as { index: boolean }).index).toBe(false);
    });
  });

  it('generates dashboard metadata with noIndex', () => {
    const meta = seoPresets.dashboard();
    expect(meta.title).toContain('Личный кабинет');
    expect((meta.robots as { index: boolean }).index).toBe(false);
  });

  it('generates profile metadata with noIndex', () => {
    const meta = seoPresets.profile();
    expect(meta.title).toContain('Профиль пользователя');
    expect((meta.robots as { index: boolean }).index).toBe(false);
  });
});

describe('generateOrganizationSchema', () => {
  it('generates valid Organization schema', () => {
    const schema = generateOrganizationSchema();
    expect(schema['@context']).toBe('https://schema.org');
    expect(schema['@type']).toBe('Organization');
    expect(schema.name).toBe('MentorHub');
    expect(schema.url).toContain('mentorhub.com');
    expect(schema.sameAs).toBeInstanceOf(Array);
    expect(schema.sameAs.length).toBeGreaterThan(0);
    expect(schema.contactPoint).toBeDefined();
    expect(schema.contactPoint.contactType).toBe('Customer Service');
  });
});

describe('generateCourseSchema', () => {
  it('generates valid Course schema', () => {
    const schema = generateCourseSchema({
      name: 'Python Basics',
      description: 'Learn Python',
      provider: 'MentorHub',
      url: 'https://mentorhub.com/courses/python',
      image: 'https://example.com/img.jpg',
      price: 2999,
      currency: 'RUB',
    });
    expect(schema['@context']).toBe('https://schema.org');
    expect(schema['@type']).toBe('Course');
    expect(schema.name).toBe('Python Basics');
    expect(schema.provider.name).toBe('MentorHub');
    expect(schema.offers.price).toBe(2999);
    expect(schema.offers.priceCurrency).toBe('RUB');
  });

  it('generates schema without optional fields', () => {
    const schema = generateCourseSchema({
      name: 'Course',
      description: 'Desc',
      provider: 'MentorHub',
      url: 'https://mentorhub.com/course',
    });
    expect(schema.image).toBeUndefined();
    expect(schema.offers).toBeUndefined();
  });
});

describe('generatePersonSchema', () => {
  it('generates valid Person schema', () => {
    const schema = generatePersonSchema({
      name: 'John Doe',
      jobTitle: 'Software Engineer',
      description: 'Experienced mentor',
      image: 'https://example.com/photo.jpg',
      url: 'https://mentorhub.com/mentors/john',
    });
    expect(schema['@context']).toBe('https://schema.org');
    expect(schema['@type']).toBe('Person');
    expect(schema.name).toBe('John Doe');
    expect(schema.jobTitle).toBe('Software Engineer');
    expect(schema.worksFor.name).toBe('MentorHub');
  });
});
