---
date: <% tp.date.now() %>
tags: [inventory, log]
---

# Inventory Log — <% tp.file.title %>

**Date:** <% tp.date.now() %>  
**Location:** <% tp.user.prompt("Location:", "") %>  
**Counter:** <% tp.user.prompt("Counter:", "") %>

## Items Counted
| SKU | Product | Qty | Notes |
|-----|---------|-----|-------|
| <% tp.user.prompt("SKU 1:", "") %> | <% tp.user.prompt("Product 1:", "") %> | <% tp.user.prompt("Qty 1:", "0") %> | <% tp.user.prompt("Notes 1:", "") %> |
| <% tp.user.prompt("SKU 2:", "") %> | <% tp.user.prompt("Product 2:", "") %> | <% tp.user.prompt("Qty 2:", "0") %> | <% tp.user.prompt("Notes 2:", "") %> |

## Discrepancies
<% tp.user.prompt("Discrepancies:", "") %>

## Action Items
<% tp.user.prompt("Actions:", "") %>
