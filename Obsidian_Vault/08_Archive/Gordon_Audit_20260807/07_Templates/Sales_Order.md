---
date: <% tp.date.now() %>
tags: [sales, order]
---

# Sales Order — <% tp.file.title %>

**Order #:** <% tp.user.prompt("Order number:", "") %>  
**Date:** <% tp.date.now() %>  
**Customer:** <% tp.user.prompt("Customer name:", "") %>  
**Status:** <% tp.user.prompt("Status:", "Pending") %>

## Items
| SKU | Product | Qty | Price | Total |
|-----|---------|-----|-------|-------|
| <% tp.user.prompt("SKU 1:", "") %> | <% tp.user.prompt("Product 1:", "") %> | <% tp.user.prompt("Qty 1:", "0") %> | $<% tp.user.prompt("Price 1:", "0") %> | $<% tp.user.prompt("Total 1:", "0") %> |

## Payment
- Method: <% tp.user.prompt("Payment method:", "") %>
- Status: <% tp.user.prompt("Payment status:", "") %>

## Shipping
- Address: <% tp.user.prompt("Shipping address:", "") %>
- Method: <% tp.user.prompt("Shipping method:", "") %>
- Tracking: <% tp.user.prompt("Tracking #:", "") %>

## Notes
<% tp.user.prompt("Notes:", "") %>
