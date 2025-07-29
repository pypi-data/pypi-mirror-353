/* STIS Target Acquisition Simulator				24-Mar-97

	Filename:	tas_checkbox.c

	IRAF task name:	targacquire
	Created:	14 Jan 1997 by RAShaw
 */

# include "tas.h"

/* findBrightCheckbox - 
 *
 *	I: inputArray		pointer to the input array
 * 	I: nRows, nCols		X,Y size of input array
 * 	I: sizeCheckbox		size of the (square) checkbox
 *	O: maxFlux		Maximum flux within checkboxes
 *	O: maxFluxRow		row index for brightest checkbox
 *	O: maxFluxCol		col index for brightest checkbox
 *
 *  	12-Jan-1997 by RAShaw 
 *  
 *  DESCRIPTION: This function finds the brightest checkboxes within the 
	input image sub-array, and returns their locations and fluxes.  
	A checkbox of specified size is scanned over the
	collected image, moving 1 pixel at a time over cols then
	rows of the collected image, always staying wholly within the
	collected image. At each position of the checkbox, the
	sum of flux counts in the checkbox is accumulated.  This sum is 
	compared against the running maximum, and the global max and 
	the upper-left corner indices of the checkbox relative to the 
	collected image are updated when a new max is found.
 *
 *  NOTES:  Based on the STIS FSW routine CalculateFlux by Ira Becker
 */

float findBrightCheckbox (float *inputArray, int nRows, int nCols, 
			int sizeCheckbox, float *maxFlux, int *maxFluxRow, 
			int *maxFluxCol)
{
	int	cbRow, cbCol;	/* row, col indices for checkbox */
	int	inRow, inCol;	/* row, col indices for inputArray */
	int	ncbRows;	/* Number of rows of checkboxes */
	int	ncbCols;	/* Number of cols of checkboxes */
	int	row;		/* Current checkbox row */
	float	checkboxSum;	/* Accumulating checkbox flux sum */

#ifdef InArray
#undef InArray
#endif
	/* The following macro to allows inputArray to be referred to 
	as a 2-D array, with 'conventional' subscript notation. */
	# define InArray(x,y)  inputArray[nCols*(x) + (y)]

	/* Compute the number of rows and cols of checkboxes */
	ncbRows = nRows - sizeCheckbox + 1;
	ncbCols = nCols - sizeCheckbox + 1;

	/* Initialize max counts & location for all checkboxes in InputArray */
	*maxFlux    = 0.;
	*maxFluxRow = -1;
	*maxFluxCol = -1;

	/* Step thru the rows and columns of checkboxes */
	for (cbRow = 0; cbRow < ncbRows; cbRow++) {
	    for (cbCol = 0; cbCol < ncbCols; cbCol++) {
		checkboxSum = 0.;     

		/* Step thru the rows and columns of the input array 
		that lie within the current checkbox */
		for (inRow = 0; inRow < sizeCheckbox; inRow++) {
		    row = inRow + cbRow;
		    for (inCol = 0; inCol < sizeCheckbox; inCol++) {

			/* Accumulate flux within checkbox */
			checkboxSum += InArray(row, inCol + cbCol); 
		    }
		}

		/* Update new flux maximum & location within the subarray */
		if (checkboxSum > *maxFlux) {
		    *maxFlux = checkboxSum; 
		    *maxFluxRow = cbRow;
		    *maxFluxCol = cbCol;
		}
	    }
	}

	return (checkboxSum);
}


/* calculateFluxCentroid - 
 *
 *	I: inputArray		pointer to the input array
 * 	I: nCols		X size of input array
 * 	I: sizeCheckbox		size of the (square) checkbox
 *	I: fluxThreshold	Minimum flux within checkboxes
 *	O: colCentroid		column centroid of checkbox
 *	O: rowCentroid		row centroid of checkbox
 *
 *  	12-Jan-1997 by RAShaw 
 *  
	EXIT CONDITIONS:  The 5th and 6th parameters are pointers to
                          the row and column centroid calculated by this
                          function. The centroid coordinates are 
                          in units of pixels, relative
                          to (0,0) at the upper left corner of the 
                          *checkbox*. The calling function must add the row
                          and column indices of the upper left pixel of the
                          checkbox in the collected image to obtain the
                          centroid coordinates relative to (0,0) at the
                          upper left corner of the collected image.
                          The centroid type "geometric" or "flux weighted"
                          is stored in the science data header.   
        DESCRIPTION: This function calculates a flux-weighted centroid
	within a given checkbox within a collected image. 

	Before computing the flux-weighted centroid, this function
	checks the total flux within the checkbox. If it does not exceed 
	a scaled box-flux threshold, there is not enough flux in the 
	checkbox to perform a meaningful flux-weighted centroid, and the 
	geometric center of the checkbox is computed instead. 

 *  NOTES: Based on the STIS FSW routine Calculate_Flux_Wtd_Centroid_For_Locate 
 *	   by Ira Becker
**/

int calculateFluxCentroid (float *inputArray, int nCols, int sizeCheckbox, 
		float fluxThreshold, float *colCentroid, float *rowCentroid)

{
	float	rowMoment;	/* moment = mass*distance for rows
                                     within the checkbox */
	float	colMoment;	/* moment = mass*distance for cols 
                                     within the checkbox */
	float	mass;		/* The flux of a pixel within the checkbox */
	int	cbRow, cbCol;	/* Row and column indices within the checkbox */
	float	totalMass;	/* Total counts in checkbox */

#ifdef InArray
#undef InArray
#endif
	/* The following macro to allows inputArray to be referred to 
	as a 2-D array, with 'conventional' subscript notation. */
	# define InArray(x,y)  inputArray[nCols*(x) + (y)]

	/* Accumulate the total flux in the checkbox */ 
	totalMass = 0.;
	for (cbRow = 0; cbRow < sizeCheckbox; cbRow++) {
	    for (cbCol = 0; cbCol < sizeCheckbox; cbCol++) 
		totalMass += InArray(cbRow,cbCol); 
	}

	/* Determine if there is enough flux in the checkbox to perform a
	meaningful flux-weighted centroid. Compare the total mass in the
	checkbox with a (ground-patchable) box flux threshold which is
	scaled by the number of pixels in the checkbox. 

	NOTE the DEVIATION from FSW: check is against totalMass <= rather 
		than < to protect against divide by zero counts below. */

/*	if (totalMass < (fluxThreshold * sizeCheckbox * sizeCheckbox)) { */
	if (totalMass <= (fluxThreshold * sizeCheckbox * sizeCheckbox)) { 

	    /* Compute the geometric centroid of the checkbox instead. */
	    *rowCentroid = *colCentroid = (float)(sizeCheckbox - 1) / 2.0;
    
	    return (GEOMETRIC); 

	} else {

	    /* Compute the flux-weighted centroid */
	    rowMoment = colMoment = 0.0;

	    /* Accumulate row, column moments over checkbox */
	    for (cbRow = 0; cbRow < sizeCheckbox; cbRow++) {
		for (cbCol = 0; cbCol < sizeCheckbox; cbCol++) {

		    mass = InArray(cbRow,cbCol);
		    rowMoment += (float)cbRow * mass;
		    colMoment += (float)cbCol * mass;
		}
	    }

	    /* Compute row and column centroids */
	    *rowCentroid = rowMoment / totalMass;
	    *colCentroid = colMoment / totalMass;

	    return (FLUX_CENTROID); 
	}
}


