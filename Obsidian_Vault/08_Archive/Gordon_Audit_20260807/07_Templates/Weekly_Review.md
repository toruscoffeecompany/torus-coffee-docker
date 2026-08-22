---
date: <% tp.date.now() %>
tags: [weekly, review]
---

# Weekly Review — Week <% tp.date.now("WW") %>

**Week of:** <% tp.date.now("YYYY-MM-DD") %>  
**Reviewer:** <% tp.user.prompt("Reviewer:", "") %>

## Sales Summary
- Revenue: $<% tp.user.prompt("Revenue:", "0") %>
- Orders: <% tp.user.prompt("Order count:", "0") %>
- Avg Order: $<% tp.user.prompt("Avg order:", "0") %>

## Inventory
<% tp.user.prompt("Inventory notes:", "") %>

## Issues
<% tp.user.prompt("Issues this week:", "") %>

## Next Week Goals
<% tp.user.prompt("Goals:", "") %>
