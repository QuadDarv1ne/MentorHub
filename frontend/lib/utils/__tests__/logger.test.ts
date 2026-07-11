/**
 * @jest-environment jsdom
 */

jest.mock('@sentry/nextjs', () => ({
  captureException: jest.fn(),
}));

// eslint-disable-next-line @typescript-eslint/no-require-imports
function getFreshLogger() {
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const FreshSentry = require('@sentry/nextjs');
  // eslint-disable-next-line @typescript-eslint/no-require-imports
  const FreshLogger = require('../logger').logger;
  return { logger: FreshLogger, captureException: FreshSentry.captureException as jest.Mock };
}

describe('logger in development mode', () => {
  let logger: ReturnType<typeof getFreshLogger>['logger'];
  let mockCaptureException: jest.Mock;

  beforeAll(() => {
    process.env.NODE_ENV = 'development';
    process.env.NEXT_PUBLIC_SENTRY_DSN = 'https://test@sentry.io/123';
    jest.resetModules();
    const fresh = getFreshLogger();
    logger = fresh.logger;
    mockCaptureException = fresh.captureException;
  });

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'info').mockImplementation(() => {});
    jest.spyOn(console, 'debug').mockImplementation(() => {});
  });

  it('logs error messages', () => {
    logger.error('Test error');
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('[ERROR] Test error')
    );
  });

  it('logs warn messages', () => {
    logger.warn('Test warning');
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('[WARN] Test warning')
    );
  });

  it('logs info messages', () => {
    logger.info('Test info');
    expect(console.info).toHaveBeenCalledWith(
      expect.stringContaining('[INFO] Test info')
    );
  });

  it('logs debug messages', () => {
    logger.debug('Test debug');
    expect(console.debug).toHaveBeenCalledWith(
      expect.stringContaining('[DEBUG] Test debug')
    );
  });

  it('formats timestamp in log message', () => {
    logger.info('Test');
    expect(console.info).toHaveBeenCalledWith(
      expect.stringMatching(/^\[\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)
    );
  });

  it('includes extra args in log message', () => {
    logger.error('Error:', new Error('detail'));
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('[ERROR] Error:')
    );
  });

  it('sends errors to Sentry when DSN is configured', () => {
    logger.error('Sentry error', new Error('test'));
    expect(mockCaptureException).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        tags: { level: 'error', source: 'client-logger' },
      })
    );
  });

  it('does not send warnings to Sentry', () => {
    logger.warn('Warning');
    expect(mockCaptureException).not.toHaveBeenCalled();
  });

  it('creates Error from string if no Error arg provided', () => {
    logger.error('Plain error message');
    expect(mockCaptureException).toHaveBeenCalledWith(
      expect.any(Error),
      expect.any(Object)
    );
    const sentryArg = mockCaptureException.mock.calls[0][0];
    expect(sentryArg.message).toBe('Plain error message');
  });

  it('passes Error object to Sentry when provided', () => {
    const testError = new Error('Original error');
    logger.error('Context', testError);
    expect(mockCaptureException).toHaveBeenCalledWith(
      testError,
      expect.any(Object)
    );
  });

  it('logs WebSocket connection', () => {
    logger.wsConnected('chat');
    expect(console.info).toHaveBeenCalledWith(
      expect.stringContaining('WebSocket connected: chat')
    );
  });

  it('logs WebSocket disconnection', () => {
    logger.wsDisconnected('chat');
    expect(console.warn).toHaveBeenCalledWith(
      expect.stringContaining('WebSocket disconnected: chat')
    );
  });

  it('logs WebSocket error', () => {
    logger.wsError('chat', new Error('timeout'));
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('WebSocket error in chat')
    );
  });

  it('logs API errors with endpoint', () => {
    logger.apiError('/users/me', new Error('401'));
    expect(console.error).toHaveBeenCalledWith(
      expect.stringContaining('API error at /users/me')
    );
  });
});

describe('logger in production mode', () => {
  let logger: ReturnType<typeof getFreshLogger>['logger'];
  let _mockCaptureException: jest.Mock;

  beforeAll(() => {
    process.env.NODE_ENV = 'production';
    process.env.NEXT_PUBLIC_SENTRY_DSN = 'https://test@sentry.io/123';
    jest.resetModules();
    const fresh = getFreshLogger();
    logger = fresh.logger;
    _mockCaptureException = fresh.captureException;
  });

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'info').mockImplementation(() => {});
    jest.spyOn(console, 'debug').mockImplementation(() => {});
  });

  it('logs error in production', () => {
    logger.error('Prod error');
    expect(console.error).toHaveBeenCalled();
  });

  it('logs warn in production', () => {
    logger.warn('Prod warning');
    expect(console.warn).toHaveBeenCalled();
  });

  it('does not log info in production', () => {
    logger.info('Prod info');
    expect(console.info).not.toHaveBeenCalled();
  });

  it('does not log debug in production', () => {
    logger.debug('Prod debug');
    expect(console.debug).not.toHaveBeenCalled();
  });
});

describe('logger without Sentry DSN', () => {
  let logger: ReturnType<typeof getFreshLogger>['logger'];
  let mockCaptureException: jest.Mock;

  beforeAll(() => {
    process.env.NODE_ENV = 'development';
    delete process.env.NEXT_PUBLIC_SENTRY_DSN;
    jest.resetModules();
    const fresh = getFreshLogger();
    logger = fresh.logger;
    mockCaptureException = fresh.captureException;
  });

  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('does not send to Sentry when DSN is not configured', () => {
    logger.error('No DSN');
    expect(mockCaptureException).not.toHaveBeenCalled();
  });
});
