# Textual-Window Changelog

## 0.3.0 - Dynamic windows update

- Breaking change: The `name` attribute is no longer required, the `id` attribute is now required instead. The window will automatically replace any underscores in the id with spaces to use for the display name (in titlebar, etc).
- Windows have a new 'mode' setting to choose between "temporary" and "permanent". In temporary mode, windows will be removed from the DOM and windowbar when closed (as a normal Desktop would). In permanent mode, the close button is removed and the window can only be minimized.
- Windows can now be added and removed from the DOM and the window bar and manager will update automatically.
- Added a new "Add window" button to the demo to demonstrate the dynamic windows feature.
- Added new "close" and "minimize" options to the WindowBar menus to reflect how these are now 2 different options.
- Added new buttons in the demo to hide the RichLog and to make the background transparent.
- Added new hotkey "ctrl-d" to windows for minimizing.
- Window switcher now toggles the minimize state of the currently focused window.
- Added a new icon argument for the window.
- Removed the footer from the demo because the transparency mode (ansi_color) messes it up for some reason (but nothing else, strangely).
- Replaced the windowbar system that built windows at start with a new dynamic system that can add and remove window buttons in real time.
- Replaced the manager worker that watched for _dom_ready on a loop to instead rely on `call_after_refresh` in a window's `on_mount` method.
- Windows now track the DOM ready themselves due to the above feature, and calculate their own max sizes and starting positions accordingly, and add themselves to the window bar (still through the manager) when they're ready.

## 0.2.3

- Moved all button symbols to a single dictionary to remove code duplication.
- Slightly modified the button rendering logic to remove whitespace, hopefully fixes a graphical glitching issue.

## 0.2.2

- Added 3 new methods:
  - `mount_in_window`
  - `mount_all_in_window`
  - `remove_children_in_window`
  
These 3 methods make it possible to change the widgets inside of a window after it has been created. They are bridge methods that connect to `mount`, `mount_all`, and `remove_children` in the content pane.

## 0.2.1

- Small fixes to documentation.
- Made the Window.calculate_starting_position and Window.calculate_max_size methods into private methods

## 0.2.0

Huge update with many improvements:

- Breaking change: Made the name argument for the window be mandatory.
- Built a window focus cycler screen. This will dynamically show which window had most recent focus using a Queue and works very similar to alt-tab in a normal desktop.
- Built a way to focus windows / tell which is focused.
- Disabled focusing for inner content pane (The vertical scroll). Now it passes through all the scrolling controls from the window to the vertical scroll while the window is focused. Overrode several `action_scroll` methods to do this.
- Replaced the lock button with a generic hamburger menu ☰, which now shows a list of callbacks which can be passed into the window as an argument.
- Add snap/lock state indicator for windows on the WindowBar.
- Make the resize button slightly larger.
- Restoring (unmaximizing) a window now restores to its previous size and location.
- Maximize symbol now changes to '_' symbol after maximizing.
- Added more help info to the demo.

## 0.1.2

- Fixed bug with double quotes containing double quotes (apparently allowed in Python >= 3.12)
- Changed Python required version to 3.10

## 0.1.0

- First public release
