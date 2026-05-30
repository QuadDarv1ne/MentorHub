import {
  formatNumber,
  formatCurrency,
  abbreviateNumber,
  formatPercent,
  toKebabCase,
  toCamelCase,
  toPascalCase,
  truncate,
  capitalize,
  capitalizeWords,
  getInitials,
  randomColor,
  hexToRgb,
  rgbToHex,
  formatBytes,
  createSlug,
  pluralize,
  maskEmail,
  chunk,
  shuffle,
  unique,
  groupBy,
  sortBy,
} from '../format';

describe('formatNumber', () => {
  it('formats numbers with thousand separators', () => {
    expect(formatNumber(1000)).toBe('1\xa0000');
    expect(formatNumber(1000000)).toBe('1\xa0000\xa0000');
  });

  it('formats with decimals', () => {
    expect(formatNumber(1234.56, 2)).toContain('1');
    expect(formatNumber(1234.56, 2)).toContain('2');
  });

  it('formats zero', () => {
    expect(formatNumber(0)).toBe('0');
  });
});

describe('formatCurrency', () => {
  it('formats RUB currency', () => {
    const result = formatCurrency(1000, 'RUB');
    expect(result).toContain('1');
    expect(result).toContain('\u20BD'); // ₽ symbol
  });

  it('formats USD currency', () => {
    const result = formatCurrency(1000, 'USD');
    expect(result).toContain('1');
    expect(result).toContain('$');
  });
});

describe('abbreviateNumber', () => {
  it('abbreviates thousands', () => {
    expect(abbreviateNumber(1500)).toBe('1.5K');
    expect(abbreviateNumber(2000)).toBe('2.0K');
  });

  it('abbreviates millions', () => {
    expect(abbreviateNumber(1500000)).toBe('1.5M');
  });

  it('abbreviates billions', () => {
    expect(abbreviateNumber(1500000000)).toBe('1.5B');
  });

  it('returns small numbers as is', () => {
    expect(abbreviateNumber(999)).toBe('999');
  });
});

describe('formatPercent', () => {
  it('formats percentages', () => {
    expect(formatPercent(75.5)).toBe('76%');
    expect(formatPercent(75.5, 1)).toBe('75.5%');
    expect(formatPercent(75.567, 2)).toBe('75.57%');
  });
});

describe('toKebabCase', () => {
  it('converts camelCase to kebab-case', () => {
    expect(toKebabCase('helloWorld')).toBe('hello-world');
  });

  it('converts spaces to dashes', () => {
    expect(toKebabCase('hello world')).toBe('hello-world');
  });

  it('converts underscores to dashes', () => {
    expect(toKebabCase('hello_world')).toBe('hello-world');
  });
});

describe('toCamelCase', () => {
  it('converts kebab-case to camelCase', () => {
    expect(toCamelCase('hello-world')).toBe('helloWorld');
  });

  it('converts spaces to camelCase', () => {
    expect(toCamelCase('hello world')).toBe('helloWorld');
  });
});

describe('toPascalCase', () => {
  it('converts kebab-case to PascalCase', () => {
    expect(toPascalCase('hello-world')).toBe('HelloWorld');
  });
});

describe('truncate', () => {
  it('truncates long strings', () => {
    expect(truncate('Hello World', 8)).toBe('Hello...');
  });

  it('does not truncate short strings', () => {
    expect(truncate('Hi', 10)).toBe('Hi');
  });
});

describe('capitalize', () => {
  it('capitalizes first letter', () => {
    expect(capitalize('hello')).toBe('Hello');
    expect(capitalize('Hello')).toBe('Hello');
  });
});

describe('capitalizeWords', () => {
  it('capitalizes each word', () => {
    expect(capitalizeWords('hello world')).toBe('Hello World');
  });
});

describe('getInitials', () => {
  it('extracts initials from full name', () => {
    expect(getInitials('John Doe')).toBe('JD');
    expect(getInitials('John')).toBe('J');
  });
});

describe('randomColor', () => {
  it('generates valid hex color', () => {
    const color = randomColor();
    expect(color).toMatch(/^#[0-9a-f]{6}$/);
  });
});

describe('hexToRgb', () => {
  it('converts hex to RGB', () => {
    const result = hexToRgb('#ff0000');
    expect(result).toEqual({ r: 255, g: 0, b: 0 });
  });

  it('returns null for invalid hex', () => {
    expect(hexToRgb('invalid')).toBeNull();
  });
});

describe('rgbToHex', () => {
  it('converts RGB to hex', () => {
    expect(rgbToHex(255, 0, 0)).toBe('#ff0000');
    expect(rgbToHex(0, 255, 0)).toBe('#00ff00');
  });
});

describe('formatBytes', () => {
  it('formats bytes correctly', () => {
    expect(formatBytes(0)).toBe('0 Bytes');
    expect(formatBytes(1024)).toBe('1 KB');
    expect(formatBytes(1048576)).toBe('1 MB');
  });
});

describe('createSlug', () => {
  it('creates URL-friendly slugs', () => {
    expect(createSlug('Hello World!')).toBe('hello-world');
    expect(createSlug('Привет мир')).toBe('привет-мир');
  });
});

describe('pluralize', () => {
  it('handles Russian pluralization', () => {
    expect(pluralize(1, 'комментарий', 'комментария', 'комментариев')).toBe('комментарий');
    expect(pluralize(2, 'комментарий', 'комментария', 'комментариев')).toBe('комментария');
    expect(pluralize(5, 'комментарий', 'комментария', 'комментариев')).toBe('комментариев');
    expect(pluralize(21, 'комментарий', 'комментария', 'комментариев')).toBe('комментарий');
  });
});

describe('maskEmail', () => {
  it('masks email correctly', () => {
    expect(maskEmail('test@example.com')).toBe('t***@example.com');
    expect(maskEmail('ab@example.com')).toBe('ab@example.com'); // short name
  });
});

describe('chunk', () => {
  it('splits array into chunks', () => {
    expect(chunk([1, 2, 3, 4, 5], 2)).toEqual([[1, 2], [3, 4], [5]]);
    expect(chunk([1, 2, 3], 1)).toEqual([[1], [2], [3]]);
  });
});

describe('shuffle', () => {
  it('returns array with same elements', () => {
    const original = [1, 2, 3, 4, 5];
    const shuffled = shuffle(original);
    expect(shuffled.sort()).toEqual([...original].sort());
    expect(shuffled.length).toBe(original.length);
  });
});

describe('unique', () => {
  it('removes duplicates', () => {
    expect(unique([1, 2, 2, 3, 3, 3])).toEqual([1, 2, 3]);
  });
});

describe('groupBy', () => {
  it('groups objects by key', () => {
    const data = [
      { type: 'fruit', name: 'apple' },
      { type: 'fruit', name: 'banana' },
      { type: 'vegetable', name: 'carrot' },
    ];
    const result = groupBy(data, 'type');
    expect(result.fruit).toHaveLength(2);
    expect(result.vegetable).toHaveLength(1);
  });
});

describe('sortBy', () => {
  it('sorts array ascending', () => {
    const data = [{ age: 30 }, { age: 20 }, { age: 25 }];
    const result = sortBy(data, 'age');
    expect(result.map(x => x.age)).toEqual([20, 25, 30]);
  });

  it('sorts array descending', () => {
    const data = [{ age: 30 }, { age: 20 }, { age: 25 }];
    const result = sortBy(data, 'age', 'desc');
    expect(result.map(x => x.age)).toEqual([30, 25, 20]);
  });
});
