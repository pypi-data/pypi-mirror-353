/* tas_struct.h - 	Target Acquisition Simulator 		27-Jan-97
 *			User data structure definitions
 */

# include "tas.h"

typedef struct {
	double		plateScaleX;		/* degree/pixel */
	double		plateScaleY;		/* degree/pixel */
	float		targetFlux;		/* brightness of target */
	float		targetX;		/* computed X location of target */
	float		targetY;		/* computed Y location of target */
	TargetType	targetType;		/* POINT or DIFFUSE */
	CenterMethod	centerMethod;		/* GEOMETRIC or FLUX_CENTROID */
	int		refPixelX;		/* X center of sub-image */
	int		refPixelY;		/* Y center of sub-image */
	int		sizeSubImage;		/* X,Y extent of sub-image */
	int		sizeCheckbox;		/* X,Y size of summation checkbox */
	char		fileName[SZ_FNAME];	/* name of input image */
	char		warnings[SZ_LINE];	/* warning message(s) */
	char		version[SZ_LINE];	/* s/w version number/date */
} UserData;

void getKeywordStr (UserData ud, const char *, char *); 

void outputASCII (UserData); 

void outputHTML (UserData ud);

