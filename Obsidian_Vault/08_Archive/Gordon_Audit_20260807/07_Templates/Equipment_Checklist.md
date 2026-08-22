---
date: <% tp.date.now() %>
tags: [equipment, checklist]
---

# Equipment Checklist — <% tp.file.title %>

**Equipment:** <% tp.user.prompt("Equipment name:", "") %>  
**Location:** <% tp.user.prompt("Location:", "") %>  
**Inspector:** <% tp.user.prompt("Inspector:", "") %>

## Pre-Use Inspection
- [ ] Visual check
- [ ] Power/cord intact
- [ ] Clean/sanitized
- [ ] Calibration check

## Daily Maintenance
- [ ] <% tp.user.prompt("Task 1:", "") %>
- [ ] <% tp.user.prompt("Task 2:", "") %>
- [ ] <% tp.user.prompt("Task 3:", "") %>

## Weekly Maintenance
- [ ] <% tp.user.prompt("Weekly task 1:", "") %>
- [ ] <% tp.user.prompt("Weekly task 2:", "") %>

## Issues Found
<% tp.user.prompt("Issues:", "") %>

## Sign-Off
**Date:** <% tp.date.now() %>  
**Signature:** ___________________
