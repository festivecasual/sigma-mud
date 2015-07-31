# Fundamental Operation #

Conceptually, Sigma has a "world" structure (`world.py`), which contains both the structure of the MUD's environment (rooms, denizen prototypes, items, etc.) and the class definitions for these structures.

When Sigma starts up (the `main()` function in `sigma.py`), it calls routines within `importer.py` that import XML data into the system, calling on `world.py`'s functionality to load relevant XML nodes into data structures.

After the remainder of the system is loaded and started up, `network.py` begins to process network activity (new connections, typed data, and closed connections), passing confirmed commands to `command.py` for parsing and processing.

# Inside the Sigma Sandbox: `libsigma`, Handlers, and Tasks #

The `libsigma.py` module provides designer-facing interfaces to Sigma internals.  Sigma's fundamental source files may call on `libsigma` directly, or in many cases on lower-level functions not directly exposed to the designer.

Handlers and tasks are modular components loaded dynamically at run-time.  No Sigma internal depends on the existence or proper function of a handler or task.  As a design principle, Sigma pushes as much instruction load as possible into handlers and tasks, to ensure a high level of modularity.  This includes activities as fundamental as denizen instantiation.

Handlers are mapped to potential user input, specifying functions to be run upon receipt of a certain typed command.  Examples include **emote**, **say**, **west**, and **look**.  These handler functions will call on `libsigma` to interpret the current state of the system, communicate this state to the user, and/or manipulate the environment.

Tasks are run at a defined frequency but are unrelated to user input.  Therefore, tasks are the best choice for time-based functions such as denizen population and weather.

Task and handler functions run within a sandbox (`safe_mode()` within `libsigma.py`), meaning errors are trapped, reported on the server console (with the source file line number included), and are bypassed (rather than terminating program execution).  This prevents designer-generated code from causing fatal run-time errors.

# Object Persistence and Instantiation #

Sigma uses Python's built-in `pickle` module to serialize object data.  When denizens and items are instantiated by the designated task module, they are unpickled and placed in the appropriate location or container.