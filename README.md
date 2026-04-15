<!-- Keywords for search engines: Harry Potter Goblet of Fire save editor, HP Goblet of Fire PC shield unlocker, Harry Potter 4 PC save mod, Triwizard Shield cheat, Harry Potter and the Goblet of Fire 2005 PC game mod, HPGOF save file editor, Harry Potter Goblet of Fire all shields, Harry Potter Goblet of Fire 100% completion, EA Harry Potter PC save tool, Harry Potter Goblet of Fire PC trainer, Harry Potter Goblet of Fire unlock all levels, HP4 PC save hack, Harry Potter 2005 PC game cheat tool -->

<div align="center">

# ⚡ Harry Potter and the Goblet of Fire — Save Editor

### Unlock all 39 Triwizard Shields instantly

**PC · 2005 · EA Games**

[![Platform](https://img.shields.io/badge/platform-Windows-blue?logo=windows&logoColor=white)](#requirements)
[![Release](https://img.shields.io/github/v/release/tomigorn/harry-potter-goblet-of-fire-shield-unlocker?label=download&color=green)](../../releases/latest)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-yellow)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-3776ab?logo=python&logoColor=white)](https://www.python.org/downloads/)

No hex editing. No coding. No replaying levels. Just download, click, and play.

<br>

[**Download**](../../releases/latest) · [Quick Start](#-quick-start) · [Features](#-features) · [FAQ](#-faq)

</div>

<br>

This is a free, community-driven Windows GUI tool that edits the save file for **Harry Potter and the Goblet of Fire** (2005, EA Games, PC) — the fourth game in the Harry Potter PC series. The game locks later levels behind Triwizard Shield collectibles scattered across 10 levels. This tool lets you max them all out in one click so you can skip the grind and play the content you want.

> **How it works in 10 seconds:** Download the `.exe` → run it → click <kbd>MAX ALL SHIELDS</kbd> → click <kbd>SAVE</kbd> → launch the game. Done.

---

## 🚀 Quick Start

**No programming needed.** You don't need Python, coding knowledge, or any technical skills. Just download one file and run it.

> [!IMPORTANT]
> You must have launched the game **at least once** so that it creates a save file. If you've never played, start the game, get past the first cutscene, then quit. Also make sure the game is **closed** before using the editor — don't edit while the game is running.

1. Go to the [**Releases page**](../../releases/latest)
2. Download **`HPGOF_SaveEditor.exe`**
3. Run it from wherever you downloaded it — your Desktop, Downloads folder, anywhere. It does **not** need to be placed in the game folder, the save folder, or any specific location. Just double-click it.
4. The editor automatically finds your save file and loads it
5. Click <kbd>⚡ MAX ALL SHIELDS</kbd>
6. Click <kbd>💾 SAVE</kbd>
7. Launch the game — all shields are now unlocked

That's it. You can close the editor and never open it again. You can also delete the `.exe` afterward — it's a standalone tool, not something that needs to stay installed.

> [!TIP]
> Every time you click Save, the editor creates a **timestamped backup** of your save file right next to the original (in the same folder). The backups look like `HPGOF.backup_20260415_211859`. You can restore any backup from within the editor, so there is zero risk of losing your progress.

---

## 📂 Where Does Everything Live?

### Save file

The game stores your save at:

```
C:\Users\<YourName>\AppData\Local\Electronic Arts\Harry Potter and the Goblet of Fire\HPGOF\HPGOF
```

> [!NOTE]
> The save file is called `HPGOF` with **no file extension** — no `.sav`, no `.dat`, nothing. It sits inside a folder also called `HPGOF`. So you're looking for a **file** named `HPGOF` inside a **folder** named `HPGOF`. Yes, it's confusing — the editor handles this for you automatically.

The `AppData\Local` folder is hidden by default in Windows. You don't need to navigate there yourself — the editor finds it automatically. If it can't (e.g., you installed the game to a non-standard location), click <kbd>📁 Open File</kbd> in the editor to browse to it manually.

### Backups

Backups are saved in the **same folder** as your save file:

```
C:\Users\<YourName>\AppData\Local\...\HPGOF\HPGOF.backup_<timestamp>
```

### Game installation

The game itself is typically installed to:

```
C:\Program Files (x86)\Electronic Arts\Harry Potter and the Goblet of Fire\
```

The editor does not need to know where the game is installed — it only reads and writes the save file.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Max all shields** | Sets every level to full Triwizard Shields — 39 total across 10 levels |
| **Per-level editing** | View and change Available, Collected, and Big Shield counts for each level |
| **Mini-shield generators** | Edit secondary shield generator tracking values (advanced) |
| **SaveFlags** | Edit the 8 game progression bitmask flags — cutscenes, pickups, quests (advanced) |
| **Automatic backups** | Timestamped backup created every time you save, right next to your save file |
| **Restore from backup** | Revert to any previous save from within the editor |
| **Portable** | Single `.exe`, no installation, no dependencies |

<details>
<summary><strong>All 10 Levels &amp; Shield Counts</strong></summary>

<br>

| # | Level | Shields |
|---|-------|:-------:|
| 1 | Defense Against the Dark Arts | 1 |
| 2 | Hogwarts Exterior | 8 |
| 3 | Moody's Challenges | 0 |
| 4 | Forbidden Forest | 8 |
| 5 | Triwizard Task 1 | 3 |
| 6 | Prefects' Bathroom | 8 |
| 7 | Herbology | 8 |
| 8 | Triwizard Task 2 | 3 |
| 9 | Triwizard Task 3 | 0 |
| 10 | Voldemort | 0 |
| | **Total** | **39** |

</details>

---

## 🔧 Requirements

| Use case | What you need |
|----------|---------------|
| **Run the `.exe`** (recommended) | Windows 7, 8, 10, or 11 — nothing else |
| **Run from source** | Windows + [Python 3.10+](https://www.python.org/downloads/) (no extra packages) |
| **Build the `.exe` yourself** | All of the above + [PyInstaller](https://pypi.org/project/pyinstaller/) |

<details>
<summary><strong>Run from source</strong></summary>

```bash
python hpgof_save_editor.py
```

No extra packages needed — only Python's built-in `tkinter`, `struct`, and `shutil`.

</details>

<details>
<summary><strong>Build the .exe yourself</strong></summary>

```bash
pip install pyinstaller
pyinstaller HPGOF_SaveEditor.spec
```

The standalone `.exe` will appear in the `dist/` folder.

</details>

---

## ❓ FAQ

<details>
<summary><strong>Will this break my save?</strong></summary>

No. The editor creates an automatic backup every time you save. If anything goes wrong, you can restore from within the editor.

</details>

<details>
<summary><strong>Does this work on the PS2/console version?</strong></summary>

No. This is for the **Windows PC version only** (2005, EA Games).

</details>

<details>
<summary><strong>The editor can't find my save file</strong></summary>

Make sure you have launched the game at least once — the save file is only created after your first play session. If you have played before, click <kbd>📁 Open File</kbd> and browse to your save file manually. See [Where Does Everything Live?](#-where-does-everything-live) for the expected path.

</details>

<details>
<summary><strong>Should the game be closed while I use the editor?</strong></summary>

Yes. Close the game before editing. If the game is running, it may overwrite your changes the next time it saves.

</details>

<details>
<summary><strong>Can I edit individual levels instead of maxing everything?</strong></summary>

Yes. The editor shows per-level fields that you can change to any value you want.

</details>

<details>
<summary><strong>Is this a virus?</strong></summary>

No. The source code is right here in this repository — you can read every line. If you don't trust the `.exe`, you can run it from source with Python or build the `.exe` yourself. Windows SmartScreen may show a warning because the `.exe` is not code-signed; click "More info" → "Run anyway".

</details>

---

<details>
<summary><h2>🔬 How It Works (Technical Details)</h2></summary>

### How the save format was reverse-engineered

There is very little documentation about this game's save format online. The binary structure was figured out by opening the save file in a hex editor, changing shield counts in-game, and comparing the before/after bytes to identify which offsets correspond to which values. The [GameFAQs walkthrough by spitfox](https://gamefaqs.gamespot.com/ps2/927365-harry-potter-and-the-goblet-of-fire/faqs/40319) (archived in this repo as `gamefaqs_walkthrough_archive.txt`) was used as a reference for level names and expected shield counts per level.

### Save file format

The save file is a binary blob with a `20CM` magic header (4 bytes: `0x32 0x30 0x43 0x4D`). All numeric values are stored as **little-endian unsigned 32-bit integers**.

Shield data lives in a `GlobalData` section as key-value pairs at fixed byte offsets. Each of the 10 levels has a group of three values:

| Field | Meaning |
|-------|---------|
| **Available** | How many shield generators exist in the level |
| **Collected** | How many generators the player has picked up |
| **Big Shields** | The converted total shown on the level-select screen |

The sum of all per-level Big Shield counts is stored redundantly in two places: a header field at offset `0xC0` and a secondary counter at offset `0x806`. The editor updates both of these so the save file stays internally consistent.

There is also a secondary set of per-level tracking values (mini-shield generators) at earlier offsets, and 8 × 32-bit bitmask flags (`SaveFlags`) starting at offset `0x0C42` that track game progression events. Setting all flag bits to `0xFFFFFFFF` marks everything as completed.

The editor reads the entire file into memory, modifies the relevant bytes, and writes it back. No data outside the known offsets is touched.

</details>

---

## About

**Harry Potter and the Goblet of Fire** (2005, EA Games) is the fourth game in the Harry Potter PC series. Players collect Triwizard Shields across 10 levels to unlock later stages of the game. This save editor removes that grind by writing the maximum shield values directly into the save file's binary data.

The save format was reverse-engineered from scratch for this project — no existing documentation or tools for this game's save format were found online.

This project is not affiliated with or endorsed by Electronic Arts, Warner Bros., or the Harry Potter franchise.

### License

This project is licensed under [CC BY-NC-SA 4.0](LICENSE) — free to use, share, and modify for non-commercial purposes. See [LICENSE](LICENSE) for details.

The file `gamefaqs_walkthrough_archive.txt` is not covered by this license — it is copyrighted by its original author (spitfox) and is archived here under fair use for non-commercial reference and preservation only. It will be removed upon request by the rights holder.

### Credits

- Save format reverse engineering and editor code: this project's author
- Level names and shield counts reference: [FAQ/Walkthrough by spitfox on GameFAQs](https://gamefaqs.gamespot.com/ps2/927365-harry-potter-and-the-goblet-of-fire/faqs/40319) (archived in this repo as `gamefaqs_walkthrough_archive.txt` in case the original goes offline)
