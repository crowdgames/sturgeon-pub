import argparse
import util_common



def graph2pdb(gr, output):
    olines = []

    atoms = {}

    counter = 0
    with open(gr, 'rt') as file:
        lines = file.readlines()

        olines.append('COMPND    UNNAMED')
        olines.append('AUTHOR    graph2pdb')

        bonded_atoms = {}

        for line in lines[6:]:
            component = line.strip().split()
            l_type = component[0]
            if l_type == 'n':
                counter += 1
                atom_no = counter
                atom_name = component[2]
                x_coord = float(component[3])
                y_coord = float(component[4])
                olines.append('HETATM  %3i%3s   %3s     %1i     %7.3f %7.3f %7.3f  %4.2f  %4.2f           %1s' %(atom_no, atom_name, 'UNL', 1, x_coord,y_coord, 0.000, 1.00, 0.00, atom_name))
                #olines.append('HETATM'+' '*2 +str(atom_no).rjust(3)+atom_name.rjust(3)+' '*3 + 'UNL' + ' '*5+'1'+ ' '*6+ f'{x_coord.ljust(5)}     {y_coord.ljust(5)}     0.000    1.00    0.00' + ' '*11 +atom_name)

                atoms.update({component[1]: atom_no})

            elif l_type == 'e':
                atom_1 = atoms[component[1]]
                atom_2 = atoms[component[2]]
                bond_type = component[3]
                if bond_type == '3':
                    n = 3
                elif bond_type =='2':
                    n = 2
                else:
                    n = 1

                if atom_1 not in bonded_atoms.keys():
                    if bond_type == '3':
                        bonded_atoms.update({atom_1:[atom_2, atom_2, atom_2]})
                    elif bond_type == '2':
                        bonded_atoms.update({atom_1:[atom_2, atom_2]})
                    else:
                        bonded_atoms.update({atom_1:[atom_2]})
                else:
                    for i in range(n):
                        bonded_atoms[atom_1].append(atom_2)

                if atom_2 not in bonded_atoms.keys():
                    if bond_type == '3':
                        bonded_atoms.update({atom_2:[atom_1, atom_1, atom_1]})
                    elif bond_type == '2':
                        bonded_atoms.update({atom_2:[atom_1, atom_1]})
                    else:
                        bonded_atoms.update({atom_2:[atom_1]})
                else:
                    for i in range(n):
                        bonded_atoms[atom_2].append(atom_1)

        #print(bonded_atoms)
        for key, values in bonded_atoms.items():
            atoms_no = '  '.join('%3i'% (value) for value in values)

            olines.append('CONECT  %3i  %3s' %(key, atoms_no))
            #olines.append(f'CONECT    {str(key).rjust(3)} {atoms_no.rjust(2)}')

    for oline in olines:
        print(oline)

    with open(output, 'wt') as o:
        o.write('\n'.join(olines))



if __name__ == '__main__':
    util_common.timer_start()

    parser = argparse.ArgumentParser(description='Converts pdb to graph file')
    parser.add_argument('--graphfile', required=True, type=str, help='Input graph file.')
    parser.add_argument('--outfile', required=True, type=str, help='Output file.')
    args = parser.parse_args()

    graph2pdb(args.graphfile, args.outfile)
