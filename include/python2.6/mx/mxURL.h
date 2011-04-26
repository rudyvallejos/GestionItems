#ifndef MXURL_H
#define MXURL_H
/* 
  mxURL -- A URL datatype.

  Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
  Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
  See the documentation for further copyright information or contact
  the author (mailto:mal@lemburg.com).
  
*/

/* The extension's name; must be the same as the init function's suffix */
#define MXURL_MODULE "mxURL"

/* Name of the package or module that provides the extensions C API.
   If the extension is used inside a package, provide the complete
   import path. */
#define MXURL_API_MODULE "mx.URL"

/* --- No servicable parts below this line ----------------------*/

/* Include generic mx extension header file */
#include "mxh.h"

#ifdef MX_BUILDING_MXURL
# define MXURL_EXTERNALIZE MX_EXPORT
#else
# define MXURL_EXTERNALIZE MX_IMPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* Flags for some APIs: Normalize the path */
#define NORMALIZE_URL	1
#define RAW_URL		0

/* --- URL Object ------------------------------------------*/

typedef struct {
    PyObject_HEAD

    PyObject *url;		/* (Normalized) URL as Python string;
				   will always be none-NULL */
    PyObject *scheme;		/* scheme string or NULL (for: not
				   given); it is always converted to
				   lower case */

    /* Indices into PyString_AS_STRING(url), with length; if a part is
       not used by the scheme, then the char-index and length are set
       to 0, otherwise the index points into PyString_AS_STRING(url)
       and the length indicates how many characters make up that
       field. */

    short netloc;		/* network location */
    short netloc_len;
    short path;			/* path */
    short path_len;
    short params;		/* parameters */
    short params_len;
    short query;		/* query */
    short query_len;
    short fragment;		/* fragment */
    short fragment_len;

    /* Flags */
    short path_normalized;	/* Is path normalized ? */

} mxURLObject;

/* Type checking macro */

#define mxURL_Check(v) \
        (((mxURLObject *)(v))->ob_type == mxURL.URL_Type)

/* --- C API ----------------------------------------------------*/

/* C API for usage by other Python modules */
typedef struct {
	 
    /* Type object for URL() */
    PyTypeObject *URL_Type;

    /* Create a new URL object from str. If normalize is true the URL
       is normalized first */
    mxURLObject *(*mxURL_FromString)(char *str,
				     int normalize);

    /* Return a pointer to the underlying URL string; the string may *not*
       be modified ! */
    char *(*mxURL_AsString)(mxURLObject *url);

    /* Create a new URL object from the given 0-terminated strings.
       If normalize is true the URL is normalized first */
    mxURLObject *(*mxURL_FromBrokenDown)(char *scheme,
					 char *netloc,
					 char *path,
					 char *params,
					 char *query,
					 char *fragment,
					 int normalize);
    

    /* Create a new URL object from url but with normalized path. */
    mxURLObject *(*mxURL_NormalizedFromURL)(mxURLObject *url);

} mxURLModule_APIObject;

#ifndef MX_BUILDING_MXURL

/* Interfacestructure to C API for other modules.
   Call mxURL_ImportModuleAPI() to initialize this
   structure. After that usage is simple:

   PyObject *v;
	
   v = mxURL.URL_New("http://www.lemburg.com/");
   if (!v)
       goto onError;
   ...

*/

static 
mxURLModule_APIObject mxURL;

/* You *must* call this before using any of the functions in
   mxURL and check its outcome; otherwise all accesses will
   result in a segfault. Returns 0 on success. */

#ifndef DPRINTF
# define DPRINTF if (0) printf
#endif

static
int mxURL_ImportModuleAndAPI(void)
{
    PyObject *mod = 0, *v = 0;
    void *api;
    
    DPRINTF("Importing the %s C API...\n",MXURL_API_MODULE);
    mod = PyImport_ImportModule(MXURL_API_MODULE);
    if (mod == NULL)
	goto onError;
    DPRINTF(" module found\n");
    v = PyObject_GetAttrString(mod,MXURL_MODULE"API");
    if (v == NULL)
	goto onError;
    Py_DECREF(mod);
    DPRINTF(" API object found\n");
    api = PyCObject_AsVoidPtr(v);
    if (api == NULL)
	goto onError;
    Py_DECREF(v);
    memcpy(&mxURL,api,sizeof(mxURL));
    DPRINTF(" API object initialized.\n");
    return 0;
    
 onError:
    DPRINTF(" not found.\n");
    Py_XDECREF(mod);
    Py_XDECREF(v);
    return -1;
}

#endif

/* EOF */
#ifdef __cplusplus
}
#endif
#endif
