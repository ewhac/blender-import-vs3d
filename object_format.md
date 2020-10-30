# VideoScape-3D Object File Format #

VideoScape-3D object files are a collection of vertices, polygons, and
surface characteristics.  Each object file represents a single object/mesh;
there are no internal semantics or hierarchy.


## Text Format ##

Objects are described using human-readable numbers in a text file.  All
lines are terminated with a single newline character (`\n`).

Example file contents:

```
3DG1
8
0.866 -2.1213 -1.2247 
-0.866 -2.1213 1.2247 
-2.5981 0 0 
-0.866 0 -2.4495 
2.5981 0 0 
0.866 0 2.4495 
-0.866 2.1213 1.2247 
0.866 2.1213 -1.2247 
4 1 0 4 5 259
4 2 3 0 1 259
4 3 7 4 0 259
4 2 1 5 6 259
4 6 5 4 7 259
4 2 6 7 3 259
```

This particular example is a chrome cube rotated such that the X axis passes
through opposing corners.


### Overview ###

The general structure of a VS3D object file consists of the following parts:
  1. Header
  2. Vertex Count
  3. Vertices
  4. Polygons

All numbers appearing in the file are in base 10.

### Header ###

The first line contains exactly "3DG1", indicating this is a version 1
geometry file in text format.  There must not be leading or trailing
whitespace (save for the terminating newline).

### Vertex Count ###

The next line is the count of vertices appearing in the file (hereinafter
referred to as `vtx_count`).  Leading and trailing whitespace on the line
are ignored.

### Vertices ###

Each vertex occupies a single line, and consists of three floating point
numbers, separated by spaces, in XYZ order.  Leading and trailing whitespace
on the line are ignored.  The coordinate system is left-handed (positive-Y
up, positive-Z into the screen).

The number of vertices (lines) appearing is equal to `vtx_count`.

### Polygons ###

Immediately following the vertices are the polygons.  Each polygon occupies
a single line, and consists of a vertex count, vertex indices, and a color
code.  Each of these components is specified as an integer, separated by spaces.
Leading and trailing whitespace on the line is ignored.

The line is structured as follows:
  * **Vertex Count:** (`poly_vtx_count`) The first integer specifies the
    number of vertices in the polygon.
  * **Vertex Indices:** The following `poly_vtx_count` integers denote
    indices into the previously appearing list of vertices.  These indices
    are zero-based; thus an index of 0 refers to the first vertex in the
    list.  Indices that are out of range (i.e. `< 0` or `>= vtx_count`) have
    undefined behavior, including crashing the program.
  * **Color code/surface attributes:** The final integer specifies the
    color and surface attributes of the polygon (discussed in the next
    section).

Polygons continue until end-of-file.

Polygons must have one or more vertices.  One-vertex polygons are intended
to be rendered as a single pixel.  Two-vertex polygons are intended to be
rendered as single-pixel-wide lines.

Polygons are only visible from one side; polygons facing away from the
camera will not be rendered.   Polygon vertices should be specified in
clockwise order as viewed from the visible side.

For lighting and visibility testing purposes, the polygon's normal is
calculated from the first three vertices; thus you should ensure these
vertices are not collinear or counter-clockwise.  One- and two-vertex
polygons are deemed as always visible, fully illuminated.

To ensure correct -- or at least unsurprising -- rendering, the vertices
describing the polygon should be co-planar.  However, there is nothing in
VS3D that enforces this.

### Surface Colors/Attributes ###

For each line describing a polygon, the final integer describes the
polygon's surface color and attributes; the absolute value of this integer
is used (negative values are allowed, indicating this polygon has detail
polygons (discussed later)).  Absolute values from 0 - 255 are "normal"
color codes.  Absolute values of 256 or greater are special surface codes.

Attributes marked as v2.0 were introduced in VideoScape version 2.0, and are
not available in v1.0.

#### Normal Color Codes (0 - 255) ####

For values 0 - 255, the code is split into several bitfields:

| Bits | Meaning |
| ---: | ------- |
| 3:0  | Base surface color |
| 5:4  | Surface rendering mode |
| 6    | Translucent (v2.0) |
| 7    | Phong shaded (v2.0) |

The values of these fields are OR'ed together to create a color code.


##### Base Surface Color Codes #####

The least significant four bits of the integer describe the polygon's color,
taken from the following table:


| Code   | Color               | Code   | Color |
| -----: | -------             | -----: | ----- |
|  0     | Black               |  8     | Black (avoid; use zero instead) |
|  1     | Dark blue           |  9     | Light blue |
|  2     | Dark green          | 10     | Light green |
|  3     | Dark cyan (v2.0)    | 11     | Cyan (v2.0) |
|  4     | Dark red            | 12     | Light red |
|  5     | Dark purple (v2.0)  | 13     | Purple (v2.0) |
|  6     | Brown               | 14     | Yellow |
|  7     | Grey                | 15     | White |

Sharp-eyed observers will note this closely resembles the EGA color coding
scheme from the original IBM-PC.


##### Surface Rendering Mode #####

Bits 5:4 of the code indicate the "surface rendering mode" for the polygon,
as follows:


| Value  | Code Range | Meaning          |
| -----: | ---------: | ---------------- |
| 0      | 0 - 15     | Light-sourced shading, matte surface |
| 1      | 16 - 31    | Light-sourced shading, glossy surface |
| 2      | 32 - 47    | Unshaded, full illumination |
| 3      | 48 - 63    | Unfilled outline (wireframe) |

A "glossy" surface means the polygon has a specular attribute, and will
appear to reflect the white light source off the surface.  A "matte" surface
has no specular attribute; it will only appear in the base color.  An
"unshaded " polygon is rendered fully illuminated, regardless of its
orientation to the light source.


##### Translucent Polygons (v2.0) #####

Values with bit 6 set (codes in the range 64 - 127 and 192 - 255) are
rendered as translucent.  Imagery behind the translucent polygon is
partially visible.  The resulting color is a 50-50 mix of the pixel's
previous color and this polygon's own color after shading (if any).


##### Phong-Shaded Polygons (v2.0) #####

Values with bit 7 clear (code ranges 0 - 127) are rendered as flat-shaded,
yielding objects that appear rigid and geometric.  Values with bit 7 set
(code ranges 128 - 255) are rendered with Phong shading, allowing objects to
appear more rounded and smooth.


#### Special Color Codes (>= 256, v2.0) ####

Polygons with codes greater than or equal to 256 render no color or
attributes of their own.  Rather, they make available some special rendering
effects as follows:

  256. (Unknown)
  257. **Decrease brightness under fill:**  This polygon dims all the pixels
       underneath it.  This can be used to achieve (highly polygonal) smoke
       effects.
  258. **Increase brightness under fill:**  This polygon brightens all the
       pixels underneath it.  This can be used to achieve laser beam or "God
       rays"-type effects.
  259. **Chrome:**  This polygon appears as a chrome-plated surface,
       reflecting the surrounding environment.  Note that only the global
       sky and ground colors are reflected (primitive environment mapping).


### Detail Polygons ###

Because VideoScape had no texture mapping, simple surface details (which
otherwise would have had to be part of the mesh) were supported using an
inventive feature called detail polygons.  These are polygons that are
rendered immediately after the "parent" polygon, in the order in which they
appear in the file.  In other words, the parent polygon and its detail
polygons are treated by VS3D as a single unit.

The structure of a detail polygon appearing in the file is as follows:
  * A polygon indicates it has detail polygons by specifying a negative value
    for the color code.
  * On the immediately following line appears a single integer specifying
    the number of detail polygons present (`detail_count`).  Leading and
    trailing whitespace are ignored.
  * On the subsequent `detail_count` lines appear polygons as described
    above (vertex count, vertex indices, color code).

An example polygon having two detail polygons might appear in the file as
follows:

```
4 1 4 3 2 -7
  2
    2 1 3 0
    2 2 4 0
```

Once `detail_count` detail polygons have been read, normal polygons may
follow.

Detail polygons are not recursive; only a single level is supported.

While detail polygons make the most sense when they are co-planar with, and
bounded by, their parent, there is nothing in VS3D that enforces this.
Thus, detail polygons can, and are known to, appear anywhere.

Shading is calculated only for the parent polygon; detail polygons that
specify shaded colors/surface attributes re-use this calculation, regardless
of their actual orientation.

Depth-sorting and visibility testing is calculated only for the parent
polygon.  If the parent polygon is deemed visible, it and all its details are
rendered, regardless of where the details might actually be.

The color code for a shaded, matte black polygon is 0.  If you want such a
polygon to have detail polygons, -0 won't work.  Use -8 instead.


## Binary Format ##

Structurally, binary format is identical to text format, consisting of a
header, vertex count, vertices, and polygons.  However, instead of being
written as human readable text, the numeric data is stored in
machine-readable form -- more precisely, readable to an Amiga computer,
which has the following rules:
  * All multi-byte values (integers and floats) are stored in big-endian
    format (most significant byte appears first).
  * Floating point values are expressed in [Motorola Fast Floating
    Point](https://wiki.amigaos.net/wiki/Math_Libraries) (FFP) format.

Happily, these conversions are fairly trivial.


### Header ###

The header consists of the following four byte values, in order:

    0x33 0x44 0x42 0x31

Which are the ASCII characters "3DB1".

### Vertex Count ###

Immediately following the header is an unsigned 16-bit integer representing
the number of vertices in the file (`vtx_count`).

### Vertices ###

Each vertex consists of three floating-point values, appearing in XYZ order,
each 32 bits wide, for a total of 12 bytes per vertex.  Expressed as a C
struct, this might appear as follows:

    // Note: We can't use the type `float` here, as these are not IEEE-754
    // compliant floating point values.
    //
    struct vs3d_vert {
        int32_t x, y, z;
    }

The number of vertices appearing is equal to `vtx_count`.

### Polygons ###

Immediately following the vertices are the polygons.  Each polygon is
specified by a series of 16-bit integers having the following structure:
  * **Vertex Count:** (`poly_vtx_count`) The first integer specifies the
    number of vertices in the polygon.  This integer is unsigned.
  * **Vertex Indices:** The following `poly_vtx_count` integers denote
    indices into the previously appearing array of vertices.  These indices
    are zero-based and unsigned.
  * **Color code/surface attributes:** The final integer specifies the
    color and surface attributes of the polygon.  This integer is *signed*,
    to allow for detail polygons.

Polygons continue until end-of-file.  All the rules that apply to
text-format polygons also apply here.

### Detail Polygons ###

Binary detail polygons are exactly analogous to their text-mode
counterparts.  The value `detail_count` is a 16-bit unsigned integer, and
immediately follows the negative color code from the parent polygon.  The
following `detail_count` polygons are formatted exactly as normal binary
polygons.

