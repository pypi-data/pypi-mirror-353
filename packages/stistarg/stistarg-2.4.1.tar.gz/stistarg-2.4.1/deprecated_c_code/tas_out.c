/* STIS Target Acquisition Simulator				24-Jan-97

	Filename:	tas_out.c

	Module:		TAS invocation-dependent output routines
	Created:	16 Jan 1997 by RAShaw
 */

# include <stdio.h>
# include <string.h>
# include "tas_error.h"
# include "tas_struct.h"

/* Template HTML file used for formatted output */
char	*templateFile = "tas_tmpl.html";

void outputASCII (UserData);
 
void outputHTML (UserData);

void parseLine (UserData, const char *, char *);

void getKeyword (char *, char *, char *);


/* outputASCII - Output the results to STDOUT as ASCII formatted text.
 *
 *	I: ud		user data structure
 */

void outputASCII (UserData ud) 
{
	char	s1[BUFSIZ];	/* generic */

	printf ("\n    STIS Target Acquisition Simulation\n");
	printf ("         %s\n\n", ud.version);
	printf ("         Image subarray: %s\n", ud.fileName); 

	printf ("       Plate scale in X: %.3f; in Y: %.3f (arcsec/pixel)\n", 
					ud.plateScaleX, ud.plateScaleX); 

	getKeywordStr (ud, "TARGETTYPE", s1);
	printf ("         Target type is: %s\n", s1); 

	getKeywordStr (ud, "CENTERMETHOD", s1);
	printf ("    Centering method is: %s\n", s1); 
	printf ("Brightest checkbox flux: %f\n", ud.targetFlux);

	s1[0] = EOS;
	if (ud.centerMethod == GEOMETRIC) 
	    strcpy (s1, "       Geometric center: %s %4.0f %s %4.0f\n"); 

	else if (ud.centerMethod == FLUX_CENTROID)
	    strcpy (s1, "          Flux centroid: %s %f %s %f\n"); 

	printf (s1, "x =", ud.targetX, "; y =", ud.targetY); 

	if ((int)strlen (ud.warnings) > 0)
	    printf ("\nWarning: %s\n", ud.warnings);
}


/* outputHTML -	Output the results to an HTML file, given an HTML template.
 *
 *	I: ud		user data structure
 */

void outputHTML (UserData ud)
{
        char	errMsg[SZ_LINE];
	FILE	*filePtr;
        char	outputLine[SZ_LINE];
        char	textLine[SZ_LINE];

	/* Open HTML output template file */
	if ( (filePtr = fopen (templateFile, "r")) != NULL ) {

	    /* Output HTTP prologue */
	    printf ("Content-type: text/html\n\n");

	    /* Output each line of the output template, substituting keywords */
	    while ( fgets (textLine, SZ_LINE, filePtr) != NULL ) {
		parseLine (ud, textLine, outputLine);
		printf ("%s", outputLine);   
		textLine[0] = EOS;
	    }

	    fclose (filePtr);

	} else {

	    /* Output HTML error message */
	    sprintf (errMsg, 
		"ERROR: HTML template file `%s' could not be opened.", 
		templateFile);
	    outputError (errMsg, 1);
	}
}


/* parseLine - 	Parse a newline-terminated string, substituting keyword 
 *		values for keyword names.  
 *
 *	I: ud		user data structure
 *	I: inStr	input string
 *	O: outStr	string with keyword substitutions
 */

void parseLine (UserData ud, const char *inStr, char *outStr)
{

	char	keywordValue[SZ_KEYWD];
	char	keyword[SZ_KEYWD];
	int	nc;
	char	wStr[SZ_LINE];

	outStr[0] = EOS;
	strcpy (wStr, inStr);

	/* Find and replace keywords in the string */
	while (wStr[0] != EOS) {

	    keyword[0] = EOS;
	    getKeyword (wStr, keyword, outStr);
	    if (keyword[0] != EOS) {
		getKeywordStr (ud, keyword, keywordValue);
 		strcat (outStr, keywordValue);
	    }
	} 
}


/* getKeyword - Append to string s2 characters in s1 up to but not including 
 * 		the keyword delimitor, and append the name of the keyword to 
 *		the keyword string.  
 *
 *	I/O: s1		input string
 *	O: keyword	string containing keyword
 *	O: s2		input string up to found keyword
 */

void getKeyword (char *s1, char *keyword, char *s2)
{
	char	*leftDelim = "-*";
	char	*rightDelim = "*-";
	char	wStr[SZ_LINE];
	int	sz_wStr, sz_str, i, nchar;

	wStr[0] = EOS;
	keyword[0] = EOS;

/*	printf ("Looking for left delimitor\n");
 */
	/* Find the keyword delimiter */
	if (strstr (s1, leftDelim) != NULL) {

	    /* If present, copy remainder string to a working array... */
	    strcpy (wStr, strstr (s1, leftDelim));
	    sz_wStr = strlen (wStr);

	} else {
	    /* ...otherwise transfer s1 to s2 and return */
	    strcat (s2, s1);
	    s1[0] = EOS;
	    return;
	}
 
	/* Append s1 to s2 up to the delimiter */
	nchar = strlen (s1) - sz_wStr;
        sz_str = strlen (s2);
	strncat (s2, s1, nchar);
	s2[sz_str+nchar+1] = EOS;
 
	/* Trim leading delimiter and place in s1 */
	nchar = strlen(leftDelim);
	for (i = 0; i <= sz_wStr-nchar; i++) { 
	    s1[i] = wStr[i+nchar];  
	}

	/* Extract the keyword name */
	if (strstr (s1, rightDelim) != NULL) {
	    strcpy (wStr, strstr (s1, rightDelim));
	    sz_wStr = strlen (wStr);

	} else {
	    printf ("Missing right keyword delimitor!\n");
	    return;
	}
 
	/* Append s1 to keyword up to the delimiter */
	nchar = strlen (s1) - sz_wStr;
	strncat (keyword, s1, nchar);
	keyword[nchar+1] = EOS;
 
	/* Trim leading delimiter from s1 */
	nchar = strlen(rightDelim);
	for (i = 0; i <= sz_wStr-nchar; i++)
	    s1[i] = wStr[i+nchar];
}


