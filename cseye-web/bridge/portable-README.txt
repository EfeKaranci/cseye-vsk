CSEYE - portable local viewer
=============================

What it is
----------
A self-contained ETABS results viewer. It reads an already-analyzed ETABS
model through the CSI API and shows, per level, column base axial forces and
base reactions -- with step-through of staged-construction stages, a
"max - min" load-change view, background PDF underlays, measuring tools, and
PDF export.

Everything runs locally on this PC from this folder. There is nothing to
install and no administrator rights are required.


Requirements
------------
- Windows (64-bit).
- ETABS installed on this PC (ETABS 21, 22, or 23). CSEYE talks to ETABS
  through its API, so the results come from your own ETABS install.
- A modern browser (Edge or Chrome).

A bundled Python runtime is included in the "python" folder -- you do NOT need
Python installed.


How to run
----------
1. Open ETABS and open (and run/unlock) the model you want to view.
2. Double-click  "Start CSEYE.bat".
   A console window opens and, after a few seconds, a browser tab opens at
   http://127.0.0.1:8766/
3. In the page, click  "Attach open model".  CSEYE reads the currently open
   ETABS model. Pick a level on the left and a result (load case or
   combination) up top.
4. To stop CSEYE, close the console window (or press Ctrl+C in it).

If the browser tab does not open by itself, just browse to
http://127.0.0.1:8766/ manually while the console window is running.


Notes
-----
- The first time you attach, ETABS may take 15-30 seconds while CSEYE reads
  the geometry. Larger models take longer.
- "Attach open model" is the simplest path and needs no configuration. The
  "Models" browser (to open a model file directly) scans your user folder by
  default; you can point it elsewhere -- see "Advanced" below.
- Cloud "Publish" (sharing a read-only web link) is intentionally DISABLED in
  this shared copy, so no account keys are included. All local features --
  view, step-through, max-min, measure, background PDFs, PDF export -- work
  normally.
- Windows may show a SmartScreen prompt the first time ("Windows protected
  your PC") because the .bat is not code-signed. Click "More info" ->
  "Run anyway". This does not require admin rights.
- You can move or copy this whole folder anywhere (Desktop, a USB stick, a
  network drive). It carries its own Python.


Advanced (optional)
-------------------
- To change the model-browser search folders, create a file named ".env"
  inside  app\bridge\  containing, for example:
      CSEYE_ROOTS=C:\Projects;D:\ETABS
  (separate multiple folders with semicolons). Restart CSEYE afterward.
- To change the port, add  CSEYE_PORT=8770  to that same .env file.
