// Mock API service for SIEM dashboard. Replace with real API calls to backend.

export async function fetchMetrics() {
  // Simulate network latency
  await new Promise((res) => setTimeout(res, 300));

  // Mocked SIEM metrics
  return {
    eventsPerMinute: 127,
    activeAlerts: 8,
    topAlerts: [
      { name: 'Suspicious Login', count: 5 },
      { name: 'Malware Detected', count: 2 },
      { name: 'Data Exfil', count: 1 },
    ],
    topSources: [
      { ip: '10.0.1.5', events: 43 },
      { ip: '172.16.0.3', events: 29 },
      { ip: '192.168.0.11', events: 18 },
    ],
    recentEvents: [
      { time: '14:22:10', source: '10.0.1.5', message: 'Failed SSH login' },
      { time: '14:21:43', source: '172.16.0.3', message: 'Malware signature match' },
      { time: '14:20:05', source: '192.168.0.11', message: 'Large file transfer' },
    ],
  };
}
