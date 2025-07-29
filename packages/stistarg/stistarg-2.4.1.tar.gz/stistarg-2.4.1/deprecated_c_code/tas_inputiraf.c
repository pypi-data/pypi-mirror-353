/* STIS Target Acquisition Simulator				27-Jan-97
 *
 *	Filename:	tas_inputiraf.c
 *
 *	Module name:	TAS input HTML
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
# include <xclio.h>
# include <stdlib.h>
# include <string.h>
# include "tas_error.h"
# include "tas_struct.h"

extern InvokeMethod invokeMethod;


/* getUserPars - Get user input parameters from IRAF STDIN.
 *
 *	I/O: ud		user data structure
 */

void getUserPars (UserData *ud) 
{
	char	value[SZ_KEYWD];

	/* Fetch file names */
	c_clgstr ("Input image name", ud->fileName, BUFSIZ);

	/* Fetch subarray location */
	ud->refPixelX = c_clgeti ("Center of subarray in X");
	ud->refPixelY = c_clgeti ("Center of subarray in Y");

	/* Fetch target type */
	c_clgstr ("Target type (POINT or DIFFUSE)", value, BUFSIZ);

	strToUpper (value);
	if (strcmp (value, "POINT") == 0)
	    ud->targetType = POINT;

	else if (strcmp (value, "DIFFUSE") == 0)
	    ud->targetType = DIFFUSE;

	else
	    outputError ("Invalid target type specified\n", 1); 

	/* Checkbox size and centering method depend upon the target type. */

	if (ud->targetType == POINT) {

	    /* Point-source acquisitions use a fixed, 3x3 checkbox 
	     * and determine target location using a flux-weighted 
	     * centroid. */
	    ud->sizeCheckbox = POINT_CHECKBOX_SIZE;
	    ud->centerMethod = FLUX_CENTROID; 
	    ud->sizeSubImage = POINT_SUBIMAGE_SIZE;

	} else if (ud->targetType == DIFFUSE) {

	    /* Diffuse acquisitions use a user-specified checkbox and 
	     * determine target location using either the brightest 
	     * checkbox, or a flux-weighted centroid. */
	    ud->sizeCheckbox = c_clgeti ("Checkbox size");
	    ud->sizeSubImage = DIFFUSE_SUBIMAGE_SIZE + ud->sizeCheckbox;

	    c_clgstr ("Centering algorithm (GEOMETRIC or FLUX_CENTROID)", 
				value, BUFSIZ);

	    strToUpper (value);
	    if (strcmp (value, "FLUX_CENTROID") == 0)
	    	ud->centerMethod = FLUX_CENTROID;

	    else if (strcmp (value, "GEOMETRIC") == 0)
	    	ud->centerMethod = GEOMETRIC;

	    else
	        outputError ("Invalid centering algorithm specified\n", 1); 
	}
}


/* getIrafPars - Get user input parameters from IRAF CL.
 *
 *	I/O: ud		user data structure
 */

void getIrafPars (UserData *ud) 
{
	char	value[SZ_KEYWD];

	/* Fetch image file name */
	c_clgstr ("inname", ud->fileName, BUFSIZ);

	/* Fetch subarray location */
	ud->refPixelX = c_clgeti ("x_center");
	ud->refPixelY = c_clgeti ("y_center");

	/* Fetch target type */
	c_clgstr ("targtype", value, BUFSIZ);

	strToUpper (value);
	if (strcmp (value, "POINT") == 0)
	    ud->targetType = POINT;

	else if (strcmp (value, "DIFFUSE") == 0)
	    ud->targetType = DIFFUSE;

	else
	    outputError ("Invalid target type specified\n", 1); 

	/* Diffuse acquisitions use a user-specified checkbox, and determine 
	 * target location using a flux-weighted centroid. Point-source 
	 * acquisitions use a fixed, 3x3 checkbox. Validate the user input 
	 * in another routine */
	ud->sizeCheckbox = c_clgeti ("ckboxsize");

	/* Fetch choice of centering algorithm */
	c_clgstr ("cntrmethod", value, BUFSIZ);

	strToUpper (value);
	if (strcmp (value, "FLUX_CENTROID") == 0)
	    ud->centerMethod = FLUX_CENTROID;

	else if (strcmp (value, "GEOMETRIC") == 0)
	    ud->centerMethod = GEOMETRIC;

	else
	    outputError ("Invalid centering algorithm specified\n", 1); 
}


# define  IsEven(x)  ( ((x/2) * 2) == x )

/* validateInput - Validate the parameters in the user data structure.
 *
 *	I/O: ud		user data structure
 */

int validateInput (UserData *ud)
{
	int	boxSize;	/* checkbox size (temp) */

	/* Set checkbox size, centering method, and subimage size based on 
	 * target type */
	if (ud->targetType == POINT) {

	    /* Point-source acquisitions use a fixed, 3x3 checkbox 
	     * and determine target location using a flux-weighted 
	     * centroid. */
	    ud->sizeCheckbox = POINT_CHECKBOX_SIZE;
	    ud->centerMethod = FLUX_CENTROID; 
	    ud->sizeSubImage = POINT_SUBIMAGE_SIZE;

	} else if (ud->targetType == DIFFUSE) {

	    /* Diffuse acquisitions use a user-specified checkbox and 
	     * determine target location using either the brightest 
	     * checkbox, or a flux-weighted centroid. */
	    ud->sizeSubImage = DIFFUSE_SUBIMAGE_SIZE + ud->sizeCheckbox;
	}

	boxSize = ud->sizeCheckbox;
	if ( IsEven (boxSize) || boxSize < POINT_CHECKBOX_SIZE || 
		boxSize > MAX_CHECKBOX_SIZE)
	    outputError ("Invalid checkbox size specified\n", 1); 

	/* Initialize other structure elements */
	strcpy (ud->version, TAS_VERSION); 
 	ud->plateScaleX = (double)0.;
	ud->plateScaleY = (double)0.;
	ud->targetFlux = 0.;
	ud->targetX = 0.;
	ud->targetY = 0.;

	/* Initialize the warnings buffer */
	strcpy (ud->warnings, "None.");

	return (0);
}


