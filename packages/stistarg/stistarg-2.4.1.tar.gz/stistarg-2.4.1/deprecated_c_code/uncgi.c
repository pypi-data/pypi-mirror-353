/*
 * @(#)uncgi.c	1.27 03/19/96
 *
 * Unescape all the fields in a form and stick them in the environment
 * so they can be used without awful machinations.
 *
 * Call with an ACTION such as:
 *	http://foo.bar.com/cgi-bin/uncgi/myscript/extra/path/stuff
 *
 * Uncgi will run "myscript" from the cgi-bin directory, and set PATH_INFO
 * to "/extra/path/stuff".
 *
 * Environment variable names are "WWW_" plus the field name.
 *
 * Copyright 1994, Steven Grimm <koreth@hyperion.com>.
 *
 * Permission is granted to redistribute freely and use for any purpose,
 * commercial or private, so long as this copyright notice is retained
 * and the source code is included free of charge with any binary
 * distributions.
 */
#include <stdio.h>
#include <ctype.h>
#include <string.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <stdlib.h>

#define VERSION "1.7"

#ifdef __TURBOC__
#include <process.h>
#pragma warn -pro
#endif

#ifdef __STDC__
#define NOPARAMS void
#else
#define NOPARAMS /**/
#endif

#ifndef __bsdi__
extern char *sys_errlist[];
#endif
extern int errno;

#define PREFIX	"WWW_"
#define ishex(x) (((x) >= '0' && (x) <= '9') || ((x) >= 'a' && (x) <= 'f') || \
		  ((x) >= 'A' && (x) <= 'F'))


/* Define some directory macros for systems that don't have them. */
#ifndef S_IFDIR
# define S_IFDIR 040000
#endif

#ifndef S_ISDIR
# define S_ISDIR(x) ((x & 0170000) == S_IFDIR)
#endif

char *id = "@(#)uncgi.c	1.27 03/19/96";

/*
 * Convert two hex digits to a value.
 */
static int
htoi(s)
	unsigned char	*s;
{
	int	value;
	char	c;

	c = s[0];
	if (isupper(c))
		c = tolower(c);
	value = (c >= '0' && c <= '9' ? c - '0' : c - 'a' + 10) * 16;

	c = s[1];
	if (isupper(c))
		c = tolower(c);
	value += c >= '0' && c <= '9' ? c - '0' : c - 'a' + 10;

	return (value);
}

/*
 * Get rid of all the URL escaping in a string.  Modify it in place, since
 * the result will always be equal in length or smaller.
 */
static void
url_unescape(str)
	unsigned char	*str;
{
	unsigned char	*dest = str;

	while (str[0])
	{
		if (str[0] == '+')
			dest[0] = ' ';
		else if (str[0] == '%' && ishex(str[1]) && ishex(str[2]))
		{
			dest[0] = (unsigned char) htoi(str + 1);
			str += 2;
		}
		else
			dest[0] = str[0];

		str++;
		dest++;
	}

	dest[0] = '\0';
}

/*
 * Print the start of an error message.
 */
static void
http_head(NOPARAMS)
{
	puts("Content-type: text/html\n");
	puts("<html><head><title>Error!</title></head><body>");
	puts("<h1>An error has occurred while processing your request.</h1>");
}

/*
 * Print a standard tagline for Un-CGI error messages.
 */
static void
uncgi_tag(NOPARAMS)
{
	printf("<pre>\n\n\n\n\n\n\n</pre><cite><a href=\"http://www.");
	printf("hyperion.com/~koreth/uncgi.html\">Un-CGI %s", VERSION);
	puts("</a></cite>\n</body></html>");
}

/*
 * Print an HTML error string with the right HTTP header and exit.
 */
static void
html_perror(str)
	char	*str;
{
	http_head();

	puts("<p>The following error was encountered while processing");
	puts("your query.");
	puts("<blockquote>");
	printf("%s: %s\n", str, sys_errlist[errno]);
	puts("</blockquote>");
	puts("<p>Please try again later.");
	uncgi_tag();

	exit(1);
}

/*
 * Stuff a URL-unescaped variable, with the prefix on its name, into the
 * environment.  Uses the "=" from the CGI arguments.  Putting an "=" in
 * a field name is probably a bad idea.
 *
 * If the variable is already defined, append a '#' to it along with the
 * new value.
 *
 * If the variable name begins with an underline, strip whitespace from the
 * start and end and normalize end-of-line characters.
 */
static void
stuffenv(var)
	char	*var;
{
	char	*buf, *c, *s, *t, *oldval, *newval;
	int	despace = 0, got_cr = 0;

	url_unescape(var);

	/*
	 * Allocate enough memory for the variable name and its value.
	 */
	buf = malloc(strlen(var) + sizeof(PREFIX) + 1);
	if (buf == NULL)
		html_perror("stuffenv");

	strcpy(buf, PREFIX);
	if (var[0] == '_')
	{
		strcpy(buf + sizeof(PREFIX) - 1, var + 1);
		despace = 1;
	}
	else
		strcpy(buf + sizeof(PREFIX) - 1, var);

	/*
	 * If, for some reason, there wasn't an = in the query string,
	 * add one so the environment will be valid.
	 *
	 * Also, change periods to spaces so folks can get at "image"
	 * input fields from the shell, which has trouble with periods
	 * in variable names.
	 */
	for (c = buf; *c != '\0'; c++)
	{
		if (*c == '.')
			*c = '_';
		if (*c == '=')
			break;
	}
	if (*c == '\0')
		c[1] = '\0';

	/*
	 * Do whitespace stripping, if applicable.  Since this can only ever
	 * shorten the value, it's safe to do in place.
	 */
	if (despace && c[1])
	{
		for (s = c + 1; *s && isspace(*s); s++)
			;
		t = c + 1;
		while (*s)
		{
			if (*s == '\r')
			{
				got_cr = 1;
				s++;
				continue;
			}
			if (got_cr)
			{
				if (*s != '\n')
					*t++ = '\n';
				got_cr = 0;
			}
			*t++ = *s++;
		}

		/* Strip trailing whitespace if we copied anything. */
		while (t > c && isspace(*--t))
			;
		t[1] = '\0';
	}

	/*
	 * Check for the presence of the variable.
	 */
	*c = '\0';
	if ((oldval = getenv(buf)))
	{
		newval = malloc(strlen(oldval) + strlen(buf) + strlen(c+1) + 3);
		if (newval == NULL)
			html_perror("stuffenv: append");
		
		*c = '=';
		strcpy(newval, buf);
		*c = '\0';

		strcat(newval, "#");
		strcat(newval, oldval);

		/*
		 * Free the entire old environment variable -- there really
		 * ought to be a library function for this.  It's safe to
		 * free here since the only place these variables come from
		 * is a previous call to this function; we can never be
		 * freeing a system-supplied environment variable.
		 */
		oldval -= strlen(buf) + 1; /* skip past VAR= */
		free(oldval);
		free(buf);
	}
	else
	{
		*c = '=';
		newval = buf;
	}

	putenv(newval);
}

/*
 * Scan a query string, stuffing variables into the environment.  This
 * should ideally just use strtok(), but that's not available everywhere.
 */
static void
scanquery(q)
	char	*q;
{
	char	*next = q;

	do {
		while (*next && *next != '&')
			next++;
		if (! *next)
			next = NULL;
		else
			*next = '\0';
		
		stuffenv(q);
		if (next)
			*next++ = '&';
		q = next;
	} while (q != NULL);
}

/*
 * Read a POST query from standard input into a dynamic buffer.  Terminate
 * it with a null character.
 */
static char *
postread(NOPARAMS)
{
	char	*buf = NULL;
	int	size = 0, sofar = 0, got;

	buf = getenv("CONTENT_TYPE");
	if (buf == NULL || strcmp(buf, "application/x-www-form-urlencoded"))
	{
		http_head();
		puts("<p>No content type was passed to uncgi.");
		uncgi_tag();
		exit(1);
	}

	buf = getenv("CONTENT_LENGTH");
	if (buf == NULL)
	{
		http_head();
		puts("<p>The server did not tell uncgi how long the request");
		puts("was.");
		uncgi_tag();
		exit(1);
	}
	
	size = atoi(buf);
	buf = malloc(size + 1);
	if (buf == NULL)
		html_perror("postread");
	do
	{
		got = fread(buf + sofar, 1, size - sofar, stdin);
		sofar += got;
	} while (got && sofar < size);

	buf[sofar] = '\0';

	return (buf);
}

/*
 * Run a shell script.  We use this instead of the OS's "#!" mechanism
 * because that mechanism doesn't work too well on SVR3-based systems.
 */
void
runscript(shell, script)
    char    *shell, *script;
{
	char    *argvec[4], **ppArg = argvec, *pz;

	/*
	 *  "shell" really points to the character following the "#!",
	 *  not to the name of the shell program to run.  Skip any
	 *  leading white space.
	 */
	while (isspace( *shell ))
		shell++;

	/*
	 *  We only run the shell if there is a full path name.
	 */
	if (*shell != '/')
		return;

	*ppArg++ = shell;

	pz = shell;
	while ((*pz != '\0') && (! isspace( *pz ))) {
		pz++;
	}

#ifdef DEBUG
	printf("Skipped whitespace\n");
	fflush(stdout);
#endif

	/*
	 *  We have found the end of the command.
	 *  Clip off the trailing white space.
	 */
	if (*pz != '\0') {
		*pz++ = '\0';
		while (isspace( *pz ))
			pz++;

#ifdef DEBUG
		printf("Stripped shell is '%s', args are '%s'\n", shell, pz);
		fflush(stdout);
#endif

		/*
		 * If anything follows the command *AND* what follows is
		 * not a comment, then insert it into the command argument
		 * vect.
		 */

		if ((*pz != '\0') && (*pz != '#')) {
			*ppArg++ = pz;

			/*
			 *  Trim off anything after the first white space char.
			 */
			while ((*pz != '\0') || (! isspace( *pz ))) {
				pz++;
			}

			*pz = '\0';
		}
	}

	*ppArg++ = script;
	*ppArg   = (char*)NULL;

#ifdef DEBUG
	if (argvec[2] == NULL)
		printf("Executing '%s %s'\n\n", argvec[0], argvec[1]);
	else
		printf("Executing '%s %s %s'\n\n", argvec[0], argvec[1],
			argvec[2]);
	fflush(stdout);
#endif

	execv(shell, argvec);
	/* Fall back to main() on error. */
}

/*
 * Main program, optionally callable as a library function.
 */
void
uncgi(NOPARAMS)
{
	char	*query, *program, *pathinfo, *newpathinfo, *method;
	char	*scriptname, *newscriptname;
	char	*ptrans, *ptend;
	char	*argvec[2], shellname[200];
	int	proglen;
	FILE	*fp;

#ifdef DEBUG
	printf("Content-type: text/plain\n\nUn-CGI %s (%s), debug mode\n",
		VERSION, id);
	fflush(stdout);
#endif

	/*
	 * First, get the query string, wherever it is, and stick its
	 * component parts into the environment.  Allow combination
	 * GET and POST queries, even though that's a bit strange.
	 */
	query = getenv("QUERY_STRING");
	if (query != NULL && strlen(query))
	{
		char    *dupquery;
 
		/* Ultrix doesn't have strdup(), so we do this the long way. */
		dupquery = malloc(strlen(query) + 1);
		if (dupquery)
		{
			strcpy(dupquery, query);
			scanquery(dupquery);
		}
	}

#ifdef DEBUG
	printf("Scanned query string.\n");
	fflush(stdout);
#endif

	method = getenv("REQUEST_METHOD");
	if (method != NULL && ! strcmp(method, "POST"))
	{
		query = postread();
		if (query[0] != '\0')
			scanquery(query);
	}

#ifdef DEBUG
	printf("Read POST query, if any.\n");
	fflush(stdout);
#endif

#ifndef NO_QUERY_OK
	if (query == NULL)
	{
		http_head();
		puts("<p>The 'uncgi' program couldn't find a query to");
		puts("process.\n</body></html>");
		exit(1);
	}
#endif

}
