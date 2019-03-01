# Harvest

## What is Harvest?

Harvest is a one-stop web application for torrent management - from ease of use to extreme scalability - everything is covered.

#### Project Goals

- Easy - create a system that's simple to set up. It should require minimal
  knowledge of Linux and command line usage to install and configure.
- Extendable - make it easy to add various functionality, some of it supplied
  as part of a core, other supplied and maintained by different people in the
  community.
- The 100K - enable transparent support and good performance even with 100K+
  torrents. Transparent means
  - You should be able to use the system just as fruitfully with 1000 torrents
    as with 100`000.
  - You shouldn't need to need anything super special to enable 100K. Minimal
    effort is OK (e.g. opening 10 ports instead of 1 for seeding), but
    otherwise everything should work out-of-the-box.
  - All features should work just as well with 100K as they do with 1K.
  - While technologically difficult, we'll do our best to not sack features
    just because they're difficult to implement for 100K.
- Modern - Harvest should be modern both for the users and the developers. The aim
  is to give a polished and user-friendly UI, while using new, but well
  established technologies for development.

#### Communcation and Team Work

For now, I'll be main driver of communication, development, design and handle
most functions. I'll try to keep this README current as the project develops.
In case other people can do a better job at something, I'm more than willing
to give up roles completely over to him/her.

I'll do my best to avoid the anti-pattern of [Design by committee](https://en.wikipedia.org/wiki/Design_by_committee).
To facilitate that, for now I'll be the gate keeper of all design,
functionality, features, decisions, etc. I'll do my best to list to everyone's
input and make the best decision, but don't be discouraged if your ideas
don't get adopted.

We will not be writing endless proposals, design documents, discussions, etc.
If you want to do something, take it on, write some code, make it nice and
clean and if it's the best proposal, we'll integrate it.

The current communication structure is just a first-pass, let me know if you
think something is broken or can be improved:
- Overall architecture, project areas and technical design will be placed in
  ARCHITECTURE.md. I'll keep this updated as I decide on approaches, integrate
  other people's work and the project develops.
- Specific issues, calls for help and async discussion will happen in
  individual GitHub issues.
- In-person communication and live discussion will happen in IRC in the #wm2
  channel in the Red IRC network.
  
As a start, head off to GitHub Projects ->
[Project Areas](https://github.com/harvest-project/harvest/projects/1).
Initial development will happen as a discussion in the individual areas with
each contributor creating one or more separate forks or even separate repos
containing POCs showcasing the solution of that problem. Once we reach a
conclusion how the problem is going to be solved, we'll work together to
integrate it into the main repo.

#### Technical Approaches and Design

Not 100% set in stone, but most of this will hold up. 

- Harvest will be an SPA web application using a REST API to handle front<->back
  end communication.
- The backend is in the latest version of Django (2 at the moment) and
  Python 3. Django REST Framework will be used to a certain extent to manage
  the API.
- The frontend is in React with state management TBD.
- Packaging will be done in multiple ways, probably involving at least manual
  set up, Docker, and a VM image.
- The torrenting backend is still a bit unknown. Current work in progress is
  a custom solution using libtorrent-rasterbar, but that's pending discussions
  with mods/admins at various sites. It's possible that the torrent backend
  will be pluggable, with a compatibility layer being offered to use
  Transmission instead of the built-in client.
- There will be a core module for supporting different trackers, managing
  torrents, storage and settings. Everything else will be provided as a set
  of built-in modules and the appropriate hooks for enabling adding plugins
  that provide functionality on top of that. How that's going to be achieved
  is fully TBD.
