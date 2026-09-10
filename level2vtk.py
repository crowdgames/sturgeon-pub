import argparse, math, pickle, sys
import util_common


DEFAULT_VOXEL_MAP = {
    '_': 0,
    'O': 1,
    'W': 2,
    'B': 3,
    'P': 4,
    'G': 5,
    'D': 6,
    'H': 7,
    'C': 8,
    'Q': 9,
}


def load_voxel_map_from_tileset(tileset):
    util_common.check(tileset.tile_to_text is not None, 'The tileset file does not contain text mappings (tile_to_text is None).')

    dynamic_map = {}
    for tile_id, tile_char in tileset.tile_to_text.items():
        if tile_char:
            dynamic_map[tile_char] = tile_id

    print(f'Loaded {len(dynamic_map)} mappings from tileset.')
    return dynamic_map


def split_by_all_void(lst):
    splt = []
    current_block = []

    for item in lst:
        all_void = (item == util_common.VOID_TEXT) or (item.count(util_common.VOID_TEXT) == len(item))
        if all_void:
            if len(current_block) > 0:
                splt.append(current_block)
                current_block = []
        else:
            current_block.append(item)
    if len(current_block) > 0:
        splt.append(current_block)

    return splt


def detect_dimensions(timesteps):
    first_block = timesteps[0]
    rows = len(first_block)
    tokens = split_by_all_void(first_block[0])
    storys = len(tokens)
    cols = len(tokens[0])

    for i, block in enumerate(timesteps):
        util_common.check(len(block) == rows, f'Timestep {i}: expected {rows} rows, got {len(block)}')
        for r, line in enumerate(block):
            toks = split_by_all_void(line)
            util_common.check(len(toks) == storys, f'Timestep {i}, row {r}: expected {storys} tokens, got {len(toks)}')
            for t in toks:
                util_common.check(len(t) == cols, f'Timestep {i}, row {r}: token "{t}" has {len(t)} chars, expected {cols}')

    return rows, cols, storys


def parse_timestep(lines, cols, rows, storys, current_map):
    grid = [[[0 for _ in range(storys)] for _ in range(cols)] for _ in range(rows)]

    for row in range(rows):
        tokens = split_by_all_void(lines[row])
        for story in range(storys):
            token = tokens[story]
            for col in range(cols):
                char = token[col]
                util_common.check(char in current_map, f'Unknown voxel char "{char}"')
                grid[row][col][story] = current_map[char]

    return grid


def make_vtk(grid, cols, rows, storys, current_map):
    lines = []

    lines.append(f'# vtk DataFile Version 3.0\n')
    lines.append(f'Voxel timestep\n')
    lines.append(f'ASCII\n')
    lines.append(f'DATASET STRUCTURED_POINTS\n')
    lines.append(f'DIMENSIONS {cols + 1} {rows + 1} {storys + 1}\n')
    lines.append(f'ORIGIN 0 0 0\n')
    lines.append(f'SPACING 1 1 1\n')

    total_cells = cols * rows * storys
    lines.append(f'CELL_DATA {total_cells}\n')

    lines.append(f'SCALARS voxels int 1\n')
    lines.append(f'LOOKUP_TABLE default\n')

    for story in range(storys):
        for row in range(rows):
            for col in range(cols):
                lines.append(str(grid[row][col][story]) + (' ' if col + 1 < cols else ''))
            lines.append('\n')
        lines.append('\n' if story + 1 < storys else '')
    lines.append('\n')

    lines.append(f'FIELD CellText 1\n')
    lines.append(f'TileName 1 {total_cells} string\n')

    inv_map = {v: k for k, v in current_map.items()}

    for story in range(storys):
        for row in range(rows):
            for col in range(cols):
                val = grid[row][col][story]
                char = inv_map.get(val, '?')
                lines.append(f'"{char}"' + (' ' if col + 1 < cols else ''))
            lines.append('\n')
        lines.append('\n' if story + 1 < storys else '')

    return lines


def level2vtk(text_level, tileset, rows, cols, storys):
    if tileset:
        current_map = load_voxel_map_from_tileset(tileset)
    else:
        current_map = DEFAULT_VOXEL_MAP

    timesteps = split_by_all_void(text_level)

    util_common.check(len(timesteps) > 0, 'No valid timesteps found.')

    use_rows, use_cols, use_storys = detect_dimensions(timesteps)
    print(f'Detected dimensions: rows={use_rows}, cols={use_cols}, storys={use_storys}')
    print(f'Found {len(timesteps)} timesteps.')

    # Allow overrides if provided
    if rows is not None:
        use_rows = rows
    if cols is not None:
        use_cols = cols
    if storys is not None:
        use_storys = storys

    all_vtks = []
    for ts_lines in timesteps:
        grid = parse_timestep(ts_lines, use_cols, use_rows, use_storys, current_map)
        vtk = make_vtk(grid, use_cols, use_rows, use_storys, current_map)
        all_vtks.append(vtk)

    print(f'Done. Created {len(all_vtks)} VTKs.')

    return all_vtks


if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Convert level text file to 3D VTK timesteps for ParaView.')
    parser.add_argument('--outfile', type=str, required=True, help='Output prefix for vtk files.')
    parser.add_argument('--textfile', type=str, required=True, help='Path to the input text file.')
    parser.add_argument('--tilesetfile', type=str, help='Path to tileset file for dynamic voxel map.')
    parser.add_argument('--cols', type=int, default=None, help='Override number of columns (auto-detected if omitted).')
    parser.add_argument('--rows', type=int, default=None, help='Override number of rows (auto-detected if omitted).')
    parser.add_argument('--storys', type=int, default=None, help='Override number of storys (auto-detected if omitted).')
    parser.add_argument('--print-vtk', action='store_true', help='Print VTK files.')
    args = parser.parse_args()

    text_level = util_common.read_text_level(args.textfile, False)

    tileset = None
    if args.tilesetfile is not None:
        with util_common.openz(args.tilesetfile, 'rb') as f:
            tileset = pickle.load(f)

    vtks = level2vtk(text_level, tileset, args.rows, args.cols, args.storys)

    digits = int(math.log(len(vtks), 10)) + 1
    for ii, vtk in enumerate(vtks):
        outname = args.outfile + str(ii).zfill(digits) + '.vtk'
        with open(outname, 'wt') as f:
            f.writelines(vtk)
        if args.print_vtk:
            sys.stdout.writelines(vtk)

    util_common.exit_solution_found()
