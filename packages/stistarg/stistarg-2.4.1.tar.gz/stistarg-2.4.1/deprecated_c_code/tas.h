/* tas.h -- Target Acquisition Simulator definitions		06-Jan-99
 */

#ifndef TAS_H
#define TAS_H

# define TAS_VERSION	"Version 1.2, 24-Mar-97"

/* Various string/length constants */
# define SZ_FNAME	160 
# define SZ_LINE	160 

# define SZ_KEYWD	 20
# define SZ_PATH	160
# define EOS		'\0'

/* File locations */
# define EXEC_FTP_TRANSFER	"/garnet/data2/httpd/cgi-bin/STIS/tas/ftp-auto-get"
# define TAS_FTP_PATH		"/data/garnet2/STIS/tas_tmp"
# define TAS_URL		"http://www.stsci.edu/ftp/instrument_news/STIS/TAS/stis_tas.html"

/* User parameter definitions */
# define POINT_CHECKBOX_SIZE	  3
# define MAX_CHECKBOX_SIZE	105
# define POINT_SUBIMAGE_SIZE	100
# define DIFFUSE_SUBIMAGE_SIZE	101
# define MAX_PS_FACTOR		  2.
# define STIS_CCD_PLATESCALE	0.0508		/* arcsec/pixel */

enum invokeMethod_ { WEB_PROGRAM = 1, OS_PROGRAM, IRAF_PROGRAM };
typedef enum invokeMethod_ InvokeMethod;

enum centerMethod_ { GEOMETRIC, FLUX_CENTROID };
typedef enum centerMethod_ CenterMethod;

enum targetType_ { POINT, DIFFUSE };
typedef enum targetType_ TargetType; 

void strToUpper (char *s1);

#endif
