type CacheItem<T> = {
  data: T;
  timestamp: number;
};

type CacheMap = {
  [key: string]: CacheItem<any>;
};

class Cache {
  private static instance: Cache;
  private cache: CacheMap = {};
  private readonly TTL: number = 5 * 60 * 1000; // 5 минут в миллисекундах

  private constructor() {}

  static getInstance(): Cache {
    if (!Cache.instance) {
      Cache.instance = new Cache();
    }
    return Cache.instance;
  }

  set<T>(key: string, data: T): void {
    this.cache[key] = {
      data,
      timestamp: Date.now(),
    };
  }

  get<T>(key: string): T | null {
    const item = this.cache[key];
    if (!item) return null;

    const isExpired = Date.now() - item.timestamp > this.TTL;
    if (isExpired) {
      delete this.cache[key];
      return null;
    }

    return item.data as T;
  }

  clear(): void {
    this.cache = {};
  }

  remove(key: string): void {
    delete this.cache[key];
  }
}

export const cache = Cache.getInstance();