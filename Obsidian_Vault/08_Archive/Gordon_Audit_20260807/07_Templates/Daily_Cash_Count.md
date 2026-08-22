---
date: <% tp.date.now() %>
tags: [cash, count, daily]
---

# Daily Cash Count — <% tp.file.title %>

**Date:** <% tp.date.now() %>  
**Shift:** <% tp.user.prompt("Shift:", "AM") %>  
**Counter:** <% tp.user.prompt("Counter:", "") %>

## Cash Breakdown
| Denomination | Count | Total |
|--------------|-------|-------|
| $100 | <% tp.user.prompt("100s:", "0") %> | $<% tp.user.prompt("100 total:", "0") %> |
| $50 | <% tp.user.prompt("50s:", "0") %> | $<% tp.user.prompt("50 total:", "0") %> |
| $20 | <% tp.user.prompt("20s:", "0") %> | $<% tp.user.prompt("20 total:", "0") %> |
| $10 | <% tp.user.prompt("10s:", "0") %> | $<% tp.user.prompt("10 total:", "0") %> |
| $5 | <% tp.user.prompt("5s:", "0") %> | $<% tp.user.prompt("5 total:", "0") %> |
| $1 | <% tp.user.prompt("1s:", "0") %> | $<% tp.user.prompt("1 total:", "0") %> |
| Coins | <% tp.user.prompt("Coins:", "0") %> | $<% tp.user.prompt("Coin total:", "0") %> |

## Card/Digital
- Card: $<% tp.user.prompt("Card total:", "0") %>
- Mobile: $<% tp.user.prompt("Mobile total:", "0") %>
- Check: $<% tp.user.prompt("Check total:", "0") %>

## Reconciliation
- Expected: $<% tp.user.prompt("Expected:", "0") %>
- Actual: $<% tp.user.prompt("Actual:", "0") %>
- Variance: $<% tp.user.prompt("Variance:", "0") %>

## Drop/Deposit
- Drop amount: $<% tp.user.prompt("Drop:", "0") %>
- Deposit slip #: <% tp.user.prompt("Deposit slip:", "") %>

## Manager Sign-Off
**Name:** ___________________  
**Date:** <% tp.date.now() %>  
**Signature:** ___________________
