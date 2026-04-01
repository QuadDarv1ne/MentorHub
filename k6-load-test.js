import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 50 },   // Ramp up to 50 users
    { duration: '5m', target: 50 },   // Stay at 50 users
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 0 },    // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500', 'p(99)<1000'], // 95% of requests under 500ms, 99% under 1s
    http_req_failed: ['rate<0.01'],                  // Error rate under 1%
    errors: ['rate<0.1'],                            // Custom error rate under 10%
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test data
const testUser = {
  email: `test_${Date.now()}@example.com`,
  password: 'TestPassword123!',
  full_name: 'Load Test User',
};

let authToken = '';

export function setup() {
  // Register test user
  const registerRes = http.post(`${BASE_URL}/api/v1/auth/register`, JSON.stringify(testUser), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (registerRes.status === 201 || registerRes.status === 200) {
    // Login to get token
    const loginRes = http.post(`${BASE_URL}/api/v1/auth/login`, JSON.stringify({
      email: testUser.email,
      password: testUser.password,
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
    
    if (loginRes.status === 200) {
      const token = loginRes.json('access_token');
      return { token };
    }
  }
  
  return { token: '' };
}

export default function(data) {
  const headers = {
    'Content-Type': 'application/json',
    'Authorization': data.token ? `Bearer ${data.token}` : '',
  };

  // Test 1: Health check
  let res = http.get(`${BASE_URL}/health`);
  check(res, {
    'health check status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);

  // Test 2: Get mentors list
  res = http.get(`${BASE_URL}/api/v1/mentors`, { headers });
  check(res, {
    'mentors list status is 200': (r) => r.status === 200,
    'mentors list has data': (r) => r.json('data') !== undefined,
  }) || errorRate.add(1);
  
  sleep(1);

  // Test 3: Get courses
  res = http.get(`${BASE_URL}/api/v1/courses`, { headers });
  check(res, {
    'courses list status is 200': (r) => r.status === 200,
  }) || errorRate.add(1);
  
  sleep(1);

  // Test 4: Get user profile (authenticated)
  if (data.token) {
    res = http.get(`${BASE_URL}/api/v1/users/me`, { headers });
    check(res, {
      'user profile status is 200': (r) => r.status === 200,
      'user profile has email': (r) => r.json('email') !== undefined,
    }) || errorRate.add(1);
  }
  
  sleep(2);
}

export function teardown(data) {
  // Cleanup: delete test user if needed
  // Note: Implement cleanup endpoint in your API
}
