---
title: "From WordPress to Hugo - because of and thanks to AI"
date: 2026-10-25T12:57:31Z
draft: false
# Search-result snippet, 70-160 characters. Say what the reader gets, not "In this post…"
description: "How the rapid improvements in AI have both enabled and necessitated my move from WordPress to Hugo"
# One category: guides, recommended, news or personal
categories:
  - "news"
# 2-4 tags from content/tags/ (raspberry-pi, ios, mac, apps, maker, education,
# open-source, sysadmin, networking, home-automation, productivity, wellbeing)
tags:
  - "sysadmin"
  - "artificial-intelligence"
# Featured image: put the file in this post's images/ folder and give the filename here
coverImage: "images/wordpress-to-hugo.png"
# Longer post? Put {{< toc >}} on its own line after the intro for an automatic table of contents
---

I have had a project on my to-do list for months now – to move my blog from WordPress to Hugo. Part of it was just the novelty of a new system, tinkering for the sake of tinkering. Part of it was to have a faster, more secure site. And watching endless videos about how Obsidian as a second brain is the best thing since sliced bread!

<!--more-->

All of these factors were nudging me towards the project, but any time I sat down to look at it and try it out, I just felt overwhelmed by the scale of it.

* Trying to keep URLs intact for SEO. 
* Writing a post is not as WYSIWYG as in WordPress. 
* How should I publish the site? 
* Do I have to learn Git and GitHub Actions? 
* How do I get search to work?

Every time, the friction was just too much, and I left another half-finished migration folder on my computer. Four attempts, and I gave up on each one.

However, this week we saw [AI help uncover two fairly major flaws in PHP](https://www.bbc.co.uk/news/articles/c3qjnwye0ep5o) (the language that WordPress is written in, along with about 70% of all websites!). The patches came out pretty quickly, and updating was reasonably straightforward for me. But it was just another little nudge to look at moving away from WordPress.

And now that AI coding tools are so much better, I figured they could help me get it over the line.

So this weekend, I sat down with Claude, pointed it at my long-forgotten Hugo folder, and we got to work.

I find it fascinating that the dangerous side of these tools is the reason I felt I had to move away from PHP, and yet the upsides are what eased the transition. Double-edged sword indeed!

So now my site is running on Hugo. Written in simple Markdown files, then pushed to GitHub with a script that Claude made for me. That script also checks for missing links and a few SEO quick wins, and runs a GitHub Action to then push the site to my hosting provider.

I can draft posts and test them locally, making sure everything looks right before hitting the publish script. And if anything goes wrong, I have the ability to easily revert.

No more WordPress updates, plugin updates or PHP monitoring, and the site loads faster than ever.

I am looking forward to finding other areas where AI can assist me with the drudgery of tasks I have been putting off. I have been listening to the [Intentional AI podcast](https://relay.fm/intentional) with David Sparks and Chris Bailey, and they say that AI should be used for the "donkey work" to free you up to be creative.

Maybe you can find some areas in your life where it can help in small ways too.
