# Generalized Steam Controller (2015) profile for Ren'Py visual novels

## Result

Use a legacy keyboard-and-mouse layout. Do not emit XInput or Steam Input API
actions: Our Red String's live app metadata reports no Steam Input API support,
and Valve warns that games which assume mouse and gamepad input cannot be used
simultaneously may glitch when both are emitted. Keep gyro disabled.

No importable VDF is included. The repository contains no VDF, the public
inventory returned no downloadable layout, the running Buddy reported no
connected controller, and Valve's documented local VDF workflow starts from a
Steam-generated autosave tied to an account/controller path. A hand-authored
file would therefore have no grounded schema/version/base and could not be
validated safely in this spike.

## Mapping

All outputs below are legacy mouse or keyboard outputs.

<!-- markdownlint-disable MD013 -->

| Steam Controller control | Output | Ren'Py action | Notes |
| --- | --- | --- | --- |
| Right trackpad | Mouse | Point at menus, choices, links | Trackball mode with moderate friction is a useful starting point. |
| Right trackpad click | Mouse 1 | Click, confirm, advance | Direct pointing/clicking path. |
| Right trigger, full pull | Mouse 1 | Advance or activate focused control | Comfortable repeated advance; do not add a gamepad output. |
| A | Enter | Confirm focused choice; dismiss/advance | Ren'Py's documented default `dismiss`/`button_select`. |
| B | Escape | Game menu / back | Also closes many modal screens. |
| Start | Escape | Redundant game menu / back | Keeps the menu action easy to find. |
| Left bumper | Page Up | Rollback | A title may disable or constrain rollback. |
| Right bumper | Page Down | Roll-forward | Works only after rollback and where the title permits it. |
| Left grip, hold | Left Ctrl | Hold-to-skip | Configure as a regular press/release, not Toggle or Turbo. |
| X | Tab | Toggle skip | Test unread-text and choice-stop behavior in the title. |
| Y | H | Hide/show the text window and UI | Ren'Py default is unshifted `H`. |
| Right grip | S | Screenshot | Ren'Py default is unshifted `S`; verify the title has not rebound it. |
| Left trackpad | Arrow keys as directional pad | Move choice/menu focus | Four-way, no overlap. |
| Left trackpad click | Enter | Select focused choice | Redundant with A. |
| Analog stick | Arrow keys | Alternate choice/menu navigation | Use digital arrow outputs, not a virtual joystick. |
| Gyro | None | Disabled | Avoid cursor drift and an unneeded second pointing source. |
| Left trigger | Unbound initially | Reserve | Suggested alternative: Mouse 1 for one-handed play. |
| Back/select | Unbound initially | Reserve | Suggested alternative: `H` or Escape if desired. |

<!-- markdownlint-enable MD013 -->

Keyboard outputs use scancodes and can be affected by the operating-system
keyboard layout. Validate `H`, `S`, and Tab on the target Windows setup.

## Why this shape

- Mouse 1 is the broadest Ren'Py activation/advance path, while Enter and arrow
  keys preserve reliable keyboard-only menu navigation.
- Page Up/Page Down, Ctrl, Tab, H, Escape, Enter, arrows, Mouse 1, and S match
  the documented Ren'Py 8.4.0 default keymap. Individual games can override
  them, and rollback can be disabled.
- Redundant click/advance and menu bindings reduce hand travel during long
  reading sessions.
- The layout never mixes emulated gamepad input with mouse input.

## Alternatives after on-device testing

- If repeated trigger clicks are tiring, change A from Enter to Space; Ren'Py
  also documents Space as a dismiss key.
- If the game consumes Page Down for another purpose, leave roll-forward
  unbound. It is convenience, not a required visual-novel action.
- If `S` is overridden, use Steam's locally configured screenshot chord and
  leave the right grip unbound. Do not assume the chord without testing it.
- For one-handed play, bind both triggers to Mouse 1 and move hold-to-skip to
  either grip.

## Steam UI creation and personal export

Steam's labels can differ slightly between Desktop and Big Picture modes, but
the safe local workflow is:

1. Connect the Steam Controller (2015), open Steam Library, and select **Our Red
   String**.
2. Open **Controller Layout** (the controller icon, or **Manage > Controller
   Layout**). Enable Steam Input for this controller if Steam presents that
   choice.
3. Open **Browse Configs/Layouts > Templates**, preview a keyboard-and-mouse
   template, and apply it as the editable base. Do not choose Community or a
   layout for a different physical controller.
4. Select **Edit Layout**. Configure Buttons, Triggers, Joysticks, and Trackpads
   according to the table above. Set **Gyro Behavior** to **None**.
5. Review the layout summary and confirm that every emitted action is a mouse
   or keyboard action; remove any inherited XInput/gamepad bindings.
6. Use the gear/options menu and choose **Export Layout** or **Save New Layout**,
   then save it as a **Personal** layout named `Ren'Py Visual Novel (Keyboard +
   Mouse)`. Do not select Share/Community or publish it.
7. Re-open **Browse Configs/Layouts > Personal** and confirm the saved layout is
   listed. This verifies a Steam-managed personal export; it is not evidence of
   a portable, validated VDF.

## Our Red String on-device checklist

1. Launch the game from Steam with the profile selected; verify prompts do not
   oscillate between controller and keyboard/mouse glyphs.
2. Move the pointer with the right trackpad; click buttons with pad click and
   advance dialogue with the right trigger.
3. Navigate a choice using the left pad or stick arrows, then select with A or
   left-pad click.
4. Open and close the game menu with B and Start.
5. After several lines, test Page Up rollback and Page Down roll-forward; note
   any scenes where the game deliberately blocks them.
6. Hold the left grip to skip, release it to stop, then test X as toggle skip.
   Confirm choices and unread text stop skipping as expected.
7. Toggle the UI with Y and take a screenshot with the right grip; verify the
   screenshot is actually written and that `S` has no title-specific conflict.
8. Leave the controller untouched for 30 seconds and confirm the cursor does
   not drift (gyro remains disabled).

## Primary references

- [Ren'Py: Customizing the Keymap](https://www.renpy.org/doc/html/keymap.html)
  documents the 8.4.0 default key bindings used above.
- [Ren'Py: Saving, Loading, and Rollback](https://www.renpy.org/doc/html/save_load_rollback.html)
  explains that rollback can be changed or blocked by a title.
- [Valve: General Concepts](https://partner.steamgames.com/doc/features/steam_controller/concepts?language=english)
  describes legacy mode and the mixed mouse/gamepad caveat.
- [Valve: Legacy Mode Bindings](https://partner.steamgames.com/doc/features/steam_controller/legacy_mode?language=english)
  documents mouse, keyboard, and XInput legacy outputs and keyboard scancodes.
- [Valve: Steam Controller (2015)](https://partner.steamgames.com/doc/features/steam_controller/device/steam_controller?language=english)
  documents the controller's trackpads, grips, stick, clicks, and gyro.
- [Valve: Browsing Configurations](https://partner.steamgames.com/doc/features/steam_controller/browse_configs?language=english)
  documents Personal, Community, Templates, export, and controller-type hiding.
- [Valve: Steam Input Gamepad Emulation best practices](https://partner.steamgames.com/doc/features/steam_controller/steam_input_gamepad_emulation_bestpractices?language=english)
  shows that local configuration VDFs are Steam-generated and account/controller
  path-specific in the documented developer workflow.
