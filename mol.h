#ifndef _MOL_H_
#define _MOL_H_

#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdio.h>

struct atom {
	char element[3];
	double x, y, z;
};

struct bond {
	unsigned short a1;
	unsigned short a2;
	struct atom *atoms;
	unsigned char epairs;
	double x1, x2, y1, y2, z, len, dx, dy;
};

struct molecule {
	unsigned short atom_max, atom_no;
	struct atom *atoms, **atom_ptrs;
	unsigned short bond_max, bond_no;
	struct bond *bonds, **bond_ptrs;
};

double xform_matrix[3][3];

struct mx_wrapper {
	double xform_matrix;
};

struct rotations {
	struct molecule *x[72];
	struct molecule *y[72];
	struct molecule *z[72];
};

void atomset(struct atom *atom, char element[3], double *x, double *y, double *z);
void atomget(struct atom *atom, char element[3], double *x, double *y, double *z);
void bondset(struct bond *bond, unsigned short *a1, unsigned short *a2, struct atom **atoms, unsigned char *epairs);
void bondget(struct bond *bond, unsigned short *a1, unsigned short *a2, struct atom **atoms, unsigned char *epairs);
void compute_coords(struct bond *bond);
struct molecule *molmalloc(unsigned short atom_max, unsigned short bond_max);
struct molecule *molcopy(struct molecule *src);
void molfree(struct molecule *ptr);
void molappend_atom(struct molecule *molecule, struct atom *atom);
void molappend_bond(struct molecule *molecule, struct bond *bond);
void molsort(struct molecule *molecule);
void xrotation(double xform_matrix[3][3], unsigned short deg);
void yrotation(double xform_matrix[3][3], unsigned short deg);
void zrotation(double xform_matrix[3][3], unsigned short deg);
void mol_xform(struct molecule *molecule, double matrix[3][3]);

#endif
