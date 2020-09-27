# VideoScape-3D Object Import Plugin for Blender #

This utility will allow Blender to load object files created for use with
VideoScape-3D, a rendering and animation package for the Amiga Computer.
This is known to work on Blender 2.8x and 2.90.

You can watch me clumsily piece this together in my [YouTube
video](https://youtu.be/fXoUjRVV7FM).


## Usage ##

This isn't an installable plugin *yet*.  Until then:

  * In Blender, click on the Scripting tab.
  * In the central editing pane, click the Open button.
  * Navigate to and open `import_vs3d.py`.  The plugin source code will
    appear.
  * At the top of the editing pane, click the Run button.

A file dialog will appear.  Navigate to your VideoScape object file and
select it.  The object should appear in your workspace.


## Support Notes ##

### File Formats ###

Both text and binary object formats are supported.  Error tolerance is meh;
please don't stress the parser.

Camera, motion, and scene files are not supported.


### Surface Materials ###

Surface colors and attributes are not yet supported.  (Leave a comment here
or on YouTube if you'd like to see that added.)


### Detail Polygons ###

As a creative compromise for the lack of texture mapping, VideoScape
supported "detail polygons" -- polygons that were rendered in specified
order after the parent polygon, thereby allowing you to draw over the parent
to add details.

It is unclear how to properly support or emulate detail polygons in Blender,
especially since they are not required to be bounded by, or even co-planar
with, the parent polygon (so it can't be faked with texture imagery).  As of
this writing, detail polygons are loaded as if they were "normal" polygons.
You may consequently end up with co-planar polygons that will display/render
inconsistently in Blender.


### 1- and 2-Vertex Polygons ###

VideoScape supported N-gons, where N could be as few as 1.  Single-point
"polygons" were used to create star fields (each star a single pixel).
2-point polygons were used to render straight lines (one pixel wide).

As of this writing, 1- and 2-point polygons are loaded by the plugin but, as
they are degenerate polygons with zero area, Blender will not display or
render them outside of edit mode.


### Linked Objects ###

Advanced VideoScape users have been known to use negative indices in
polygons to "reach back" into previously loaded object(s), linking their
meshes together and allowing animation of different pieces of the mesh to
achieve stretching/bending/deformation effects.  This technique was brittle,
and required precise knowledge of the load order and vertex layout of
objects.

This will not work, and almost certainly cannot be made to work.  As of this
writing, loading objects with negative polygon indices will cause the load
to abort.


## VideoScape History ##

In 1987, Aegis Software published VideoScape-3D, written by Allen Hastings
for the [Amiga Computer](https://en.wikipedia.org/wiki/Amiga).  It was one
of the very first 3D packages available for personal computers, Its low cost
made it quite popular, and gave many people their first exposure to 3D
rendering and animation.

Allen Hastings later joined NewTek to write [LightWave
3D](https://en.wikipedia.org/wiki/LightWave_3D), an explosively successful
rendering/animation suite that saw wide use in television and video games
throughout the 1990's and early 2000's.  He then went on to co-found
Luxology where he designed and wrote
[Modo](https://www.foundry.com/products/modo).  Luxology was acquired in
2012 by [Foundry Visionmongers](https://www.foundry.com/).

