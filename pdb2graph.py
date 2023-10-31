import argparse
import util_common



def pdb2graph(pdb_file, gr_name):
    atoms = {}
    bonds = {}
    edges = []
    bond_type = {'double': [], 'triple': []}

    with open(pdb_file, 'r') as pdb:
        lines = pdb.readlines()
        for line in lines[2:-2]:
            components = line.strip().split()
            s_type = components[0]

            if s_type == 'HETATM':
                    atom_no = int(components [1])
                    atom_name = components [2]
                    x_coord = components [5]
                    y_coord = components [6]

                    if atom_name != 'H':
                        atoms.update({atom_no: (atom_name, x_coord, y_coord)})

            elif s_type == 'CONECT':
                    atom1_no = int(components [1])
                    bond_atoms = components[2:]

                    for n_atoms in bond_atoms:
                        count = bond_atoms.count(n_atoms)

                        if count == 2 and [atom1_no, n_atoms] not in bond_type['double']:
                            bond_type['double'].append([atom1_no, int(n_atoms)])
                        elif count == 3 and [atom1_no, n_atoms] not in bond_type['double']:
                            bond_type['triple'].append([atom1_no, int(n_atoms)])

                        for b_atom in bond_atoms:
                            if atom1_no in atoms.keys() and int(b_atom) in atoms.keys():
                                atom2_no = int(b_atom)
                                if atom2_no > atom1_no:
                                    bond = [atom1_no, atom2_no]
                                else:
                                    bond = [atom2_no, atom1_no]

                            if bond[0] not in bonds.keys():
                                bonds.update({bond[0]:[bond]})
                            elif bond not in bonds[bond[0]]:
                                bonds[bond[0]].append(bond)

        f_occurance = {}
        s_occurance = {}

        for e_bond in bonds.keys():
            for i in range(len(bonds[e_bond])):
                edges.append(bonds[e_bond][i])

            count = 0
            s_count = 0
            f_occurance.update({e_bond: []})
            s_occurance.update({e_bond: []})
            for j in range(len(edges)):
                if edges[j][0] == (e_bond):
                    count +=1
                    f_occurance[e_bond].append([j,edges[j][1]])

                elif edges[j][1] == (e_bond):
                    s_count += 1
                    s_occurance[e_bond].append([j, edges[j][0]])

            if len(f_occurance[e_bond]) > 2:
                for k in range(len(f_occurance[e_bond])):
                 b_atom = (f_occurance[e_bond][k][1])
                 if b_atom not in bonds.keys() and count > 2:
                    new_bond = edges[f_occurance[e_bond][k][0]][::-1]
                    edges[f_occurance[e_bond][k][0]] = new_bond
                    count = count - 1

            if len(s_occurance[e_bond]) > 1:
                for l in range(len(s_occurance[e_bond])):
                    b_atom = (s_occurance[e_bond][l][1])
                    if len(s_occurance[b_atom]) < 1 and s_count > 1:
                        new_bond = edges[s_occurance[e_bond][l][0]][::-1]
                        edges[s_occurance[e_bond][l][0]] = new_bond
                        s_count = s_count - 1

    dag_edges = list(edges)
    root = next(iter(atoms))
    q = [root]
    seen = {}
    while len(q) > 0:
        src = q[0]
        q = q[1:]
        seen[src] = None
        for i in range(len(edges)):
            dst, flip = None, False
            if edges[i][0] == src:
                dst = edges[i][1]
            elif edges[i][1] == src:
                dst = edges[i][0]
                flip = True
            if dst is not None and dst not in seen:
                q.append(dst)
                if flip:
                    dag_edges[i] = list(reversed(dag_edges[i]))

    olines = []
    olines.append('t dag l2 l')
    olines.append('c C dddddd')
    olines.append('c N b8ccee')
    olines.append('c O ea9999')
    olines.append('c S ffe599')
    olines.append('c P dfba94')

    for atom_no, (atom_name, x_coord, y_coord) in atoms.items():
        olines.append(f'n {atom_no} {atom_name} {x_coord} {y_coord}')

    for i in range(len(edges)):
        if edges[i] in bond_type['double']:
            b_type = '2'
        elif edges[i] in bond_type['triple']:
            b_type = '3'
        else:
            b_type = '1'

        olines.append(f'e {dag_edges[i][0]} {dag_edges[i][1]} {b_type}')

    for oline in olines:
        print(oline)

    with open(gr_name, 'wt') as o:
        o.write('\n'.join(olines))



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Converts pdb to graph file')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    parser.add_argument('--pdbfile', required=True, type=str, help='Input pdb description file.')
    args = parser.parse_args()

    pdb2graph(args.pdbfile, args.outfile)
