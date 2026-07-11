/**
 * @jest-environment jsdom
 */
import {
  debounce,
  throttle,
  memoize,
  supportsIntersectionObserver,
  preloadImage,
  preloadImages,
  deepEqual,
  isElementInViewport,
  generateUniqueId,
  formatFileSize,
  safeJsonParse,
  getViewportSize,
  isMobileDevice,
  copyToClipboard,
} from '../performance';

describe('debounce', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('delays function execution', () => {
    const fn = jest.fn();
    const debounced = debounce(fn, 200);
    debounced();
    expect(fn).not.toHaveBeenCalled();
    jest.advanceTimersByTime(200);
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('calls function only once for rapid invocations', () => {
    const fn = jest.fn();
    const debounced = debounce(fn, 200);
    debounced();
    debounced();
    debounced();
    jest.advanceTimersByTime(200);
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('passes arguments to the function', () => {
    const fn = jest.fn();
    const debounced = debounce(fn, 100);
    debounced('a', 1);
    jest.advanceTimersByTime(100);
    expect(fn).toHaveBeenCalledWith('a', 1);
  });
});

describe('throttle', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('calls function immediately first time', () => {
    const fn = jest.fn();
    const throttled = throttle(fn, 200);
    throttled();
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('ignores calls within throttle window', () => {
    const fn = jest.fn();
    const throttled = throttle(fn, 200);
    throttled();
    throttled();
    throttled();
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('allows call after throttle window expires', () => {
    const fn = jest.fn();
    const throttled = throttle(fn, 200);
    throttled();
    jest.advanceTimersByTime(200);
    throttled();
    expect(fn).toHaveBeenCalledTimes(2);
  });
});

describe('memoize', () => {
  it('caches function results', () => {
    const fn = jest.fn((x: number) => x * 2);
    const memoized = memoize(fn);
    expect(memoized(2)).toBe(4);
    expect(memoized(2)).toBe(4);
    expect(fn).toHaveBeenCalledTimes(1);
  });

  it('recomputes for different arguments', () => {
    const fn = jest.fn((x: number) => x * 2);
    const memoized = memoize(fn);
    memoized(2);
    memoized(3);
    expect(fn).toHaveBeenCalledTimes(2);
  });

  it('handles object arguments via JSON stringify', () => {
    const fn = jest.fn((obj: Record<string, number>) => obj.x);
    const memoized = memoize(fn);
    expect(memoized({ x: 1 })).toBe(1);
    expect(memoized({ x: 1 })).toBe(1);
    expect(fn).toHaveBeenCalledTimes(1);
  });
});

describe('supportsIntersectionObserver', () => {
  it('returns true when IntersectionObserver is available', () => {
    class MockIntersectionObserver {
      observe() {}
      unobserve() {}
      disconnect() {}
    }
    (window as any).IntersectionObserver = MockIntersectionObserver;
    (window as any).IntersectionObserverEntry = function() {};
    (window as any).IntersectionObserverEntry.prototype = { intersectionRatio: 1 };
    expect(supportsIntersectionObserver()).toBe(true);
  });

  it('returns false when IntersectionObserver is not available', () => {
    const originalIO = (window as any).IntersectionObserver;
    delete (window as any).IntersectionObserver;
    expect(supportsIntersectionObserver()).toBe(false);
    (window as any).IntersectionObserver = originalIO;
  });

  it('returns false on server-side (window undefined)', () => {
    const origWindow = (global as any).window;
    delete (global as any).window;
    expect(supportsIntersectionObserver()).toBe(false);
    (global as any).window = origWindow;
  });
});

describe('preloadImage', () => {
  beforeEach(() => {
    (global as any).Image = class MockImage {
      onload: (() => void) | null = null;
      onerror: (() => void) | null = null;
      set src(_: string) {
        setTimeout(() => this.onload?.(), 0);
      }
    };
  });

  it('resolves when image loads successfully', async () => {
    await expect(preloadImage('test.jpg')).resolves.toBeUndefined();
  });
});

describe('preloadImages', () => {
  it('loads multiple images', async () => {
    const results = await preloadImages(['a.jpg', 'b.jpg']);
    expect(results).toHaveLength(2);
  });
});

describe('deepEqual', () => {
  it('returns true for identical primitives', () => {
    expect(deepEqual(1, 1)).toBe(true);
    expect(deepEqual('a', 'a')).toBe(true);
    expect(deepEqual(true, true)).toBe(true);
    expect(deepEqual(null, null)).toBe(true);
  });

  it('returns false for different primitives', () => {
    expect(deepEqual(1, 2)).toBe(false);
    expect(deepEqual('a', 'b')).toBe(false);
    expect(deepEqual(null, undefined)).toBe(false);
  });

  it('returns true for identical objects', () => {
    expect(deepEqual({ a: 1, b: 2 }, { a: 1, b: 2 })).toBe(true);
  });

  it('returns false for objects with different keys', () => {
    expect(deepEqual({ a: 1 }, { a: 1, b: 2 })).toBe(false);
  });

  it('returns true for identical arrays', () => {
    expect(deepEqual([1, 2, 3], [1, 2, 3])).toBe(true);
  });

  it('returns false for different arrays', () => {
    expect(deepEqual([1, 2], [1, 3])).toBe(false);
  });

  it('returns false for different length arrays', () => {
    expect(deepEqual([1, 2], [1, 2, 3])).toBe(false);
  });
});

describe('isElementInViewport', () => {
  it('returns true for element in viewport', () => {
    const el = document.createElement('div');
    jest.spyOn(el, 'getBoundingClientRect').mockReturnValue({
      top: 100, left: 100, bottom: 200, right: 200,
      width: 100, height: 100, x: 100, y: 100,
      toJSON: () => {},
    });
    expect(isElementInViewport(el)).toBe(true);
  });

  it('returns false for element out of viewport', () => {
    const el = document.createElement('div');
    jest.spyOn(el, 'getBoundingClientRect').mockReturnValue({
      top: -100, left: 0, bottom: -50, right: 100,
      width: 100, height: 50, x: 0, y: -100,
      toJSON: () => {},
    });
    expect(isElementInViewport(el)).toBe(false);
  });
});

describe('generateUniqueId', () => {
  it('generates ID with prefix', () => {
    const id = generateUniqueId('btn');
    expect(id).toMatch(/^btn-\d+-\d+$/);
  });

  it('generates unique IDs sequentially', () => {
    const id1 = generateUniqueId();
    const id2 = generateUniqueId();
    expect(id1).not.toBe(id2);
  });

  it('uses default prefix "id"', () => {
    const id = generateUniqueId();
    expect(id).toMatch(/^id-/);
  });
});

describe('formatFileSize', () => {
  it('formats 0 bytes', () => {
    expect(formatFileSize(0)).toBe('0 Bytes');
  });

  it('formats bytes', () => {
    expect(formatFileSize(500)).toBe('500 Bytes');
  });

  it('formats KB', () => {
    expect(formatFileSize(1024)).toBe('1 KB');
  });

  it('formats MB', () => {
    expect(formatFileSize(1048576)).toBe('1 MB');
  });

  it('formats GB', () => {
    expect(formatFileSize(1073741824)).toBe('1 GB');
  });
});

describe('safeJsonParse', () => {
  it('parses valid JSON', () => {
    expect(safeJsonParse('{"a":1}', {})).toEqual({ a: 1 });
  });

  it('returns fallback for invalid JSON', () => {
    expect(safeJsonParse('invalid', { fallback: true })).toEqual({ fallback: true });
  });

  it('returns fallback for empty string', () => {
    expect(safeJsonParse('', 'default')).toBe('default');
  });
});

describe('getViewportSize', () => {
  it('returns viewport dimensions', () => {
    const size = getViewportSize();
    expect(size).toHaveProperty('width');
    expect(size).toHaveProperty('height');
    expect(typeof size.width).toBe('number');
    expect(typeof size.height).toBe('number');
  });
});

describe('isMobileDevice', () => {
  it('returns false on non-mobile user agent', () => {
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 Windows',
      configurable: true,
    });
    expect(isMobileDevice()).toBe(false);
  });

  it('returns true for Android user agent', () => {
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 Android',
      configurable: true,
    });
    expect(isMobileDevice()).toBe(true);
  });

  it('returns false when window is undefined', () => {
    const origWindow = (global as any).window;
    delete (global as any).window;
    expect(isMobileDevice()).toBe(false);
    (global as any).window = origWindow;
  });
});

describe('copyToClipboard', () => {
  it('uses clipboard API when available', async () => {
    const writeText = jest.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText },
      configurable: true,
    });
    const result = await copyToClipboard('test');
    expect(result).toBe(true);
    expect(writeText).toHaveBeenCalledWith('test');
  });

  it('returns false when clipboard API fails', async () => {
    Object.defineProperty(navigator, 'clipboard', {
      value: { writeText: jest.fn().mockRejectedValue(new Error('denied')) },
      configurable: true,
    });
    const result = await copyToClipboard('test');
    expect(result).toBe(false);
  });
});
