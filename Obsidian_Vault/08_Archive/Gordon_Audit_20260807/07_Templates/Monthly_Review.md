---
date: <% tp.date.now() %>
tags: [monthly, review]
---

# Monthly Review — <% tp.date.now("MMMM YYYY") %>

**Month:** <% tp.date.now("YYYY-MM") %>  
**Reviewer:** <% tp.user.prompt("Reviewer:", "") %>

## Financial Summary
- Revenue: $<% tp.user.prompt("Revenue:", "0") %>
- Expenses: $<% tp.user.prompt("Expenses:", "0") %>
- Profit: $<% tp.user.prompt("Profit:", "0") %>

## Key Metrics
<% tp.user.prompt("Key metrics:", "") %>

## Challenges
<% tp.user.prompt("Challenges:", "") %>

## Next Month Plan
<% tp.user.prompt("Plan:", "") %>
