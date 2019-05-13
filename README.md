# _**jikca**_

**A multiplayer interactive fiction game engine.**

> You are standing in an open `field` west of a white `house` with a boarded front `door`. There is as small, sad, empty `mailbox` here, its own door, and flag, having been removed through violent force at some point in the recent past. You are also surrounded by a strangely pressing crowd of 23 other `people`. Every one looks guilty.
>
> A deep `male voice` shouts over the ambient din, “Someone shot the `food`!”

1. [Introduction & Overview](#introduction--overview)
2. [Requirements](#requirements)
3. [Installation Instructions](#installation-instructions)

---

### Introduction & Overview

Jikca is a single- and multi-player interactive fiction framework. If you're thinking Zork or Colossal Cave Adventure,
but with more people racooning your loot, you're right on the mark. There are various forms of these, depending on core
functionality and focus, such as MUSH (Multi-User Shared Hallucination), MUD (Multi-User Dungeon), MUCK, MOO, etc. There
are so many, they're often collectively abbreviated as MU*.

_MC Frontalot's_ [It Is Pitch Dark](https://www.youtube.com/watch?v=4nigRT2KmCE) is the official project theme song.


### Requirements

Jikca has relatively minimal requirements, and some helper scripts to try to make setup easier. Unfortunately we can not automate the installation or preparation of everything. To wit, these are prerequisites to begin:

* **A Python 3 language interpreter.** The codebase is tested against [CPython](https://www.python.org/), the default or standard interpreter often pre-installed on many UNIX and UNIX-like systems, and [Pypy](https://pypy.org), an "optimizing" interpreter itself written in Python suitable for very large or complex worlds… universes… or multiverses.

* **A MongoDB database storage server.** This _must not_ be exposed to the internet. We always recommend running the latest version, but any version >= 4.0 should be sufficient to reliably persist a game world.


### Installation Instructions

We recommend installing the `jikca` service within a Python _virtual environment_, a form of light-weight container to help keep all of the source files organized together, and to not pollute the system-level installed set of packages.  (This also saves needing elevated administrative permissions.)

#### Creating and activating the runtime ("virtual") environment.

As a core feature of the Python 3 language, you can execute the following in a terminal to get set up:

1. First, change your current working directory to the desired location for your project environment to be stored within.
   
   ```sh
   mkdir ~/Projects
   cd ~/Projects
   ```  

2. Next, get Python to construct a new directory to contain the project, then populate it with a standard subdirectory structure and a "standard library" of Python code.
   
   ```sh
   python3 -m venv jikca
   ```

3. Change the working directory to the newly created environment, then _activate_ it so that Python will utilize it when invoked.
   
   ```sh
   cd jikca
   . bin/activate
   ```

#### Installing Jikca

There are several different scenarios under which you might be installing and running this application. TO facilitate only installing the minimal amount of additional code required, we have partitioned our third-party dependencies into tagged "extra" requirements.

1. Support a **local, single player experience**.
   
   ```sh
   pip install 'jikca[single]'
   ```

2. Only install the **client components**, not server or engine, so that you may easily connect to and participate on an instance running elsewhere.
   
   ```sh
   pip install 'jikca[client,interactive]'
   pip install 'jikca[client,web,http]'
   pip install 'jikca[client,web,https]'
   ```

3. Only install the bare minimum required to **host a running game world**, ignoring all but the most minimal game client concerns.
   
   ```sh
   pip install 'jikca[server]'
   ```
   
   The server tag offers additional customization based on the transport you wish to offer the game over. Add these as commas-separated additions after `server` and before `]`.
   
   * `http` — **HTTP**, the _Hyper-Text Transport Protocol_, a text-based protocol spoken over TCP generally defaulting to port 80 on public servers, as this is the default web browsers will use if none is specified. (**Note:** Requires administrative privileges to run on ports lower than 1024.)
   
   * `https` — **HTTPS**, HTTP over an SSL or TLS encrypted channel, spoken over TCP defaulting to port 443. Additionally allows selection of additional protocols, such as HTTP/2 (formerly SPDY), or our telnet-like MUSH/1.
   
   * `rest` — **Representative State Transfer**, a standardization of the use of HTTP for transfer and management of resources ("objects") grouped into collections ("containers").
   
   * `rpc` — **Remote Procedure Call** Support RPC-like interactive sessions over an HTTP or WebSocket transport.
   
   * `ws` — **WebSockets**, expose a telnet-like interface over a WebSocket tunnel through an HTTP protocol.
   
   * `ssh` — **Secure SHell**, an interactive terminal experience over an encrypted channel. Permits username/password (or key-based) authentication as part of the initial connection process; no need to "log in" after connecting.
   
   * `tcp` — **TCP**, the _Transport Control Protocol_, a low level socket (byte stream) transport.  Telnet.
