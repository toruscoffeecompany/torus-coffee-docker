---
date: <% tp.date.now() %>
tags: [customer, intake, crm]
---

# Customer Intake — <% tp.file.title %>

**Customer:** <% tp.user.prompt("Customer name:", "") %>  
**Email:** <% tp.user.prompt("Email:", "") %>  
**Phone:** <% tp.user.prompt("Phone:", "") %>

## Account Type
- [ ] Retail
- [ ] Wholesale
- [ ] Subscription

## Preferences
- Products: <% tp.user.prompt("Preferred products:", "") %>
- Flavors: <% tp.user.prompt("Favorite flavors:", "") %>
- Allergies: <% tp.user.prompt("Allergies:", "") %>

## Order Info
- First order: <% tp.user.prompt("First order date:", "") %>
- Referral: <% tp.user.prompt("Referral source:", "") %>

## CRM Notes
<% tp.user.prompt("CRM notes:", "") %>
