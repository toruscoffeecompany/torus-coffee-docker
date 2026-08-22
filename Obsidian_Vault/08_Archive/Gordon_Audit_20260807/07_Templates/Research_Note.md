---
date: <% tp.date.now() %>
tags: [research, note]
---

# Research Note — <% tp.file.title %>

**Topic:** <% tp.user.prompt("Research topic:", "") %>  
**Source:** <% tp.user.prompt("Source:", "") %>  
**Date:** <% tp.date.now() %>

## Key Findings
<% tp.user.prompt("Findings:", "") %>

## Data/Statistics
<% tp.user.prompt("Data:", "") %>

## Conclusion
<% tp.user.prompt("Conclusion:", "") %>

## Next Steps
<% tp.user.prompt("Next steps:", "") %>
