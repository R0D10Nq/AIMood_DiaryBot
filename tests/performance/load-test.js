import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const apiResponseTime = new Trend('api_response_time');

// Test configuration
export const options = {
  stages: [
    { duration: '2m', target: 10 }, // Ramp up to 10 users
    { duration: '5m', target: 10 }, // Stay at 10 users
    { duration: '2m', target: 20 }, // Ramp up to 20 users
    { duration: '5m', target: 20 }, // Stay at 20 users
    { duration: '2m', target: 0 },  // Ramp down to 0 users
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'], // 95% of requests should be below 500ms
    http_req_failed: ['rate<0.1'],    // Error rate should be less than 10%
    errors: ['rate<0.1'],             // Custom error rate
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';

// Test data
const testUser = {
  telegram_id: Math.floor(Math.random() * 1000000),
  username: `testuser_${Math.floor(Math.random() * 1000)}`,
  first_name: 'Test',
  last_name: 'User'
};

let userId;

export function setup() {
  // Create test user
  const createUserResponse = http.post(`${BASE_URL}/api/users/`, JSON.stringify(testUser), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  if (createUserResponse.status === 201) {
    const user = JSON.parse(createUserResponse.body);
    console.log(`Created test user with ID: ${user.id}`);
    return { userId: user.id };
  } else {
    console.error('Failed to create test user');
    return { userId: null };
  }
}

export default function(data) {
  if (!data.userId) {
    console.error('No user ID available for testing');
    return;
  }

  // Test 1: Health check
  testHealthCheck();
  
  // Test 2: Get user
  testGetUser(data.userId);
  
  // Test 3: Create mood entry
  testCreateMoodEntry(data.userId);
  
  // Test 4: Get mood entries
  testGetMoodEntries(data.userId);
  
  // Test 5: Get analytics
  testGetAnalytics(data.userId);
  
  sleep(1);
}

function testHealthCheck() {
  const response = http.get(`${BASE_URL}/health`);
  
  const success = check(response, {
    'health check status is 200': (r) => r.status === 200,
    'health check response time < 200ms': (r) => r.timings.duration < 200,
  });
  
  errorRate.add(!success);
  apiResponseTime.add(response.timings.duration);
}

function testGetUser(userId) {
  const response = http.get(`${BASE_URL}/api/users/${userId}`);
  
  const success = check(response, {
    'get user status is 200': (r) => r.status === 200,
    'get user response time < 300ms': (r) => r.timings.duration < 300,
    'get user has valid data': (r) => {
      try {
        const user = JSON.parse(r.body);
        return user.id === userId;
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!success);
  apiResponseTime.add(response.timings.duration);
}

function testCreateMoodEntry(userId) {
  const moodEntry = {
    user_id: userId,
    mood_score: Math.floor(Math.random() * 10) + 1,
    note: `Test mood entry ${Date.now()}`,
    emotions: ['радость', 'спокойствие'],
    activities: ['работа', 'отдых'],
    energy_level: Math.floor(Math.random() * 10) + 1,
    stress_level: Math.floor(Math.random() * 10) + 1,
    entry_date: new Date().toISOString()
  };
  
  const response = http.post(`${BASE_URL}/api/mood-entries/`, JSON.stringify(moodEntry), {
    headers: { 'Content-Type': 'application/json' },
  });
  
  const success = check(response, {
    'create mood entry status is 201': (r) => r.status === 201,
    'create mood entry response time < 500ms': (r) => r.timings.duration < 500,
    'create mood entry has valid response': (r) => {
      try {
        const entry = JSON.parse(r.body);
        return entry.id && entry.user_id === userId;
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!success);
  apiResponseTime.add(response.timings.duration);
}

function testGetMoodEntries(userId) {
  const response = http.get(`${BASE_URL}/api/mood-entries/?user_id=${userId}&limit=10`);
  
  const success = check(response, {
    'get mood entries status is 200': (r) => r.status === 200,
    'get mood entries response time < 400ms': (r) => r.timings.duration < 400,
    'get mood entries has valid structure': (r) => {
      try {
        const data = JSON.parse(r.body);
        return Array.isArray(data.entries);
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!success);
  apiResponseTime.add(response.timings.duration);
}

function testGetAnalytics(userId) {
  const response = http.get(`${BASE_URL}/api/analytics/mood-trends?user_id=${userId}&period=week`);
  
  const success = check(response, {
    'get analytics status is 200': (r) => r.status === 200,
    'get analytics response time < 1000ms': (r) => r.timings.duration < 1000,
    'get analytics has valid structure': (r) => {
      try {
        const data = JSON.parse(r.body);
        return data.period && Array.isArray(data.mood_trend);
      } catch (e) {
        return false;
      }
    },
  });
  
  errorRate.add(!success);
  apiResponseTime.add(response.timings.duration);
}

export function teardown(data) {
  if (data.userId) {
    // Clean up test user (if delete endpoint exists)
    const response = http.del(`${BASE_URL}/api/users/${data.userId}`);
    console.log(`Cleanup: ${response.status === 204 ? 'Success' : 'Failed'}`);
  }
}

export function handleSummary(data) {
  return {
    'performance-report.html': htmlReport(data),
    'performance-summary.json': JSON.stringify(data),
  };
}

function htmlReport(data) {
  const date = new Date().toISOString();
  return `
<!DOCTYPE html>
<html>
<head>
    <title>AI Mood Diary Bot - Performance Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .metric { margin: 10px 0; padding: 10px; border-left: 4px solid #007cba; }
        .passed { border-left-color: #28a745; }
        .failed { border-left-color: #dc3545; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f4f4f4; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 AI Mood Diary Bot - Performance Test Report</h1>
        <p><strong>Test Date:</strong> ${date}</p>
        <p><strong>Duration:</strong> ${Math.round(data.state.testRunDurationMs / 1000)}s</p>
        <p><strong>Total Requests:</strong> ${data.metrics.http_reqs.values.count}</p>
    </div>

    <h2>📊 Key Metrics</h2>
    
    <div class="metric ${data.metrics.http_req_duration.values.p95 < 500 ? 'passed' : 'failed'}">
        <strong>95th Percentile Response Time:</strong> ${Math.round(data.metrics.http_req_duration.values.p95)}ms
        (Target: < 500ms)
    </div>
    
    <div class="metric ${data.metrics.http_req_failed.values.rate < 0.1 ? 'passed' : 'failed'}">
        <strong>Error Rate:</strong> ${(data.metrics.http_req_failed.values.rate * 100).toFixed(2)}%
        (Target: < 10%)
    </div>
    
    <div class="metric">
        <strong>Average Response Time:</strong> ${Math.round(data.metrics.http_req_duration.values.avg)}ms
    </div>
    
    <div class="metric">
        <strong>Requests per Second:</strong> ${Math.round(data.metrics.http_reqs.values.rate)}
    </div>

    <h2>📈 Detailed Metrics</h2>
    <table>
        <tr>
            <th>Metric</th>
            <th>Average</th>
            <th>Min</th>
            <th>Max</th>
            <th>90th %ile</th>
            <th>95th %ile</th>
        </tr>
        <tr>
            <td>HTTP Request Duration</td>
            <td>${Math.round(data.metrics.http_req_duration.values.avg)}ms</td>
            <td>${Math.round(data.metrics.http_req_duration.values.min)}ms</td>
            <td>${Math.round(data.metrics.http_req_duration.values.max)}ms</td>
            <td>${Math.round(data.metrics.http_req_duration.values.p90)}ms</td>
            <td>${Math.round(data.metrics.http_req_duration.values.p95)}ms</td>
        </tr>
        <tr>
            <td>API Response Time (Custom)</td>
            <td>${Math.round(data.metrics.api_response_time.values.avg)}ms</td>
            <td>${Math.round(data.metrics.api_response_time.values.min)}ms</td>
            <td>${Math.round(data.metrics.api_response_time.values.max)}ms</td>
            <td>${Math.round(data.metrics.api_response_time.values.p90)}ms</td>
            <td>${Math.round(data.metrics.api_response_time.values.p95)}ms</td>
        </tr>
    </table>

    <h2>🎯 Test Results</h2>
    <div class="metric ${data.metrics.http_req_failed.values.rate === 0 ? 'passed' : 'failed'}">
        <strong>Overall Result:</strong> ${data.metrics.http_req_failed.values.rate < 0.1 && data.metrics.http_req_duration.values.p95 < 500 ? '✅ PASSED' : '❌ FAILED'}
    </div>
</body>
</html>
  `;
}`;