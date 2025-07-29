/* STIS Target Acquisition Simulator				06-Jan-99
 *
 *	Filename:	tas_getirafimage.c
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
# include <float.h>
# include <math.h>
# include "tas.h"
# include "tas_error.h"

# define IRAF_YES 1
# define IRAF_NO  0

# define LO	0
# define HI	1

extern InvokeMethod invokeMethod;

/* void iraferr (void); */

/* getIrafImage - 	Open an IRAF image and return its descriptor & image 
 *			dimensions. 
 *
 *	I: inName		input image name
 *	I: sizeSubImage		size of the needed subimage 
 *	O: in			IRAF image descriptor
 *	O: dim1, dim2		max array dimensions
 *	O: scaleX, scaleY	image plate scale
 */

int getIrafImage (char *inName, int sizeSubImage, IRAFPointer *in, 
		long int *dim1, long int *dim2, double *scaleX, double *scaleY) 
{
	int	n_dims;			/* no. of input image dimensions*/
	char	hostCommand[SZ_FNAME];
	char	remoteName[SZ_FNAME];
	char	*s1;

	strcpy (remoteName, inName);
	if (invokeMethod == WEB_PROGRAM) { 

	    /* Insist that the image format be FITS for Web program */
	    s1 = strstr (inName, "fit");
	    if (s1 == NULL)
	    	return (IMAGE_NOT_FITS);

	    else if ((int)strlen (s1) > 4)
	    	return (IMAGE_NOT_FITS);

	    sprintf (hostCommand, "%s %s %s/%s", 
		EXEC_FTP_TRANSFER, inName, TAS_FTP_PATH, inName);
	    system (hostCommand);
	    sprintf (remoteName, "%s/%s", TAS_FTP_PATH, inName);
	} 
/*	printf ("Finished ftp transfer of image: %s\n", remoteName); */

	/* Open the image; get the dimensionality & axis sizes */
	if (c_imaccess (remoteName, IRAF_READ_ONLY) != 1)
	    return (IMAGE_ACCESS_ERROR); 

	*in = c_immap (remoteName, IRAF_READ_ONLY, 0);

	if (c_iraferr() != 0) 
	    return (IMAGE_OPEN_ERROR);

	n_dims = c_imgndim (*in);
	if (n_dims != 2) {
	    c_imunmap (*in);
	    return (IMAGE_NOT_2D);
	}

	*dim1 = c_imglen (*in, 1);
	*dim2 = c_imglen (*in, 2);

	if (*dim1 < sizeSubImage || *dim2 < sizeSubImage) {
	    c_imunmap (*in);
	    return (IMAGE_TOO_SMALL);
	}

	/* Get image plate scale in arcsec/pixel */
	return (getImageScale (*in, scaleX, scaleY));
}


/* getIrafArray - 	Fetch a pointer to an IRAF image subsection and  
 *			reset negative values to zero. 
 *
 *	I: in		IRAF image descriptor
 *	I: boundX	X bounding pixels of subarray
 *	I: boundY	Y bounding pixels of subarray
 *	I/O: arrayPtr	ptr to fetched sub-array
 */

int getIrafArray (IRAFPointer in, int boundX[], int boundY[], float **arrayPtr) 
{
	int	sizeArr;	/* size of subarray */
	int	i;		/* generic */

	if (in == IRAF_NULL)
	    return (IMAGE_READ_ERROR);

	*arrayPtr = c_imgs2r (in, boundX[LO], boundX[HI], boundY[LO], 
				boundY[HI]);

	if (c_iraferr() != 0) 
	    return (IMAGE_READ_ERROR);

	sizeArr = (boundX[HI] - boundX[LO] + 1) * (boundY[HI] - boundY[LO] + 1);
	for (i = 0; i < sizeArr; i++) 
	    (*arrayPtr)[i] = (*arrayPtr)[i] < 0. ? 0. : (*arrayPtr)[i];

	return (0);
}


/* getImageScale - 	Determine the image plate scale.
 *
 *	I: in		IRAF image descriptor
 *	O: scaleX	X pixel scale
 *	O: scaleY	Y pixel scale
 */

# define DEGREE_TO_ARCSEC 3.6E+3

int getImageScale (IRAFPointer in, double *scaleX, double *scaleY) 
{
	double	cd1_1, cd2_1;		/* Elements of CD matrix */
	double	cd1_2, cd2_2;		/* Elements of CD matrix */

	/* Initialize */
	*scaleX = (double)0.;
	*scaleY = (double)0.;
	cd1_1 = (double)0.;
	cd2_1 = (double)0.;
	cd1_2 = (double)0.;
	cd2_2 = (double)0.;

	/* Assume header units are degree/pixel. */
	/* For X-coordinate, use CDELT convention... */
	if (c_imaccf (in, "CDELT1") == IRAF_YES)
	    *scaleX = c_imgetd (in, "CDELT1") * DEGREE_TO_ARCSEC;

	/* ...or CD matrix convention. */
	else {
	    if (c_imaccf (in, "CD1_1") == IRAF_YES)
	    	cd1_1 = c_imgetd (in, "CD1_1") * DEGREE_TO_ARCSEC;
	    if (c_imaccf (in, "CD2_1") == IRAF_YES)
	    	cd2_1 = c_imgetd (in, "CD2_1") * DEGREE_TO_ARCSEC;

	    *scaleX = sqrt ( pow (cd1_1, 2) + pow (cd2_1, 2) );
	}

	/* For Y-coordinate, use CDELT convention... */
	if (c_imaccf (in, "CDELT2") == IRAF_YES)
	    *scaleY = c_imgetd (in, "CDELT2") * DEGREE_TO_ARCSEC;

	/* ...or CD matrix convention. */
	else {
	    if (c_imaccf (in, "CD1_2") == IRAF_YES)
	    	cd1_2 = c_imgetd (in, "CD1_2") * DEGREE_TO_ARCSEC;
	    if (c_imaccf (in, "CD2_2") == IRAF_YES)
	    	cd2_2 = c_imgetd (in, "CD2_2") * DEGREE_TO_ARCSEC;

	    *scaleY = sqrt ( pow (cd1_2, 2) + pow (cd2_2, 2) );
	}

	/* If plate scale is indeterminate, or too coarse for a good 
	 * simulation, return the appropriate warning. */
	if (*scaleX > MAX_PS_FACTOR * STIS_CCD_PLATESCALE)
	    return (IMAGE_SCALE_TOO_COARSE);

	if (*scaleY > MAX_PS_FACTOR * STIS_CCD_PLATESCALE)
	    return (IMAGE_SCALE_TOO_COARSE);

	if (fabs (*scaleX) <= DBL_EPSILON || fabs (*scaleY) <= DBL_EPSILON)
	    return (IMAGE_SCALE_UNDEFINED);

	return (0);
}


