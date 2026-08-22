---
date: <% tp.date.now() %>
tags: [project, note]
---

# Project Note — <% tp.file.title %>

**Project:** <% tp.user.prompt("Project name:", "") %>  
**Status:** <% tp.user.prompt("Status:", "Planning") %>  
**Priority:** <% tp.user.prompt("Priority:", "Medium") %>  
**Due Date:** <% tp.user.prompt("Due date:", "") %>

## Description
<% tp.user.prompt("Description:", "") %>

## Tasks
- [ ] <% tp.user.prompt("Task 1:", "") %>
- [ ] <% tp.user.prompt("Task 2:", "") %>
- [ ] <% tp.user.prompt("Task 3:", "") %>

## Notes
<% tp.user.prompt("Notes:", "") %>
