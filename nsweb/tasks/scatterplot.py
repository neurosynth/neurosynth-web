import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import nibabel as nb

def scatter(x=None, y=None, gene=None, threshold_x=None, threshold_y=None, log_x=None, log_y=None, 
                        filter_x=None, filter_y=None, spatial_masks=None, region_masks=None, 
                        outfile=None, coef_font_size=10, axis_lab_size=24, 
                        x_lab='Gene expression (z)', y_lab='', mask_labels=None, lab_size=16, alpha=1.0,
                        unlabeled_alpha=1.0, fig_size=(8,8), min_samples=4, voxel_count_mask=None,
                        unlabeled_color='0.3', palette='Set1', marginals=True, savefile=None):

    # vectorize image data.
    x_data = x
    y_data = y

    fig = plt.figure(figsize=fig_size)
    
    scale = 5
    if marginals:
        scatter_ax = plt.subplot2grid((scale, scale), (1,0), colspan=scale-1, rowspan=scale-1)
        top_ax = plt.subplot2grid((scale, scale), (0,0), colspan=scale-1)
        right_ax = plt.subplot2grid((scale, scale), (1, scale-1), rowspan=scale-1)
        top_ax.set_axis_off()
        right_ax.set_axis_off()
    else:
        scatter_ax = plt.subplots()
        
    scatter_ax.set_xlabel(x_lab, fontsize=axis_lab_size)
    scatter_ax.set_ylabel(y_lab, fontsize=axis_lab_size)
    scatter_ax.xaxis.set_tick_params(labelsize=lab_size)
    scatter_ax.yaxis.set_tick_params(labelsize=lab_size)

    # decide which points to include
    x_in = np.isfinite(x_data)
    y_in = np.isfinite(x_data)
    
    if threshold_x != None:
        x_thr = x_data > float(threshold_x)
    else:
        x_thr = True
    if threshold_y != None:
        y_thr = y_data > float(threshold_y)
    else:
        y_thr = True

    # apply spatial masks
    if spatial_masks is not None:
        incl = np.zeros((len(x_data), len(spatial_masks)))
        for i, m in enumerate(spatial_masks):
            incl[:,i] = m
        if voxel_count_mask is not None:
            vcm = voxel_count_mask
            vcm[vcm < min_samples] = 0
            incl = np.hstack((incl, np.atleast_2d(vcm[:,None])))

        incl = np.all(incl, axis=1)
    else:
        incl = True

    valid_voxels = (x_in & y_in & x_thr & y_thr & incl)
    
    x = x_data[valid_voxels]
    y = y_data[valid_voxels]
    
    # Set image layers--each unique value > 0 represents a different mask;
    # 0 = all unlabeled voxels.
    layers = np.zeros_like(y)
    if region_masks is not None:
        for i, m in enumerate(region_masks):
            m = m[valid_voxels]
            layers[m>0] = i + 1
    
    palette = sns.color_palette(palette, len(np.unique(layers))-1)

    for i, v in enumerate(np.unique(layers)):
        v = int(v)
        color = tuple(palette[i-1]) if v else (0,0,0)
        x_r, y_r = x[layers==v], y[layers==v]
        a = alpha if v else unlabeled_alpha
        
        # Make label
        if i:
            if mask_labels is None:
                # name = re.split( '\.', re.split( '/', region_masks[v-1])[-1])[0]
                name = "Mask %i" % str(i)
            else:
                name = mask_labels[v-1]
            label = '%s (r = %.2f)' % (name, np.corrcoef(x_r, y_r)[1][0])
        else:
            label = 'all (r = %.2f)' % np.corrcoef(x, y)[1][0]

        # Add layer to scatter plot
        scatter_ax.plot(x_r, y_r, 'o', alpha=a, markersize=6, label=label, markerfacecolor=color)
        
        # Marginal densities
        if marginals:
            if not i:
                x_r, y_r = x, y  # Marginal density for all points, not just unlabeled
            sns.kdeplot(x_r, ax=top_ax, color=color, shade=True)
            sns.kdeplot(y_r, ax=right_ax, color=color, vertical=True, shade=True)
    
    scatter_ax.legend(fontsize=lab_size, markerscale=1.5, framealpha=0.8, loc='upper left')
    fig.subplots_adjust(hspace=0.0)
    fig.subplots_adjust(wspace=0.0)

    # plt.tight_layout()
    
    if savefile is not None:
        plt.savefig(savefile, bbox_inches='tight')
        
    return scatter_ax