/* STIS Target Acquisition Simulator				24-Jan-97
 *
 *	Filename:	tas_error.c
 *
 *	Module:		TAS invocation-dependent output routines
 *	Created:	16 Jan 1997 by RAShaw
 */

# include <stdio.h>
# include <string.h>
# include "tas.h"
# include "tas_error.h"

void outputHTMLError (const char *errMsg);

extern InvokeMethod invokeMethod;

/* outputError - 	Write an error message to the output stream, formatted 
 *			either as HTML or ASCII text.
 *
 *	I: errMsg		text of error message
 *	I: status		error code
 */

void outputError (const char *errMsg, int status)
{
	if (invokeMethod == WEB_PROGRAM) 
	    outputHTMLError (errMsg);

	else
	    printf ("ERROR: %s\n", errMsg);

	exit (status);
}


/* outputHTMLError - 	Write an error message to the output stream, formatted 
 *			as HTML.
 *
 *	I: errMsg		text of error message
 */

void outputHTMLError (const char *errMsg)
{
	/* Output HTTP prologue */
	printf ("Content-type: text/html\n\n");

	/* Output HTML header */
	printf ("<HTML><HEAD><TITLE>\n");
	printf ("STIS Target Acquisition Simulator ERROR\n");
	printf ("</TITLE></HEAD>\n");
	printf ("<BODY >\n");
	printf ("<H1>STIS Target Acquisition Simulator ERROR</H1>\n");

	/* Output error message and pointer back to TAS page */
	printf ("%s\n", errMsg);
	printf ("<P>Return to the <A HREF=\"%s\">STIS Target Acquisition Simulator</A>\n",
		TAS_URL);

	/* Conclude with HTML footer */
	printf ("</BODY></HTML>\n");
}


