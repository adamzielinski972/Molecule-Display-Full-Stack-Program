#include "mol.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#define PI 3.141592654


void atomset( atom *atom, char element[3], double *x, double *y, double *z ) 
{
    //copies passed in variable information to corresponding atom member
    strcpy(atom->element,element);
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

void atomget( atom *atom, char element[3], double *x, double *y, double *z ) 
{   
    //copies information from atom and pastes it in the correspomding pointer variable
    strcpy(element,atom->element);
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs)
{   
    //copies passed in information to corresponding bond members
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;

    compute_coords(bond);
}

void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs )
{   
    //copies info from bond members and puts them in the variables
    *a1 = bond->a1;
    *a2 = bond->a2;
    *epairs = bond->epairs;
    *atoms = bond->atoms;
}

void compute_coords( bond *bond )
{
    //grabs the info from the bonds atoms to compute bond info
    bond->x1 = bond->atoms[bond->a1].x;
    bond->x2 = bond->atoms[bond->a2].x;
    bond->y1 = bond->atoms[bond->a1].y;
    bond->y2 = bond->atoms[bond->a2].y;
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2; //average of atom z values
    bond->len = sqrt(pow((bond->x2 - bond->x1),2) + pow((bond->y2 - bond->y1), 2) + pow((bond->atoms[1].z - bond->atoms[0].z),2)); //len between atoms
    bond->dx = (bond->x2 - bond->x1) / bond->len; //difference in x vals of atoms
    bond->dy = (bond->y2 - bond->y1) / bond->len; //difference in y vals of atoms
}

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) 
{
    molecule *newMolecule = malloc(sizeof(molecule)); //creates space for new molecule

    if (newMolecule == NULL) { //checks if the molecule is null
        printf("Error malloc return Null"); //prints error message
        return NULL; //returns NULl
    }
    //copies info over to the moleucle
    newMolecule->atom_max = atom_max; 
    newMolecule->atom_no = 0;

    newMolecule->atoms = malloc(atom_max * sizeof(atom)); //creates space for the atoms array
    if (newMolecule->atoms == NULL) { //checks if the list is null
        printf("Error malloc return Null");
        return NULL;
    }

    newMolecule->atom_ptrs = malloc(atom_max * sizeof(atom*)); //creates space for the atom pointers array
    if (newMolecule->atom_ptrs == NULL) { //checks if the list is null
        printf("Error malloc return Null");
        return NULL;
    }
    //copies values to the newMolecules corresponding members
    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;

    newMolecule->bonds = malloc(bond_max * sizeof(bond)); //creates space for the bonds list
    if (newMolecule->bonds == NULL) { //checks if the list is null
        printf("Error malloc return Null");
        return NULL;
    }
    newMolecule->bond_ptrs = malloc(bond_max * sizeof(bond*)); //creates space for the bond pointers list
    if (newMolecule->bond_ptrs == NULL) { //checks if the list is null
        printf("Error malloc return Null");
        return NULL;
    }

    return newMolecule; //returns the address of newMolecule
}

molecule *molcopy( molecule *src ) 
{
    molecule *newMolecule = molmalloc(src->atom_max,src->bond_max); //creates space for new molecule

    for (int i = 0; i < src->atom_no; i++) { //runs through each atom in the source molecule and appends them to the list in the new molecule
        molappend_atom(newMolecule,&(src->atoms[i])); //calls molappened function to add the atoms to the new molecule
    }

    for (int i = 0; i < src->bond_no; i++) { //does the same as above but for the bonds
        molappend_bond(newMolecule,&(src->bonds[i]));
    }

    return newMolecule;

}

void molfree( molecule *ptr ) 
{   
    //first frees the members of the molecule
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    /*for (int i = 0; i < ptr->bond_no; i++)
    {
        free(ptr->bond_ptrs[i]->atoms);
    }*/
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    //then free the molecule
    free(ptr);
}

void molappend_atom( molecule *molecule, atom *atom )
{
    if (molecule->atom_max == 0) //checks if the max number of atoms is zero
    {
        molecule->atom_max++; //increments it to zer
        molecule->atoms = realloc(molecule->atoms,sizeof(struct atom) * molecule->atom_max); //adds more space for the new max number of atoms
        molecule->atom_ptrs = realloc(molecule->atom_ptrs,sizeof(struct atom*) * molecule->atom_max); //adds more space for the new max number of atoms pointers
    }
    else if (molecule->atom_no == molecule->atom_max) //checks if there is no more room for any atoms
    {
        molecule->atom_max = (molecule->atom_max ) * 2; //doubles the max number of atoms
        molecule->atoms = realloc(molecule->atoms,sizeof(struct atom) * molecule->atom_max); //adds more space for the new max number of atoms
        molecule->atom_ptrs = realloc(molecule->atom_ptrs,sizeof(struct atom*) * molecule->atom_max); //adds more space for the new max number of atom pointers
        for (int i = 0; i < molecule->atom_no; i++) { //goes through all the atoms and updates the pointers
            molecule->atom_ptrs[i] = &(molecule->atoms[i]);
        }
    }
    molecule->atoms[molecule->atom_no] = *atom; //adds the new atom to the list
    molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]); //updates the pointer to point to the new atom
    molecule->atom_no++; //increses the numbers of atoms in the list
}

void molappend_bond( molecule *molecule, bond *bond ) //works the same as the above function but for bonds
{
    if (molecule->bond_max == 0)
    {
        molecule->bond_max++;
        molecule->bonds = realloc(molecule->bonds,sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs,sizeof(struct bond*) * molecule->bond_max);
    }
    else if (molecule->bond_no == molecule->bond_max)
    {
        molecule->bond_max = (molecule->bond_max ) * 2;
        molecule->bonds = realloc(molecule->bonds,sizeof(struct bond) * molecule->bond_max);
        molecule->bond_ptrs = realloc(molecule->bond_ptrs,sizeof(struct bond*) * molecule->bond_max);
        for (int i = 0; i < molecule->bond_no; i++) {
            molecule->bond_ptrs[i] = &(molecule->bonds[i]);
        }
    }
    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
    molecule->bond_no++;
}

void molsort( molecule *molecule ) { //calls q sort to re-arrange the atom and bond pointers
    qsort(molecule->atom_ptrs,molecule->atom_no,sizeof(struct atom*),cmpAtom);
    qsort(molecule->bond_ptrs,molecule->bond_no,sizeof(struct bond*),cmpBond);
}

int cmpAtom (const void *a, const void *b) {
    atom **double_ptr_a, **double_ptr_b;

    double_ptr_a = (atom**)a; //creates variable to represent passed in atom 1
    double_ptr_b = (atom**)b; //creates varaible to represent passed in atom 2

    if ((*double_ptr_a)->z > (*double_ptr_b)->z) { //compares the atoms z values and returns value telling how to arrange
        return 1; 
    }
    else if ((*double_ptr_a)->z < (*double_ptr_b)->z) { //compares the atoms z values and returns value telling how to arrange
        return -1;
    }
    else { //returns zero in other cases
        return 0;
    }
}

int cmpBond (const void *a, const void *b) { //works same as above but calculates average of two atoms z values
    bond *double_ptr_a, *double_ptr_b;

    double_ptr_a = (bond*)a;
    double_ptr_b = (bond*)b;

    double avg1 = double_ptr_a->z; //uses the two atoms in the bonds z values and gets average
    double avg2 = double_ptr_b->z;

    if (avg1 > avg2) {
        return 1;
    }
    else if (avg1 < avg2) {
        return -1;
    }
    else {
        return 0;
    }
}

void xrotation( xform_matrix xform_matrix, unsigned short deg )
{
    //assigns values to matrix based on the base x rotation matrix and the passed in degree
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos((deg * PI) / 180);
    xform_matrix[1][2] = -1 * (sin((deg * PI) / 180));

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin((deg * PI) / 180);
    xform_matrix[2][2] = cos((deg * PI) / 180);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg )
{
    //assigns values to matrix based on the base y rotation matrix and the passed in degree
    xform_matrix[0][0] = cos((deg * PI) / 180);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin((deg * PI) / 180);

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -1 * (sin((deg * PI) / 180));
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos((deg * PI) / 180);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg )
{
    //assigns values to matrix based on the base z rotation matrix and the passed in degree
    xform_matrix[0][0] = cos((deg * PI) / 180);
    xform_matrix[0][1] = -1 * (sin((deg * PI) / 180));
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin((deg * PI) / 180);
    xform_matrix[1][1] = cos((deg * PI) / 180);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

void mol_xform( molecule *molecule, xform_matrix matrix ) 
{
    int i;

    double tempx, tempy, tempz; 

    for (i = 0; i < molecule->atom_no; i++) 
    {   
        //sets the values of the variables to their initial state before they get changed
        tempx = molecule->atoms[i].x;
        tempy = molecule->atoms[i].y;
        tempz = molecule->atoms[i].z;

        //uses dot product to multiply the two matrices together to get the new x,y,z values
        molecule->atoms[i].x = ((tempx * matrix[0][0]) + 
                                    (tempy * matrix[0][1]) + 
                                    (tempz * matrix[0][2]));

        molecule->atoms[i].y = ((tempx * matrix[1][0]) + 
                                    (tempy * matrix[1][1]) + 
                                    (tempz * matrix[1][2]));
        
        molecule->atoms[i].z = ((tempx * matrix[2][0]) + 
                                    (tempy * matrix[2][1]) + 
                                    (tempz * matrix[2][2]));
    }

    for (i = 0; i < molecule->bond_no; i++)
    {
        compute_coords(&molecule->bonds[i]);
    }
}
