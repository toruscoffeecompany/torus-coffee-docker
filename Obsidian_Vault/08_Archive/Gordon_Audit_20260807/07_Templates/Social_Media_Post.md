---
date: <% tp.date.now() %>
tags: [social, media, marketing]
---

# Social Media Post — <% tp.file.title %>

**Platform:** <% tp.user.prompt("Platform:", "Instagram") %>  
**Campaign:** <% tp.user.prompt("Campaign:", "") %>  
**Date:** <% tp.date.now() %>  
**Status:** <% tp.user.prompt("Status:", "Draft") %>

## Post Copy
<% tp.user.prompt("Post copy:", "") %>

## Hashtags
<% tp.user.prompt("Hashtags:", "") %>

## Visual Assets
- Image: <% tp.user.prompt("Image file:", "") %>
- Video: <% tp.user.prompt("Video file:", "") %>

## Engagement Goals
- Likes: <% tp.user.prompt("Like goal:", "0") %>
- Shares: <% tp.user.prompt("Share goal:", "0") %>
- Comments: <% tp.user.prompt("Comment goal:", "0") %>

## Post-Publish Tracking
- Posted: <% tp.user.prompt("Posted date:", "") %>
- Actual likes: <% tp.user.prompt("Actual likes:", "0") %>
- Actual shares: <% tp.user.prompt("Actual shares:", "0") %>
- Actual comments: <% tp.user.prompt("Actual comments:", "0") %>
