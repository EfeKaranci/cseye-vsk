import matplotlib.pyplot as plt
import matplotlib.patches as patches
import states.statesAllRequests as statesAllRequests
def GetFigureDimension():
    # Extract x and y extents from the selected points.
    # (Here we assume statesAllRequests.SelectedPointsForCurrentRequest exists and that the 6th element [index 5] is a point [x, y].)
    all_x = [pt["Coords"][0] for pt in statesAllRequests.SelectedPointsForCurrentRequest]
    all_y = [pt["Coords"][1] for pt in statesAllRequests.SelectedPointsForCurrentRequest]
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    span_x = max_x - min_x
    span_y = max_y - min_y
    # Use the dominant span so that the data region is square.
    span = max(span_x, span_y)
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    # Determine the data axis limits.
    # We add a 2" margin (in data units) around the data.
    fig_width, fig_height = 48, 36  # overall figure size in inches
    # Define the available content region after the outer 2" margins:
    content_width_in = fig_width - 2   # 48 - 2*2
    content_height_in = fig_height - 2   # 36 - 2*2
    # Use the dominant span to compute effective scale (data units per inch).
    if span == span_x:
        effective_scale = span / content_width_in
    else:
        effective_scale = span / content_height_in
    margin_data = 2 * effective_scale  # 2" in data units
    final_x_lim = (center_x - span/2 - margin_data, center_x + span/2 + margin_data)
    final_y_lim = (center_y - span/2 - margin_data, center_y + span/2 + margin_data)
    # Now lay out the figure. The overall page is 48″ x 36″.
    # Outer margin (between the page edge and the border): 2″ on every side.
    outer_left_in = 1.0
    outer_bottom_in = 1.0
    content_width_in = fig_width - 4  # 48 - 2*2 = 44 inches
    content_height_in = fig_height - 4  # 36 - 2*2 = 32 inches
    # Internal padding: leave 1″ padding inside the border.
    padding_in = 1.0
    # Reserve fixed height for the title area (e.g., 3 inches) at the bottom of the content region.
    title_height_in = 3.0
    # Compute the data (plot) area dimensions in inches.
    # The data area is inside the content region minus internal padding and title area.
    data_left_in = outer_left_in + padding_in           # e.g., 2 + 1 = 3 inches from left edge
    data_bottom_in = outer_bottom_in + padding_in + title_height_in  # e.g., 2 + 1 + 3 = 6 inches from bottom edge
    data_width_in = content_width_in - 1 * padding_in    # e.g., 44 - 2 = 42 inches
    data_height_in = content_height_in - 1 * padding_in - title_height_in  # e.g., 32 - 2 - 3 = 27 inches
    # Convert these data area dimensions into normalized coordinates (relative to overall figure).
    left_norm = data_left_in / fig_width         # data area left in figure coords.
    bottom_norm = data_bottom_in / fig_height    # data area bottom in figure coords.
    width_norm = data_width_in / fig_width
    height_norm = data_height_in / fig_height
    # Also define normalized coordinates for the border (which outlines the entire content region).
    border_left_norm = outer_left_in / fig_width
    border_bottom_norm = outer_bottom_in / fig_height
    border_width_norm = (fig_width - 4) / fig_width  # 44/48
    border_height_norm = (fig_height - 4) / fig_height  # 32/36
    return (fig_width, fig_height, final_x_lim, final_y_lim,
            left_norm, bottom_norm, width_norm, height_norm,
            border_left_norm, border_bottom_norm, border_width_norm, border_height_norm)

def SetAx(fig, left_norm, bottom_norm, width_norm, height_norm, final_x_lim, final_y_lim):
    # Create the data axes in the allocated area.
    ax = fig.add_axes([left_norm, bottom_norm, width_norm, height_norm])
    ax.set_xlim(final_x_lim)
    ax.set_ylim(final_y_lim)
    ax.set_aspect('equal', adjustable='box')
    ax.axis('off')
    return ax

def PlotStructure():
    if len(statesAllRequests.SelectedPointsForCurrentRequest) > 0:
        (fig_width, fig_height, final_x_lim, final_y_lim,
         data_left_norm, data_bottom_norm, data_width_norm, data_height_norm,
         border_left_norm, border_bottom_norm, border_width_norm, border_height_norm) = GetFigureDimension()
        # Create the overall figure.
        fig = plt.figure(figsize=(fig_width, fig_height))
        # Create the data (plot) axes using the normalized positions.
        ax = SetAx(fig, data_left_norm, data_bottom_norm, data_width_norm, data_height_norm, final_x_lim, final_y_lim)
        # Plot your structure lines (example loop; customize as needed).
        FrameScale = 0.9
        for line in statesAllRequests.SelectedFramesForCurrentRequest:
            # Assume line[6:8] are two 2D points (already projected)
            Pt2dI, Pt2dJ = line["Pt2dI"],line["Pt2dJ"],
            mid = (Pt2dI + Pt2dJ) / 2
            new_pI = mid + (Pt2dI - mid) * FrameScale
            new_pJ = mid + (Pt2dJ - mid) * FrameScale
            xs = [new_pI[0], new_pJ[0]]
            ys = [new_pI[1], new_pJ[1]]
            Color = "black"
            if "Color" in line:
                Color = line["Color"]
            ax.plot(xs, ys, '-o', markersize=0.5, color=Color, linewidth=0.5)
        for floor in statesAllRequests.SelectedAreasForCurrentRequest:
            SurfaceColor='lightgray'
            Pts = floor["Coords"]
            xs = [p[0] for p in Pts]
            ys = [p[1] for p in Pts]
            if("Color" in floor):
                SurfaceColor=floor["Color"]
            ax.fill(xs, ys, facecolor=SurfaceColor, edgecolor='gray', alpha=0.3)
        for floor in statesAllRequests.SelectedNullAreasForCurrentRequest:
            SurfaceColor='white'
            Pts = floor["Coords"]
            xs = [p[0] for p in Pts]
            ys = [p[1] for p in Pts]
            if("Color" in floor):
                SurfaceColor=floor["Color"]
            ax.fill(xs, ys, facecolor=SurfaceColor, edgecolor='gray', alpha=0.3)
        statesAllRequests.ax = ax
        # Add the title in the title area (which lies in the content region,
        # beneath the data axes). The title region is the bottom part of the content region.
        title_text = statesAllRequests.RequestNameFormat2  # with multiple lines if desired.
        # Place the title using fig.text in normalized coordinates.
        # We want it inside the content region but below the data axes.
        # The content region (border) lower left is at (border_left_norm, border_bottom_norm).
        # We reserved a 1" internal padding, so we can position the title roughly at:
        title_x = border_left_norm + 0.02          # a small offset from the left border
        # The title area in inches starts at outer_bottom_in + padding_in, i.e. 2 + 1 = 3 inches,
        # and extends up to (2+1+title_height_in)= 6 inches. We choose a normalized y near the bottom of the content region.
        title_y = border_bottom_norm + (1 / fig_height)  # about 1" above the bottom of content region.
        fig.text(title_x, title_y, title_text, fontsize=36,
                 verticalalignment='bottom', horizontalalignment='left')
        # Draw a border around the entire content region (the area with dimensions 44" x 32")
        border = patches.Rectangle((border_left_norm, border_bottom_norm),
                                   border_width_norm, border_height_norm,
                                   transform=fig.transFigure,
                                   fill=False, edgecolor='black', linewidth=1)
        fig.patches.append(border)

        plt.close(fig)
        return fig