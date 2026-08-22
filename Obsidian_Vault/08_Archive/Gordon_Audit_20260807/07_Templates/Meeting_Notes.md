---
date: <% tp.date.now() %>
tags: [meeting, notes]
---

# Meeting Notes — <% tp.file.title %>

**Date:** <% tp.date.now() %>  
**Attendees:** <% tp.user.prompt("Attendees:", "") %>  
**Location:** <% tp.user.prompt("Location:", "") %>

## Agenda
1. <% tp.user.prompt("Agenda item 1:", "") %>
2. <% tp.user.prompt("Agenda item 2:", "") %>
3. <% tp.user.prompt("Agenda item 3:", "") %>

## Discussion
<% tp.user.prompt("Discussion notes:", "") %>

## Action Items
- [ ] <% tp.user.prompt("Action 1:", "") %> — Owner: <% tp.user.prompt("Owner:", "") %>
- [ ] <% tp.user.prompt("Action 2:", "") %> — Owner: <% tp.user.prompt("Owner:", "") %>

## Next Meeting
<% tp.user.prompt("Next meeting date:", "") %>
