# Sample Log Files for Testing

## Sample 1: Syslog with Failed Authentication (Brute Force)
Nov 22 10:30:45 server sshd[1234]: Failed password for admin from 192.168.1.100 port 54321 ssh2
Nov 22 10:30:47 server sshd[1235]: Failed password for admin from 192.168.1.100 port 54322 ssh2
Nov 22 10:30:49 server sshd[1236]: Failed password for admin from 192.168.1.100 port 54323 ssh2
Nov 22 10:30:51 server sshd[1237]: Failed password for admin from 192.168.1.100 port 54324 ssh2
Nov 22 10:30:53 server sshd[1238]: Failed password for admin from 192.168.1.100 port 54325 ssh2
Nov 22 10:30:55 server sshd[1239]: Failed password for admin from 192.168.1.100 port 54326 ssh2
Nov 22 10:31:00 server sshd[1240]: Accepted password for admin from 192.168.1.100 port 54327 ssh2

## Sample 2: Apache Logs with SQL Injection Attempt
192.168.1.50 - - [22/Nov/2025:10:30:45 +0000] "GET /search?q=test' UNION SELECT * FROM users-- HTTP/1.1" 200 1234
192.168.1.50 - - [22/Nov/2025:10:30:46 +0000] "GET /login.php?user=admin&pass=test HTTP/1.1" 200 512
192.168.1.50 - - [22/Nov/2025:10:30:47 +0000] "POST /api/data HTTP/1.1" 200 2048
192.168.1.75 - - [22/Nov/2025:10:30:48 +0000] "GET /admin/users?id=1 OR 1=1 HTTP/1.1" 403 256

## Sample 3: Firewall Logs
Nov 22 10:30:45 DENY TCP 192.168.1.100:12345 -> 10.0.0.1:22
Nov 22 10:30:46 DENY TCP 192.168.1.100:12346 -> 10.0.0.1:22
Nov 22 10:30:47 ACCEPT TCP 192.168.1.50:54321 -> 10.0.0.5:443
Nov 22 10:30:48 DENY UDP 192.168.1.200:5353 -> 8.8.8.8:53
Nov 22 10:30:49 ACCEPT TCP 10.0.0.10:443 -> 192.168.1.25:54123

## Sample 4: Windows Event Log
2025-11-22 10:30:45 ERROR Security 4625 An account failed to log on. Account Name: Administrator Source IP: 192.168.1.100
2025-11-22 10:30:47 WARNING Security 4740 User account was locked out. Account Name: admin
2025-11-22 10:30:50 INFO System 1074 System has been shutdown by user
2025-11-22 10:31:00 ERROR Application 1000 Application error: Faulting application name: malware.exe

## Sample 5: Mixed Severity Events
Nov 22 10:30:45 server kernel: [12345.678] CRITICAL: Out of memory
Nov 22 10:30:46 server httpd[5678]: ERROR: Failed to connect to database
Nov 22 10:30:47 server app[9012]: WARNING: Disk space low on /var
Nov 22 10:30:48 server cron[3456]: INFO: Job completed successfully
Nov 22 10:30:49 server nginx[7890]: NOTICE: Configuration reloaded

## Sample 6: XSS Attack Attempt
192.168.1.99 - - [22/Nov/2025:10:30:45 +0000] "GET /comment?text=<script>alert('XSS')</script> HTTP/1.1" 200 512
192.168.1.99 - - [22/Nov/2025:10:30:46 +0000] "POST /profile HTTP/1.1" 200 1024
192.168.1.99 - - [22/Nov/2025:10:30:47 +0000] "GET /search?q=<img src=x onerror=alert(1)> HTTP/1.1" 403 256

## How to Use These Samples

1. Copy any section above into a text file (e.g., `test_logs.log`)
2. Go to http://localhost:8000/logs/
3. Upload the file
4. Watch as the system:
   - Parses the logs
   - Detects threats (brute force, SQL injection, XSS)
   - Creates events
   - Generates alerts
   - Shows statistics

## Expected Results

### Sample 1 (Brute Force):
- 7 events created
- 1 alert: "Brute Force Detected" (6 failed logins from same IP)
- Severity: High

### Sample 2 (SQL Injection):
- 4 events created
- 2 alerts: "Malicious Pattern Detected" (SQL injection attempts)
- Severity: Critical

### Sample 3 (Firewall):
- 5 events created
- Category: Network
- Mixed severities based on DENY/ACCEPT

### Sample 4 (Windows Events):
- 4 events created
- Severity based on event level (ERROR/WARNING/INFO)
- Category: Authentication/System

### Sample 5 (Mixed):
- 5 events created
- Severities: Critical, High, Medium, Low, Info
- Demonstrates severity classification

### Sample 6 (XSS):
- 3 events created
- 2 alerts: "Malicious Pattern Detected" (XSS attempts)
- Severity: Critical
