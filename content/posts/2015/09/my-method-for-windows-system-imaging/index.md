---
title: "My method for Windows system imaging"
date: 2015-09-20
categories: 
  - "guides"
tags: 
  - "sysadmin"
aliases:
  - "/my-method-for-windows-system-imaging/"
---

In our school we use FOG as our imaging system [as I have mentioned before.](https://intelligentdithering.com/open-source-pc-imaging-with-fog/)

I like to keep a default image with an up to date installation of Windows 7 Pro, Office 2010 and other essential tools and utilities on it. Most of our smaller bits of software we push out to the machines using Group Policy.

The method I have found that works the best for us is to use [VirtualBox](https://www.virtualbox.org/) to make a virtual machine with Windows 7 installed. The key to making this work with imaging systems is using Sysprep to strip out key machine information from the image so that it can be deployed on many makes and models of PC.

When you install Windows 7 Pro at first, you will want to get the system into [“Audit mode”](https://technet.microsoft.com/en-us/library/cc722413%28v=ws.10%29.aspx). You do this by pressing Ctrl - Shift - F3 at the Windows Welcome screen during installation. This puts your system into a special mode where you have admin rights with no login details required.

From here you install all the programs and tools you need, install all the Windows updates and security patches etc. Once you have a clean setup I recommend you take a Virtual Machine snapshot and name it accordingly. This will allow you to go back to this state easily, as the Sysprep utility can sometimes go wrong and you don’t want to have to go through the whole install and setup process by hand again!

Once a snapshot has been taken you will want to run Sysprep to prepare the image for capture with FOG or your preferred imaging tool. The VM will shutdown after you do this. I will write a separate post on setting up a file to run Sysprep with the appropriate settings soon.

With Sysprep complete and the VM shutdown, you would now tell FOG to upload an image from the machine on next boot. Make sure you have set the Virtual Machine to boot from network before starting it up so that FOG can boot it from PXE to take the image.

This setup will allow you to easily restore the “pre-Sysprep” snapshot in your VM, quickly update any tools and patches and take a new image to FOG.

I have found that this simple image will work on all of the machines in our network, with only a small handful needing a driver or two installed after the fact.

This allows us to focus on other work. If it would take longer than 30 minutes to troubleshoot the issue, we just wipe the machine and it is sorted. Also gives the machine a clear out and the user that “new install” feeling.

#### In summary[](#in-summary)

- Install Windows 7 in Audit mode on a Virtual Machine

- Install all updates and programs you want

- Set up shortcuts etc

- Take a snapshot of the VM in case of issues

- Run Sysprep to prepare it for upload to your imaging server

- Upload to imaging server

- Deploy to machines and profit
