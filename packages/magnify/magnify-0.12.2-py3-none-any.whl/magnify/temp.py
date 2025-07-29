@registry.component("standardize_format")
def standardize_format(xp: xr.Dataset | xr.DataArray) -> xr.Dataset:
    if isinstance(xp, xr.DataArray):
        xp = xr.Dataset({"tile": xp}).assign_attrs(xp.attrs)

    # Rename dimensions since we'll be adding new arrays whose names will conflict.
    for old_name in ["x", "y", "row", "col"]:
        if old_name in xp.tile.dims:
            xp = xp.rename({old_name: "tile_" + old_name})

    # Save the original dimension ordering to be restored later.
    xp.attrs["__original_tile_dims__"] = list(xp.tile.dims)

    desired_order = ["channel", "time", "tile_row", "tile_col", "tile_y", "tile_x"]
    # If we have additional dimensions stack them all into a single time dimension.
    extra_dims = [dim for dim in xp.tile.dims if dim not in desired_order]
    if len(extra_dims) > 0:
        if "time" in xp.tile.dims:
            # Rename the time dimension to avoid conflicts.
            xp = xp.rename(time="__time__")
            extra_dims.append("__time__")
        xp = xp.stack(time=extra_dims)

    # Reorder the dimensions so they're always consistent and add missing dimensions.
    for dim in desired_order:
        if dim not in xp.tile.dims:
            xp["tile"] = xp.tile.expand_dims(dim)

    xp = xp.transpose(*desired_order)

    return xp



