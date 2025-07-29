/* tas_error.h -- Target Acquisition Simulator 			24-Mar-97
 *			Error definitions
 */

enum errorType_ { TAS_ERROR_WARNING, TAS_ERROR_FATAL };
typedef enum errorType_ ErrorType;

# define IMAGE_NOT_FITS		10
# define IMAGE_ACCESS_ERROR	11
# define IMAGE_OPEN_ERROR	12
# define IMAGE_TOO_SMALL	13
# define IMAGE_NOT_2D		14
# define IMAGE_READ_ERROR	15
# define IMAGE_NO_FLUX		15

# define IMAGE_SCALE_UNDEFINED	20
# define IMAGE_SCALE_TOO_COARSE	21

void outputError (const char *, int);

