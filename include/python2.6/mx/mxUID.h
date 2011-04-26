#ifndef MXUID_H
#define MXUID_H
/* 
  mxUID -- A UID datatype.

  Copyright (c) 2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
  Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
  See the documentation for further copyright information or contact
  the author (mailto:mal@lemburg.com).
  
*/

/* The extension's name; must be the same as the init function's suffix */
#define MXUID_MODULE "mxUID"

/* Name of the package or module that provides the extensions C API.
   If the extension is used inside a package, provide the complete
   import path. */
#define MXUID_API_MODULE "mx.UID"

/* --- No servicable parts below this line ----------------------*/

/* Include generic mx extension header file */
#include "mxh.h"

#ifdef MX_BUILDING_MXUID
# define MXUID_EXTERNALIZE MX_EXPORT
#else
# define MXUID_EXTERNALIZE MX_IMPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* --- C API ----------------------------------------------------*/

/* C API for usage by other Python modules */
typedef struct {

    /* Build a new UID string for object with address id.

       code is optionally included in UID if given. It may be NULL.
       timestamp should be a double indicating Unix ticks, or 0 to have
       the API use the current time.

       The output buffer uid must have room for at least 512
       bytes. uid_len is set to the uid data length. It must be preset to
       the buffer's size.

       Returns the Python string object on success, NULL on error.

    */

    PyObject *(*UID)(void *obj,
		     char *code,
		     double timestamp);
	 
    /* Extracts the ticks timestamp from an UID string uid */

    double (*timestamp)(unsigned char *uid);
   

} mxUIDModule_APIObject;

#ifndef MX_BUILDING_MXUID

/* Interfacestructure to C API for other modules.
   Call mxUID_ImportModuleAPI() to initialize this
   structure. After that usage is simple:

   PyObject *v;
	
   v = mxUID.UID("Marc");
   if (!v)
       goto onError;
   ...

*/

static 
mxUIDModule_APIObject mxUID;

/* You *must* call this before using any of the functions in
   mxUID and check its outcome; otherwise all accesses will
   result in a segfault. Returns 0 on success. */

#ifndef DPRINTF
# define DPRINTF if (0) printf
#endif

static
int mxUID_ImportModuleAndAPI(void)
{
    PyObject *mod = 0, *v = 0;
    void *api;
    
    DPRINTF("Importing the %s C API...\n",MXUID_API_MODULE);
    mod = PyImport_ImportModule(MXUID_API_MODULE);
    if (mod == NULL)
	goto onError;
    DPRINTF(" module found\n");
    v = PyObject_GetAttrString(mod,MXUID_MODULE"API");
    if (v == NULL)
	goto onError;
    Py_DECREF(mod);
    DPRINTF(" API object found\n");
    api = PyCObject_AsVoidPtr(v);
    if (api == NULL)
	goto onError;
    Py_DECREF(v);
    memcpy(&mxUID,api,sizeof(mxUID));
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
