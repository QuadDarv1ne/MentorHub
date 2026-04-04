import {
  isValidEmail,
  isValidPhone,
  validatePassword,
  isValidUrl,
  isValidUsername,
  isValidCreditCard,
  isValidBirthDate,
  isValidZipCode,
  sanitizeHtml,
  isInRange,
  isEmpty,
  isAlpha,
  isNumeric,
  isAlphanumeric,
  isValidINN,
  formatPhone,
  formatCardNumber,
} from '../validation';

describe('isValidEmail', () => {
  it('returns true for valid email', () => {
    expect(isValidEmail('test@example.com')).toBe(true);
    expect(isValidEmail('user.name@domain.org')).toBe(true);
  });

  it('returns false for invalid email', () => {
    expect(isValidEmail('invalid')).toBe(false);
    expect(isValidEmail('test@')).toBe(false);
    expect(isValidEmail('@domain.com')).toBe(false);
    expect(isValidEmail('test@domain')).toBe(false);
    expect(isValidEmail('')).toBe(false);
  });
});

describe('isValidPhone', () => {
  it('returns true for valid Russian phone numbers', () => {
    expect(isValidPhone('+7 (999) 123-45-67')).toBe(true);
    expect(isValidPhone('89991234567')).toBe(true);
    expect(isValidPhone('+79991234567')).toBe(true);
  });

  it('returns false for invalid phone numbers', () => {
    expect(isValidPhone('12345')).toBe(false);
    expect(isValidPhone('abc')).toBe(false);
    expect(isValidPhone('')).toBe(false);
  });
});

describe('validatePassword', () => {
  it('returns invalid for short password', () => {
    const result = validatePassword('abc');
    expect(result.isValid).toBe(false);
    expect(result.errors).toContain('Пароль должен быть не менее 6 символов');
    expect(result.strength).toBe(0);
  });

  it('returns valid for strong password', () => {
    const result = validatePassword('StrongPass1!');
    expect(result.isValid).toBe(true);
    expect(result.errors).toHaveLength(0);
    expect(result.strength).toBeGreaterThanOrEqual(4);
  });

  it('detects missing uppercase', () => {
    const result = validatePassword('weakpassword1');
    expect(result.errors).toContain('Пароль должен содержать строчные и заглавные буквы');
  });

  it('detects missing numbers', () => {
    const result = validatePassword('WeakPassword');
    expect(result.errors).toContain('Пароль должен содержать хотя бы одну цифру');
  });

  it('calculates strength correctly', () => {
    const weak = validatePassword('weak');
    const strong = validatePassword('Str0ng!Pass');
    expect(strong.strength).toBeGreaterThan(weak.strength);
  });
});

describe('isValidUrl', () => {
  it('returns true for valid URLs', () => {
    expect(isValidUrl('https://example.com')).toBe(true);
    expect(isValidUrl('http://localhost:3000')).toBe(true);
    expect(isValidUrl('https://example.com/path?query=value')).toBe(true);
  });

  it('returns false for invalid URLs', () => {
    expect(isValidUrl('not-a-url')).toBe(false);
    expect(isValidUrl('ftp://example.com')).toBe(false);
    expect(isValidUrl('')).toBe(false);
  });
});

describe('isValidUsername', () => {
  it('returns true for valid usernames', () => {
    expect(isValidUsername('user123')).toBe(true);
    expect(isValidUsername('user_name')).toBe(true);
    expect(isValidUsername('user-name')).toBe(true);
    expect(isValidUsername('abc')).toBe(true);
  });

  it('returns false for invalid usernames', () => {
    expect(isValidUsername('ab')).toBe(false); // too short
    expect(isValidUsername('user name')).toBe(false); // space
    expect(isValidUsername('user@name')).toBe(false); // special char
    expect(isValidUsername('')).toBe(false);
  });
});

describe('isValidCreditCard', () => {
  it('returns true for valid card numbers (Luhn algorithm)', () => {
    expect(isValidCreditCard('4532015112830366')).toBe(true);
    expect(isValidCreditCard('5425233430109903')).toBe(true);
    expect(isValidCreditCard('4532 0151 1283 0366')).toBe(true); // with spaces
  });

  it('returns false for invalid card numbers', () => {
    expect(isValidCreditCard('1234567890123')).toBe(false);
    expect(isValidCreditCard('abc')).toBe(false);
    expect(isValidCreditCard('')).toBe(false);
  });
});

describe('isValidBirthDate', () => {
  it('returns true for valid birth dates (13-120 years)', () => {
    const validDate = new Date('1990-01-01');
    expect(isValidBirthDate(validDate)).toBe(true);
  });

  it('returns false for too young person', () => {
    const tooYoung = new Date();
    tooYoung.setFullYear(tooYoung.getFullYear() - 10);
    expect(isValidBirthDate(tooYoung)).toBe(false);
  });

  it('returns false for too old person', () => {
    const tooOld = new Date();
    tooOld.setFullYear(tooOld.getFullYear() - 130);
    expect(isValidBirthDate(tooOld)).toBe(false);
  });
});

describe('isValidZipCode', () => {
  it('returns true for valid 6-digit zip code', () => {
    expect(isValidZipCode('123456')).toBe(true);
  });

  it('returns false for invalid zip codes', () => {
    expect(isValidZipCode('12345')).toBe(false);
    expect(isValidZipCode('1234567')).toBe(false);
    expect(isValidZipCode('abc')).toBe(false);
  });
});

describe('sanitizeHtml', () => {
  it('escapes HTML tags', () => {
    const input = '<script>alert("xss")</script>';
    const result = sanitizeHtml(input);
    expect(result).toBe('&lt;script&gt;alert("xss")&lt;/script&gt;');
  });

  it('preserves text content', () => {
    const input = 'Hello <b>World</b>';
    const result = sanitizeHtml(input);
    expect(result).toBe('Hello &lt;b&gt;World&lt;/b&gt;');
  });
});

describe('isInRange', () => {
  it('returns true for values in range', () => {
    expect(isInRange(5, 1, 10)).toBe(true);
    expect(isInRange(1, 1, 10)).toBe(true);
    expect(isInRange(10, 1, 10)).toBe(true);
  });

  it('returns false for values out of range', () => {
    expect(isInRange(0, 1, 10)).toBe(false);
    expect(isInRange(11, 1, 10)).toBe(false);
  });
});

describe('isEmpty', () => {
  it('returns true for empty or whitespace-only strings', () => {
    expect(isEmpty('')).toBe(true);
    expect(isEmpty('   ')).toBe(true);
    expect(isEmpty('\t\n')).toBe(true);
  });

  it('returns false for non-empty strings', () => {
    expect(isEmpty('hello')).toBe(false);
    expect(isEmpty(' a ')).toBe(false);
  });
});

describe('isAlpha', () => {
  it('returns true for alphabetic strings', () => {
    expect(isAlpha('hello')).toBe(true);
    expect(isAlpha('Привет')).toBe(true);
    expect(isAlpha('abcABC')).toBe(true);
  });

  it('returns false for non-alphabetic strings', () => {
    expect(isAlpha('hello123')).toBe(false);
    expect(isAlpha('hello!')).toBe(false);
    expect(isAlpha('')).toBe(false);
  });
});

describe('isNumeric', () => {
  it('returns true for numeric strings', () => {
    expect(isNumeric('123')).toBe(true);
    expect(isNumeric('0')).toBe(true);
  });

  it('returns false for non-numeric strings', () => {
    expect(isNumeric('abc')).toBe(false);
    expect(isNumeric('123abc')).toBe(false);
    expect(isNumeric('')).toBe(false);
  });
});

describe('isAlphanumeric', () => {
  it('returns true for alphanumeric strings', () => {
    expect(isAlphanumeric('abc123')).toBe(true);
    expect(isAlphanumeric('Привет123')).toBe(true);
  });

  it('returns false for non-alphanumeric strings', () => {
    expect(isAlphanumeric('abc!')).toBe(false);
    expect(isAlphanumeric('')).toBe(false);
  });
});

describe('isValidINN', () => {
  it('returns true for valid INN formats (10 or 12 digits)', () => {
    expect(isValidINN('1234567890')).toBe(true);
    expect(isValidINN('123456789012')).toBe(true);
  });

  it('returns false for invalid INN formats', () => {
    expect(isValidINN('123')).toBe(false);
    expect(isValidINN('abc')).toBe(false);
    expect(isValidINN('')).toBe(false);
  });
});

describe('formatPhone', () => {
  it('formats Russian phone numbers correctly', () => {
    expect(formatPhone('89991234567')).toBe('+7 (999) 123-45-67');
    expect(formatPhone('79991234567')).toBe('+7 (999) 123-45-67');
  });

  it('returns original for non-Russian numbers', () => {
    expect(formatPhone('1234567890')).toBe('1234567890');
  });
});

describe('formatCardNumber', () => {
  it('formats card number with spaces every 4 digits', () => {
    expect(formatCardNumber('4532015112830366')).toBe('4532 0151 1283 0366');
  });

  it('handles non-numeric input', () => {
    expect(formatCardNumber('abc')).toBe('');
  });

  it('handles short numbers', () => {
    expect(formatCardNumber('1234')).toBe('1234');
  });
});
