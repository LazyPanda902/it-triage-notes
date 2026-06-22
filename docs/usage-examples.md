# Usage Examples

## Creating Notes

### Simple incident

```bash
$ it-triage add "Printer not responding" "HP LaserJet 5 on 3rd floor is offline"
Added note abc1234567
```

### Incident with category and severity

```bash
$ it-triage add "Database query timeout" "Production sales DB queries timing out after 10s" \
  --category monitoring --severity high
Added note def8901234
```

### Incident with tags

```bash
$ it-triage add "VPN connection drops" "Users report VPN disconnects every 5-10 minutes" \
  --category network --severity high --tags vpn,connectivity,urgent
Added note ghi5678901
```

## Listing and Filtering

### View all notes

```bash
$ it-triage list
[!] abc1234567  [open       ]  [monitoring ]  Database query timeout
[ ] jkl2345678  [open       ]  [network    ]  VPN connection drops
[X] mno9012345  [resolved   ]  [azure      ]  User account lockout
```

The badge indicates severity: `[X]` = critical, `[!]` = high, `[~]` = medium, `[ ]` = low.

### Filter by status

```bash
$ it-triage list --status open
[!] abc1234567  [open       ]  [monitoring ]  Database query timeout
[ ] jkl2345678  [open       ]  [network    ]  VPN connection drops
```

### Filter by severity

```bash
$ it-triage list --severity critical
[X] pqr3456789  [in-progress]  [security   ]  SQL injection vulnerability in login form
```

### Filter by category

```bash
$ it-triage list --category azure
[!] mno9012345  [resolved   ]  [azure      ]  User account lockout
[~] stu6789012  [open       ]  [azure      ]  MFA sign-in spam for service account
```

### Filter by tag

```bash
$ it-triage list --tag vpn
[ ] jkl2345678  [open       ]  [network    ]  VPN connection drops
[~] vwx0123456  [in-progress]  [network    ]  Configure new VPN gateway
```

## Showing Details

```bash
$ it-triage show abc1234567
  id       : abc1234567
  title    : Database query timeout
  category : monitoring
  severity : high
  status   : open
  tags     : database,performance,urgent
  created  : 2026-06-22T14:30:15Z
  updated  : 2026-06-22T14:30:15Z
  body     :
    Production sales DB queries timing out after 10s. Threshold alert
    triggered at 14:25 UTC. Database CPU at 85%, disk I/O at 90%.
    Restarting DB service now.
```

## Updating Notes

### Change status when working on incident

```bash
$ it-triage update abc1234567 --status in-progress
Updated note abc1234567
```

### Mark incident as resolved

```bash
$ it-triage update abc1234567 --status resolved --body "Restarted DB service at 14:45 UTC. Queries back to normal. Root cause: runaway index rebuild job."
Updated note abc1234567
```

### Update title and tags

```bash
$ it-triage update jkl2345678 --title "VPN gateway maintenance scheduled" --tags vpn,maintenance,scheduled
Updated note jkl2345678
```

### Update severity

```bash
$ it-triage update pqr3456789 --severity critical
Updated note pqr3456789
```

## Deleting Notes

```bash
$ it-triage delete abc1234567
Deleted note abc1234567
```

## Statistics

### Text format (default)

```bash
$ it-triage stats
Total notes : 12

By status:
  closed         1
  in-progress    3
  open           6
  resolved       2

By severity:
  critical       2
  high           4
  low            3
  medium         3

By category:
  azure          2
  hardware       1
  m365           2
  monitoring     4
  network        2
  other          1
  security       0
```

### JSON format

```bash
$ it-triage stats --json
{
  "total": 12,
  "by_status": {
    "open": 6,
    "in-progress": 3,
    "resolved": 2,
    "closed": 1
  },
  "by_severity": {
    "critical": 2,
    "high": 4,
    "medium": 3,
    "low": 3
  },
  "by_category": {
    "azure": 2,
    "m365": 2,
    "monitoring": 4,
    "network": 2,
    "hardware": 1,
    "security": 0,
    "other": 1
  }
}
```

## Using a Custom Database

```bash
$ it-triage --db /var/incidents/production.jsonl add "Load balancer error" "502 Bad Gateway"
Added note xyz0987654
```

List from custom database:

```bash
$ it-triage --db /var/incidents/production.jsonl list --status open
```

## Workflow Example: Daily Triage

```bash
# Morning: see what's open
it-triage list --status open

# During day: log incidents as they come in
it-triage add "Email server down" "Outlook Web Access returning 503" \
  --category m365 --severity critical --tags email,outage
it-triage add "Printer jam, room 212" "Paper jam in left tray" \
  --category hardware --severity low

# Update status as you work
it-triage update abc1234567 --status in-progress
it-triage update def5678901 --status resolved --body "Cleared jam, printer online"

# End of day: check progress
it-triage stats
```
