/* STIS Target Acquisition Simulator				24-Mar-97
 *
 *	Filename:	tas_locate.c
 *
 *	Module name:	TAS target location
 *	Created:	16 Jan 1997 by RAShaw
 */

# if defined (IRAF_NATIVE_TASK)
#   define import_spp
#   define import_libc
#   define import_stdio
#   include <iraf.h>
# else
#   include <stdio.h>
# endif

# include <c_iraf.h>
# include <ximio.h>

# include <stdlib.h>
# include <string.h>
# include "tas_error.h"
# include "tas_struct.h"

# define LO			0
# define HI			1

extern InvokeMethod invokeMethod;

int getIrafImage (char *, int, IRAFPointer *, long int *, long int *, 
			double *, double *); 

void getIrafArray (IRAFPointer, int[], int[], float **); 

int getSubarrayBounds (int, int, int, long int, long int, int [], int []); 

float findBrightCheckbox (float *, int, int, int, float *, int *, int *); 

int calculateFluxCentroid (float *, int, int, float, float *, float *);


/* locateTarget - Locate the target in an image subsection.
 *
 *	I/O: ud		user data structure
 */

int locateTarget (UserData *ud)
{
	int		boundX[2];	/* X bounds of subarray */
	int		boundY[2];	/* Y bounds of subarray */
	float		brightest;	/* brightest checkbox flux */
	float		centroidX, centroidY; /* X,Y centroid within checkbox */
	long int	dim1, dim2;	/* input image dimensions */
	float		fluxThreshold;	/* min flux for FLUX_CENTROID algorithm */
	IRAFPointer 	in;		/* input image descriptor */
	float		*in_data;	/* ptr to input sub-array */
	InvokeMethod 	invokeMethod;	/* method of program invocation */
	int		targX, targY;	/* location of brightest pixel */
	char		s1[BUFSIZ];	/* generic */
	int		status;		/* return error code */

	status = 0;

	/* Open the image; get the descriptor, axis sizes & plate scales */
	status = getIrafImage (ud->fileName, ud->sizeSubImage, &in, &dim1, 
				&dim2, &ud->plateScaleX, &ud->plateScaleY); 

	switch (status) {
	    case IMAGE_NOT_FITS: 
	    	sprintf (s1, "Image %s must be FITS format.\n", ud->fileName);
	    	outputError (s1, IMAGE_NOT_FITS);
	    	return (status);

	    case IMAGE_ACCESS_ERROR: 
	    	sprintf (s1, "Unable to access image %s.\n", ud->fileName);
	    	outputError (s1, IMAGE_ACCESS_ERROR);
	    	return (status);

	    case IMAGE_OPEN_ERROR: 
	    	sprintf (s1, "Unable to open image %s.\n", ud->fileName);
	    	outputError (s1, IMAGE_OPEN_ERROR);
	    	return (status);

	    case IMAGE_TOO_SMALL: 
	    	sprintf (s1, "Image %s is too small.\n", ud->fileName);
	    	outputError (s1, IMAGE_TOO_SMALL);
	    	return (status);

	    case IMAGE_NOT_2D: 
	    	sprintf (s1, "Image %s not 2-dimensional.\n", ud->fileName);
	    	outputError (s1, IMAGE_NOT_2D);
	    	return (status);

	    case IMAGE_SCALE_UNDEFINED: 
	    	sprintf (s1, "%s %s \n", 
		    "Image plate scale is indeterminate:",
		    "may not be suitable for simulation.");
	    	strcpy (ud->warnings, s1);
	    	status = 0;
		break;

	    case IMAGE_SCALE_TOO_COARSE: 
	    	strcpy (ud->warnings, 
		    "Image plate scale is too coarse for simulation.\n");
	    	status = 0;
		break;

	    default:
		break;
	}

	/* Determine the subarray bounds */
	status = getSubarrayBounds (ud->sizeSubImage, ud->refPixelX, 
			ud->refPixelY, dim1, dim2, boundX, boundY); 

	if (status == IMAGE_READ_ERROR) {
	    sprintf (s1, "Unable to read image %s\n", ud->fileName);
	    c_imunmap (in);
	    outputError (s1, IMAGE_READ_ERROR);
	    return (status);

	} else if (status == IMAGE_TOO_SMALL) {
	    sprintf (s1, "Subarray for image %s is out of bounds.\n", 
		ud->fileName);
	    c_imunmap (in);
	    outputError (s1, IMAGE_TOO_SMALL);
	    return (status);
	}

	/* Read the image subarray */
	getIrafArray (in, boundX, boundY, &in_data);
	sprintf (s1, "[%d:%d,%d:%d]", 
		boundX[LO], boundX[HI], boundY[LO], boundY[HI]);
	strcat (ud->fileName, s1);

	/* Find the corner of the brightest checkbox, ensuring that it 
	   is valid. */
	brightest = findBrightCheckbox (in_data, ud->sizeSubImage, 
		ud->sizeSubImage, ud->sizeCheckbox, &ud->targetFlux, 
		&targY, &targX);

	if (brightest <= 0.) {
	    sprintf (s1, "Image %s has no flux.\n", ud->fileName);
	    c_imunmap (in);
	    outputError (s1, IMAGE_NO_FLUX);
	    return (IMAGE_NO_FLUX);
	}

	/* Convert the indexes of the corner in the subarray to the 
	location of the checkbox center in the full array */
	targX = (targX + (ud->sizeCheckbox / 2) + boundX[LO]);
	targY = (targY + (ud->sizeCheckbox / 2) + boundY[LO]);
	ud->targetX = (float)targX;
	ud->targetY = (float)targY;

	/* If needed, refine the brightest checkbox location with a 
	 * flux-weighted centroid. 
	 */
	if (ud->centerMethod == FLUX_CENTROID) {
	    fluxThreshold = 0.;
	    centroidX = 0.;
	    centroidY = 0.;

	    /* Determine the subarray bounds for the checkbox */
	    status = getSubarrayBounds (ud->sizeCheckbox, targX, targY, 
			dim1, dim2, boundX, boundY); 
	    if (status != 0) {
	    	printf ("Error code is %d\n", status);
	    	c_imunmap (in);
	    	return (status);
	    }
	    getIrafArray (in, boundX, boundY, &in_data);

	    /* Find the centroid within the checkbox. */
	    status = calculateFluxCentroid (in_data, ud->sizeCheckbox, 
			ud->sizeCheckbox, fluxThreshold, &centroidX, 
			&centroidY);

	    if (status == GEOMETRIC) {
	    	sprintf (s1, "%s %s\n", 
		"Insufficient counts for flux centroid calculation;", 
		"using GEOMETRIC center instead");
	    	strcat (ud->warnings, s1);

	    	ud->centerMethod = GEOMETRIC;
	    }

	    ud->targetX = centroidX + (float)boundX[LO];
	    ud->targetY = centroidY + (float)boundY[LO];
	}

	/* Close input image */
	c_imunmap (in);

	return (status);
}


/* getSubarrayBounds - 	Fetch appropriate image subsection boundaries.  
 *
 *	I: sizeArray	size of the (square) subarray
 *	I: refPixelX	location of the subarray center in X
 *	I: refPixelY	location of the subarray center in Y
 *	I: dim1, dim2	max array dimensions
 *	O: boundX	X bounding pixels of subarray
 *	O: boundY	Y bounding pixels of subarray
 */

int getSubarrayBounds (int sizeArray, int refPixelX, int refPixelY, 
			long int dim1, long int dim2, int boundX[], int boundY[])
{
	/* Determine the subarray bounds */
	boundX[LO] = refPixelX - (sizeArray / 2);
	boundX[LO] = boundX[LO] < 1 ? 1 : boundX[LO];
	boundX[HI] = boundX[LO] + sizeArray - 1;

	boundY[LO] = refPixelY - (sizeArray / 2);
	boundY[LO] = boundY[LO] < 1 ? 1 : boundY[LO];
	boundY[HI] = boundY[LO] + sizeArray - 1;

	/* Ensure subarray fits within full image */
	if (boundX[HI] > dim1 || boundY[HI] > dim2) 
	    return (IMAGE_TOO_SMALL);
	else
	    return (0);
}


