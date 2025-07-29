/* STIS Target Acquisition Simulator				24-Mar-97

	Filename:	tas_inputhtml.c

	Module name:	TAS input HTML
	Created:	16 Jan 1997 by RAShaw
 */

# include <ctype.h>
# include <stdio.h>
# include <stdlib.h>
# include "tas_struct.h"
# include "tas_error.h"


/* readHtmlInput - Populate the UserData structure from HTML input.
 *
 *	I/O: ud		user data structure
 */

void readHtmlInput (UserData *ud)
{
	char	value[SZ_KEYWD];

	/* Fetch image name */
	if (sscanf (getenv ("WWW_fileName"), "%s", &(ud->fileName)) == EOF)
	    outputError ("Invalid image name specified\n", 1); 

	/* Fetch location of subarray center */
	if (sscanf (getenv ("WWW_refPixelX"), "%d", &(ud->refPixelX)) == EOF) 
	    ud->refPixelX = 50;

	if (sscanf (getenv ("WWW_refPixelY"), "%d", &(ud->refPixelY)) == EOF) 
	    ud->refPixelY = 50;

	/* Fetch spatial extent of target */
	if (sscanf (getenv ("WWW_targetType"), "%s", value) != EOF) {
	    if (strcmp (value, "POINT") == 0)
	    	ud->targetType = POINT;

	    else if (strcmp (value, "DIFFUSE") == 0)
	    	ud->targetType = DIFFUSE;

	    else
	    	outputError ("Invalid target type specified", 1); 
	}

	/* Diffuse acquisitions use a user-specified checkbox, and determine 
	 * target location using a flux-weighted centroid. Point-source 
	 * acquisitions use a fixed, 3x3 checkbox. Validate the user input 
	 * in another routine */
	if (sscanf (getenv ("WWW_sizeCheckbox"), "%d", 
		    &(ud->sizeCheckbox)) == EOF)
	    ud->sizeCheckbox = 3.;

	/* Fetch choice of centering algorithm */
	if (sscanf (getenv ("WWW_centerMethod"), "%s", value) != EOF) {
	    if (strcmp (value, "FLUX_CENTROID") == 0)
	    	ud->centerMethod = FLUX_CENTROID;

	    else if (strcmp (value, "GEOMETRIC") == 0)
	    	ud->centerMethod = GEOMETRIC;

	    else
	    	outputError ("Invalid centering algorithm specified\n", 1); 
	}
}


/* getKeywordStr - Retrieve the value of a keyword as a string, given its name.
 *
 *	I: ud		user data structure
 *	I: keyword	string containing keyword
 *	I: value	string containing keyword value
 */

void getKeywordStr (UserData ud, const char *keyword, char *value)
{
	char	kwUpper[SZ_KEYWD];
	char 	*centerMethodName[] = { "GEOMETRIC", "FLUX_CENTROID" };
	char 	*targetTypeName[] = { "POINT", "DIFFUSE" };

	/* Case insensitive comparison */
	strcpy (kwUpper, keyword);
	strToUpper (kwUpper);

	/* Output requested structure member */
        value[0] = EOS;
	if (strcmp (kwUpper, "FILENAME") == 0)
	     sprintf (value, "%s", ud.fileName);

	else if (strcmp (kwUpper, "CENTERMETHOD") == 0)
	     sprintf (value, "%s", centerMethodName[ud.centerMethod]);

	else if (strcmp (kwUpper, "PLATESCALEX") == 0)
	     sprintf (value, "%.3f", ud.plateScaleX);

	else if (strcmp (kwUpper, "PLATESCALEY") == 0)
	     sprintf (value, "%.3f", ud.plateScaleY);

	else if (strcmp (kwUpper, "REFPIXELX") == 0)
	     sprintf (value, "%d", ud.refPixelX);

	else if (strcmp (kwUpper, "REFPIXELY") == 0)
	     sprintf (value, "%d", ud.refPixelY);

	else if (strcmp (kwUpper, "SIZESUBIMAGE") == 0)
	     sprintf (value, "%d", ud.sizeSubImage);

	else if (strcmp (kwUpper, "SIZECHECKBOX") == 0)
	     sprintf (value, "%d", ud.sizeCheckbox);

	else if (strcmp (kwUpper, "TARGETTYPE") == 0)
	     sprintf (value, "%s", targetTypeName[ud.targetType]);

	else if (strcmp (kwUpper, "TARGETFLUX") == 0)
	     sprintf (value, "%10.5f", ud.targetFlux);

	else if (strcmp (kwUpper, "TARGETX") == 0)
	     sprintf (value, "%10.3f", ud.targetX);

	else if (strcmp (kwUpper, "TARGETY") == 0)
	     sprintf (value, "%10.3f", ud.targetY);

	else if (strcmp (kwUpper, "VERSION") == 0)
	     sprintf (value, "%s", ud.version);

	else if (strcmp (kwUpper, "WARNINGS") == 0)
	     sprintf (value, "%s", ud.warnings);

	else
	     sprintf (value, "%s", " ");

}
 

/* strToUpper -	Convert the input string to upper case.
 *
 *	I/O: s1		string to be converted in-place
 */

void strToUpper (char *s1)
{
	int	i, nchar;

	nchar = strlen(s1);
	for (i = 0; i <= nchar; i++)
	    s1[i] = toupper(s1[i]);
}


