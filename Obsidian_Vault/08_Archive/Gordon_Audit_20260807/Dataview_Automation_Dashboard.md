# Automation Dashboard

```dataview
TABLE
  timestamp AS "Last Updated",
  type AS "Type",
  severity AS "Severity",
  message AS "Message"
FROM "10_Skills_Library/05_Operations"
WHERE file.name = "automation_status.json"
SORT timestamp DESC
LIMIT 50
```
