---
title: "{{ replace .File.ContentBaseName "-" " " | title }}"
date: {{ .Date }}
draft: true
# Search-result snippet, 70-160 characters. Say what the reader gets, not "In this post…"
description: ""
# One category: guides, recommended, news or personal
categories:
  - ""
# 2-4 tags from content/tags/ (raspberry-pi, ios, mac, apps, maker, education,
# open-source, sysadmin, networking, home-automation, productivity, wellbeing)
tags:
  - ""
# Featured image: put the file in this post's images/ folder and give the filename here
coverImage: ""
# Longer post? Put {{ "{{< toc >}}" }} on its own line after the intro for an automatic table of contents
---

Intro paragraph – the first part becomes the summary on the home page and in the RSS feed.

<!--more-->

![Alt text](images/example.webp)

<!-- SEO: describe each image in the [alt text], link to a related post or two, use ## for section headings. ./test.sh checks all of this. -->
