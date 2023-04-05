#include "mol.h"

void atomset(atom *atom, char element[3], double *x, double *y, double *z) {
  for (int ctr = 0; ctr < 3; ctr++) {
    atom->element[ctr] = element[ctr];
  }

  atom->x = *x;
  atom->y = *y;
  atom->z = *z;
}

void atomget(atom *atom, char element[3], double *x, double *y, double *z) {
  for (int ctr = 0; ctr < 3; ctr++) {
    element[ctr] = atom->element[ctr];
  }

  *x = atom->x;
  *y = atom->y;
  *z = atom->z;
}

// This was a strange function. That is all I am going to say :)
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
  bond->a1 = *a1;
  bond->a2 = *a2;
  bond->epairs = *epairs;
  bond->atoms = *atoms;
  compute_coords(bond);
}

// Had to modify bondget() due to the change in the bond structure
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
  *a1 = bond->a1;
  *a2 = bond->a2;
  *epairs = bond->epairs;
  *atoms = bond->atoms;
}

// This is a fantastic function and greatly simplifies the work needed in x_form and bond_ptrsCompare()
void compute_coords(bond *bond) {
  bond->x1 = bond->atoms[bond->a1].x;
  bond->y1 = bond->atoms[bond->a1].y;
  bond->x2 = bond->atoms[bond->a2].x;
  bond->y2 = bond->atoms[bond->a2].y;
  bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;
  bond->len = sqrt(((bond->x2 - bond->x1) * (bond->x2 - bond->x1)) + ((bond->y2 - bond->y1) * (bond->y2 - bond->y1)));
  bond->dx = (bond->x2 - bond->x1) / bond->len;
  bond->dy = (bond->y2 - bond->y1) / bond->len;
}

// dynamically allocating the molecule each time this function is called
molecule *molmalloc(unsigned short atom_max, unsigned short bond_max) {
  molecule *molPtr = malloc(sizeof(molecule));
  if (molPtr == NULL) {
    exit(1);
  }

  molPtr->atoms = malloc(sizeof(atom) * atom_max);
  if (molPtr->atoms == NULL) {
    exit(1);
  }

  molPtr->atom_ptrs = malloc(sizeof(atom *) * atom_max);
  if (molPtr->atom_ptrs == NULL) {
    exit(1);
  }

  molPtr->bonds = malloc(sizeof(bond) * bond_max);
  if (molPtr->bonds == NULL) {
    exit(1);
  }

  molPtr->bond_ptrs = malloc(sizeof(bond *) * bond_max);
  if (molPtr->bond_ptrs == NULL) {
    exit(1);
  }

  molPtr->atom_max = atom_max;
  molPtr->bond_max = bond_max;
  molPtr->atom_no = 0;
  molPtr->bond_no = 0;

  return molPtr;
}

// freeing memory to keep our hardware sane
void molfree(molecule *ptr) {
  free(ptr->atoms);
  free(ptr->bonds);
  free(ptr->atom_ptrs);
  free(ptr->bond_ptrs);
  free(ptr);
}

rotations *spin(molecule *mol) {
  rotations *molRot = NULL;
  printf("This function is a work-in-progress.\n");
  return molRot;
}

void rotationsfree(rotations *rotations) {
  free(rotations->x);
  free(rotations->y);
  free(rotations->z);
  free(rotations);
}

// Absolutely crucial functions, the append ones
void molappend_atom(molecule *molecule, atom *atom) {
  
  if (molecule->atom_no == molecule->atom_max) {
    if (molecule->atom_max == 0) {
      molecule->atom_max++;
      molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
      for (int ctr = 0; ctr < molecule->atom_no; ctr++) {
        molecule->atom_ptrs[ctr] = &molecule->atoms[ctr];
      }
      if (molecule->atoms == NULL) {
        exit(1);
      }
      molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
      if (molecule->atom_ptrs == NULL) {
        exit(1);
      }
    } else {
      molecule->atom_max = molecule->atom_max * 2;
      molecule->atoms = realloc(molecule->atoms, sizeof(struct atom) * molecule->atom_max);
      for (int ctr = 0; ctr < molecule->atom_no; ctr++) {
        molecule->atom_ptrs[ctr] = &molecule->atoms[ctr];
      }
      if (molecule->atoms == NULL) {
        exit(1);
      }
      molecule->atom_ptrs = realloc(molecule->atom_ptrs, sizeof(struct atom*) * molecule->atom_max);
      if (molecule->atom_ptrs == NULL) {
        exit(1);
      }
    }
  }

  memcpy(&(molecule->atoms[molecule->atom_no]), atom, sizeof(struct atom));
  molecule->atom_ptrs[molecule->atom_no] = &(molecule->atoms[molecule->atom_no]);
  molecule->atom_no++;
}

void molappend_bond(molecule *molecule, bond *bond) {

  if (molecule->bond_no == molecule->bond_max) {
    if (molecule->bond_max == 0) {
      molecule->bond_max++;
      molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
      for (int ctr = 0; ctr < molecule->bond_no; ctr++) {
        molecule->bond_ptrs[ctr] = &molecule->bonds[ctr];
      }
      if (molecule->bonds == NULL) {
        exit(1);
      }
      molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
      if (molecule->bond_ptrs == NULL) {
        exit(1);
      }
    } else {
        molecule->bond_max = molecule->bond_max * 2;
        molecule->bonds = realloc(molecule->bonds, sizeof(struct bond) * molecule->bond_max);
        for (int ctr = 0; ctr < molecule->bond_no; ctr++) {
          molecule->bond_ptrs[ctr] = &molecule->bonds[ctr];
        }
      if (molecule->bonds == NULL) {
        exit(1);
      }
      molecule->bond_ptrs = realloc(molecule->bond_ptrs, sizeof(struct bond*) * molecule->bond_max);
      if (molecule->bond_ptrs == NULL) {
        exit(1);
      }
    }
  }

  memcpy(&(molecule->bonds[molecule->bond_no]), bond, sizeof(struct bond));
  molecule->bond_ptrs[molecule->bond_no] = &(molecule->bonds[molecule->bond_no]);
  molecule->bond_no++;
}

// finally this function works as intended
molecule *molcopy(molecule *src) {
  molecule *cpyMol = molmalloc(src->atom_max, src->bond_max);
  if (cpyMol == NULL) {
    exit(1);
  }

  for (int ctr1 = 0; ctr1 < src->atom_no; ctr1++) {
    molappend_atom(cpyMol, &(src->atoms[ctr1]));
  }

  for (int ctr2 = 0; ctr2 < src->bond_no; ctr2++) {
    molappend_bond(cpyMol, &(src->bonds[ctr2]));
  }
  
  return cpyMol;
}

int atom_comp(const void *atomOne, const void *atomTwo) {
  double arithmResult;
  int cmpResult;

  struct atom **atomPtrOne = (struct atom **)atomOne;
  struct atom **atomPtrTwo = (struct atom **)atomTwo;

  arithmResult = (*atomPtrOne)->z - (*atomPtrTwo)->z;

  if (arithmResult == 0) {
    cmpResult = 0;
  } else if (arithmResult < 0) {
    cmpResult = -1;
  } else {
    cmpResult = 1;
  }

  return cmpResult;
}

// bond_ptrsCompare needs to be tested again just to make sure the new changes haven't broken it
int bond_comp(const void *bondOne, const void *bondTwo) {
  double arithmResult;
  int cmpResult;
  
  struct bond **bondPtrOne = (struct bond **)bondOne;
  struct bond **bondPtrTwo = (struct bond **)bondTwo;

  arithmResult = (*bondPtrOne)->z - (*bondPtrTwo)->z; // This function became much simpler because of compute_coords()

  if (arithmResult == 0) {
    cmpResult = 0;
  } else if (arithmResult < 0) {
    cmpResult = -1;
  } else {
    cmpResult = 1;
  }

  return cmpResult;
}

// our qsort function
void molsort(molecule *molecule) {
  qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom *), atom_comp);
  qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond *), bond_comp);
}

// the rotation functions are curcial for our transformations
void xrotation(xform_matrix xform_matrix, unsigned short deg) {
  double inputRad = deg * (M_PI / 180.0);

  xform_matrix[0][0] = 1;
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = 0;

  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = cos(inputRad);
  xform_matrix[1][2] = -1 * (sin(inputRad));

  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = sin(inputRad);
  xform_matrix[2][2] = cos(inputRad);
}

void yrotation(xform_matrix xform_matrix, unsigned short deg) {
  double inputRad = deg * (M_PI / 180.0);

  xform_matrix[0][0] = cos(inputRad);
  xform_matrix[0][1] = 0;
  xform_matrix[0][2] = sin(inputRad);

  xform_matrix[1][0] = 0;
  xform_matrix[1][1] = 1;
  xform_matrix[1][2] = 0;

  xform_matrix[2][0] = -1 * (sin(inputRad));
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = cos(inputRad);
}

void zrotation(xform_matrix xform_matrix, unsigned short deg) {
  double inputRad = deg * (M_PI / 180.0);

  xform_matrix[0][0] = cos(inputRad);
  xform_matrix[0][1] = -1 * (sin(inputRad));
  xform_matrix[0][2] = 0;

  xform_matrix[1][0] = sin(inputRad);
  xform_matrix[1][1] = cos(inputRad);
  xform_matrix[1][2] = 0;

  xform_matrix[2][0] = 0;
  xform_matrix[2][1] = 0;
  xform_matrix[2][2] = 1;
}

// we gotta modify mol_xform to work with the new bond structure using the new compute coordinates function above and fix the bugs in it
void mol_xform(molecule *molecule, xform_matrix matrix) {
  
  for (int ctr = 0; ctr < molecule->atom_no; ctr++) {
    double x = molecule->atoms[ctr].x;
    double y = molecule->atoms[ctr].y;
    double z = molecule->atoms[ctr].z;

    molecule->atoms[ctr].x = (matrix[0][0] * x) + (matrix[0][1] * y) + (matrix[0][2] * z);
    molecule->atoms[ctr].y = (matrix[1][0] * x) + (matrix[1][1] * y) + (matrix[1][2] * z);
    molecule->atoms[ctr].z = (matrix[2][0] * x) + (matrix[2][1] * y) + (matrix[2][2] * z);
  }

  // I think this is how the new modification for mol_xform is supposed to look like, but I gotta test it more later
  for (int ctr2 = 0; ctr2 < molecule->bond_no; ctr2++) {
    compute_coords(&(molecule->bonds[ctr2]));
  }
}
