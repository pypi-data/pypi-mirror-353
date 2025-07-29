/* STIS Target Acquisition Simulator				22-Jan-97
 *
 *	Filename:	tas_main.c
 *
 *	IRAF task name:	targacquire
 *	Created:	14 Jan 1997 by RAShaw
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
# include <stdlib.h>
# include <string.h>
# include "tas_struct.h"
# include "tas_error.h"

/* Global variable */
InvokeMethod 	invokeMethod;	/* method of program invocation */

/* Function prototypes */
InvokeMethod getInvokeMethod (void); 

void uncgi (void);

int readUserInput (UserData *); 

void readHtmlInput (UserData *);

void getUserPars (UserData *); 

void getIrafPars (UserData *);

int validateInput (UserData *);

int locateTarget (UserData *);

void outputResults (UserData);

void iraferr () 
{
	printf ("IRAF error code %d \nIRAF message: %s\n", 
		c_iraferr(), c_iraferrmsg()); 
	exit(0);
}

# if defined (IRAF_NATIVE_TASK)
IRAFTASK (targacquire) 
# else
int main (int argc, char **argv) 
# endif
{
	int		status;		/* return error code */
	UserData	ud;		/* structure for user parameters */

	/* IRAF initialization */
	c_irafinit (argc, argv);

	/* Install the error handler */
	c_pusherr (iraferr);

	/* Determine the invocation method */
	uncgi();
	invokeMethod = getInvokeMethod (); 

	/* Get user parameters */
	status = readUserInput (&ud);
	if (status != 0)
	    outputError ("Problem reading user input\n", status);

	/* Find the target(s) in the image */
	status = locateTarget (&ud);
	if (status > FLUX_CENTROID)
	    outputError ("Target location failed\n", status);

	/* Output results of calculation */
	outputResults (ud);

	return (0);
}


/* getInvokeMethod - Determine how this program was invoked.
 */

InvokeMethod getInvokeMethod () 
{
	if (getenv ("REQUEST_METHOD") != NULL) 
	    return (WEB_PROGRAM);

	else if (os_host_task)
	    return (OS_PROGRAM);

	else
	    return (IRAF_PROGRAM);

}


/* readUserInput - Fetch user input in invocation-dependent way.
 *
 *	I: ud		user data structure
 */

int readUserInput (UserData *ud) 
{
	if (invokeMethod == WEB_PROGRAM)
	    readHtmlInput (ud);

	else if (invokeMethod == OS_PROGRAM)
	    getUserPars (ud);

	else if (invokeMethod == IRAF_PROGRAM)
	    getIrafPars (ud);

	return (validateInput (ud)); 
}


/* outputResults - Output the results to an HTML file, or to STDOUT.
 *
 *	I: ud		user data structure
 */

void outputResults (UserData ud) 
{
	if (invokeMethod == OS_PROGRAM) 
	    outputASCII (ud); 
/*	    outputHTML (ud); */

	else if (invokeMethod == IRAF_PROGRAM)
	    outputASCII (ud);

	else if (invokeMethod == WEB_PROGRAM)
	    outputHTML (ud);
}


