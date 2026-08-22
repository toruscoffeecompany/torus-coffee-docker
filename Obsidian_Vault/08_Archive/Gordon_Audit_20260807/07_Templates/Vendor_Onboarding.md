---
date: <% tp.date.now() %>
tags: [vendor, onboarding]
---

# Vendor Onboarding — <% tp.file.title %>

**Vendor Name:** <% tp.user.prompt("Vendor name:", "") %>  
**Contact:** <% tp.user.prompt("Contact person:", "") %>  
**Email:** <% tp.user.prompt("Email:", "") %>  
**Phone:** <% tp.user.prompt("Phone:", "") %>

## Business Details
- Products/Services: <% tp.user.prompt("Products/services:", "") %>
- Terms: <% tp.user.prompt("Terms:", "") %>
- Pricing: <% tp.user.prompt("Pricing structure:", "") %>

## Compliance Checklist
- [ ] W-9 Form received
- [ ] Insurance certificate received
- [ ] Vendor agreement signed
- [ ] Banking info added

## Notes
<% tp.user.prompt("Notes:", "") %>
