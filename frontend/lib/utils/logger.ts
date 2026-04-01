/**
 * Logger Utility
 * Централизованное логирование с интеграцией Sentry
 * 
 * Использование:
 * - logger.error() — для критичных ошибок (отправляется в Sentry)
 * - logger.warn() — для предупреждений
 * - logger.info() — для информационных сообщений (только dev)
 * - logger.debug() — для отладки (только dev)
 */

import * as Sentry from '@sentry/nextjs';

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LoggerConfig {
  sentryEnabled: boolean;
  devMode: boolean;
}

const config: LoggerConfig = {
  sentryEnabled: process.env.NEXT_PUBLIC_SENTRY_DSN !== undefined,
  devMode: process.env.NODE_ENV === 'development',
};

class Logger {
  private shouldLog(level: LogLevel): boolean {
    if (config.devMode) return true;
    // В production логируем только warn и error
    return level === 'warn' || level === 'error';
  }

  private formatMessage(level: LogLevel, message: string, ...args: any[]): string {
    const timestamp = new Date().toISOString();
    const argsStr = args.length > 0 ? args.map(arg => 
      typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
    ).join(' ') : '';
    
    return `[${timestamp}] [${level.toUpperCase()}] ${message} ${argsStr}`.trim();
  }

  private sendToSentry(level: LogLevel, message: string, ...args: any[]) {
    if (!config.sentryEnabled || level !== 'error') return;

    const error = args.find(arg => arg instanceof Error) || new Error(message);
    
    Sentry.captureException(error, {
      tags: {
        level,
        source: 'client-logger',
      },
      extra: {
        message,
        args: args.filter(arg => !(arg instanceof Error)),
        timestamp: new Date().toISOString(),
      },
    });
  }

  error(message: string, ...args: any[]): void {
    if (this.shouldLog('error')) {
      console.error(this.formatMessage('error', message, ...args));
    }
    this.sendToSentry('error', message, ...args);
  }

  warn(message: string, ...args: any[]): void {
    if (this.shouldLog('warn')) {
      console.warn(this.formatMessage('warn', message, ...args));
    }
  }

  info(message: string, ...args: any[]): void {
    if (this.shouldLog('info')) {
      console.info(this.formatMessage('info', message, ...args));
    }
  }

  debug(message: string, ...args: any[]): void {
    if (this.shouldLog('debug')) {
      console.debug(this.formatMessage('debug', message, ...args));
    }
  }

  /**
   * Логирование WebSocket событий
   */
  wsConnected(channel: string): void {
    this.info(`✅ WebSocket connected: ${channel}`);
  }

  wsDisconnected(channel: string): void {
    this.warn(`❌ WebSocket disconnected: ${channel}`);
  }

  wsError(channel: string, error: Error): void {
    this.error(`WebSocket error in ${channel}`, error);
  }

  /**
   * Логирование API ошибок
   */
  apiError(endpoint: string, error: Error): void {
    this.error(`API error at ${endpoint}`, error);
  }
}

// Экспортируем глобальный экземпляр
export const logger = new Logger();

// Экспортируем для использования в компонентах
export default logger;
