import matplotlib.pyplot as plt
import matplotlib.patches as patches
import states.statesAllRequests as statesAllRequests
def GetFigureDimension():
    # 1) Compute data extents
    xs = [pt["Coords"][0] for pt in statesAllRequests.SelectedPointsForCurrentRequest]
    ys = [pt["Coords"][1] for pt in statesAllRequests.SelectedPointsForCurrentRequest]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = (max_x - min_x)*1.5
    span_y = (max_y - min_y)*1.5
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    # 2) Figure and margin sizes (in inches)
    fig_w, fig_h = 48, 36
    outer_margin = 2.0  # 2" from page edge to border
    inner_w = fig_w - 2 * outer_margin  # 44"
    inner_h = fig_h - 2 * outer_margin  # 32"
    data_margin = 2.0  # 2" of data‐unit margin

    # 3) Determine the common scale (data units per inch) so that the larger span just fits
    scale_x = (span_x + 2 * data_margin) / inner_w
    scale_y = (span_y + 2 * data_margin) / inner_h
    common_scale = max(scale_x, scale_y)

    # 4) Compute axis size in inches for each direction
    axis_w_in = (span_x + 2 * data_margin) / common_scale
    axis_h_in = (span_y + 2 * data_margin) / common_scale

    # 5) Convert axis size and position to normalized figure coords
    # Center the axis‐box within the inner region ([outer_margin, outer_margin] to [fig_w-outer_margin, fig_h-outer_margin])
    axis_left_in = outer_margin + (inner_w - axis_w_in) / 2
    axis_bottom_in = outer_margin + (inner_h - axis_h_in) / 2

    left_norm = axis_left_in / fig_w
    bottom_norm = axis_bottom_in / fig_h
    width_norm = axis_w_in / fig_w
    height_norm = axis_h_in / fig_h

    # 6) Compute final data limits (centered, with margin_data)
    half_w = span_x / 2 + data_margin
    half_h = span_y / 2 + data_margin
    final_x_lim = (center_x - half_w, center_x + half_w)
    final_y_lim = (center_y - half_h, center_y + half_h)

    # 7) Border rectangle around the inner content region:
    border_left_norm = outer_margin / fig_w
    border_bottom_norm = outer_margin / fig_h
    border_width_norm = inner_w / fig_w
    border_height_norm = inner_h / fig_h

    return (
        fig_w, fig_h,
        final_x_lim, final_y_lim,
        left_norm, bottom_norm, width_norm, height_norm,
        border_left_norm, border_bottom_norm, border_width_norm, border_height_norm
    )

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