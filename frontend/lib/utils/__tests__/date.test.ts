import {
  formatDate,
  formatTime,
  formatDateTime,
  getRelativeTime,
  addDays,
  subtractDays,
  startOfDay,
  endOfDay,
  isToday,
  isYesterday,
  isTomorrow,
  getWeekRange,
  getMonthRange,
  daysDifference,
  formatDuration,
  isWeekend,
  getMonthName,
  getDayName,
} from '../date';

describe('formatDate', () => {
  it('formats date in short format', () => {
    const date = new Date('2024-01-15');
    const result = formatDate(date, 'short');
    expect(result).toContain('2024');
    expect(result).toContain('01');
    expect(result).toContain('15');
  });

  it('formats date in long format', () => {
    const date = new Date('2024-01-15');
    const result = formatDate(date, 'long');
    expect(result).toContain('2024');
    expect(result).toContain('январ');
  });

  it('accepts string date', () => {
    const result = formatDate('2024-01-15');
    expect(result).toBeTruthy();
  });
});

describe('formatTime', () => {
  it('formats time correctly', () => {
    const date = new Date('2024-01-15T14:30:00');
    const result = formatTime(date);
    expect(result).toContain('14');
    expect(result).toContain('30');
  });
});

describe('formatDateTime', () => {
  it('formats date and time together', () => {
    const date = new Date('2024-01-15T14:30:00');
    const result = formatDateTime(date);
    expect(result).toBeTruthy();
    expect(result.length).toBeGreaterThan(0);
  });
});

describe('getRelativeTime', () => {
  it('returns "только что" for recent events', () => {
    const now = new Date();
    const result = getRelativeTime(now);
    expect(result).toBe('только что');
  });

  it('returns minutes for recent past', () => {
    const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
    const result = getRelativeTime(fiveMinutesAgo);
    expect(result).toContain('минут');
  });

  it('returns "вчера" for yesterday', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const result = getRelativeTime(yesterday);
    expect(result).toBe('вчера');
  });
});

describe('addDays', () => {
  it('adds days to date', () => {
    const date = new Date('2024-01-15');
    const result = addDays(date, 5);
    expect(result.getDate()).toBe(20);
  });

  it('handles negative values', () => {
    const date = new Date('2024-01-15');
    const result = addDays(date, -5);
    expect(result.getDate()).toBe(10);
  });
});

describe('subtractDays', () => {
  it('subtracts days from date', () => {
    const date = new Date('2024-01-15');
    const result = subtractDays(date, 5);
    expect(result.getDate()).toBe(10);
  });
});

describe('startOfDay', () => {
  it('sets time to start of day', () => {
    const date = new Date('2024-01-15T14:30:45.123');
    const result = startOfDay(date);
    expect(result.getHours()).toBe(0);
    expect(result.getMinutes()).toBe(0);
    expect(result.getSeconds()).toBe(0);
  });
});

describe('endOfDay', () => {
  it('sets time to end of day', () => {
    const date = new Date('2024-01-15T14:30:45.123');
    const result = endOfDay(date);
    expect(result.getHours()).toBe(23);
    expect(result.getMinutes()).toBe(59);
    expect(result.getSeconds()).toBe(59);
  });
});

describe('isToday', () => {
  it('returns true for today', () => {
    expect(isToday(new Date())).toBe(true);
  });

  it('returns false for other dates', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(isToday(yesterday)).toBe(false);
  });
});

describe('isYesterday', () => {
  it('returns true for yesterday', () => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    expect(isYesterday(yesterday)).toBe(true);
  });
});

describe('isTomorrow', () => {
  it('returns true for tomorrow', () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    expect(isTomorrow(tomorrow)).toBe(true);
  });
});

describe('getWeekRange', () => {
  it('returns start and end of week', () => {
    const date = new Date('2024-01-15'); // Monday
    const { start, end } = getWeekRange(date);
    expect(start.getDay()).toBe(1); // Monday
    expect(end.getDate()).toBe(start.getDate() + 6);
  });
});

describe('getMonthRange', () => {
  it('returns start and end of month', () => {
    const date = new Date('2024-01-15');
    const { start, end } = getMonthRange(date);
    expect(start.getDate()).toBe(1);
    expect(end.getMonth()).toBe(date.getMonth());
    expect(end.getFullYear()).toBe(date.getFullYear());
  });
});

describe('daysDifference', () => {
  it('calculates difference between dates', () => {
    const date1 = new Date('2024-01-01');
    const date2 = new Date('2024-01-11');
    expect(daysDifference(date1, date2)).toBe(10);
  });

  it('handles negative difference', () => {
    const date1 = new Date('2024-01-11');
    const date2 = new Date('2024-01-01');
    expect(daysDifference(date1, date2)).toBe(-10);
  });
});

describe('formatDuration', () => {
  it('formats minutes less than 60', () => {
    expect(formatDuration(30)).toBe('30 мин');
  });

  it('formats hours', () => {
    expect(formatDuration(120)).toBe('2 часа');
    expect(formatDuration(60)).toBe('1 час');
  });

  it('formats hours and minutes', () => {
    expect(formatDuration(90)).toBe('1 ч 30 мин');
  });
});

describe('isWeekend', () => {
  it('returns true for Saturday', () => {
    const saturday = new Date('2024-01-13');
    expect(isWeekend(saturday)).toBe(true);
  });

  it('returns true for Sunday', () => {
    const sunday = new Date('2024-01-14');
    expect(isWeekend(sunday)).toBe(true);
  });

  it('returns false for weekday', () => {
    const monday = new Date('2024-01-15');
    expect(isWeekend(monday)).toBe(false);
  });
});

describe('getMonthName', () => {
  it('returns month name in Russian', () => {
    const date = new Date('2024-01-15');
    const result = getMonthName(date);
    expect(result).toContain('январ');
  });
});

describe('getDayName', () => {
  it('returns day name in Russian', () => {
    const monday = new Date('2024-01-15');
    const result = getDayName(monday);
    expect(result).toContain('понедельник');
  });
});
