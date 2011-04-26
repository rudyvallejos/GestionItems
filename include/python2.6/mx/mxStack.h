#ifndef MXSTACK_H
#define MXSTACK_H
/* 
  mxStack -- A stack implemenation

  Copyright (c) 1998-2000, Marc-Andre Lemburg; mailto:mal@lemburg.com
  Copyright (c) 2000-2009, eGenix.com Software GmbH; mailto:info@egenix.com
  See the documentation for further copyright information or contact
  the author (mailto:mal@lemburg.com).
  
*/

/* The extension's name; must be the same as the init function's suffix */
#define MXSTACK_MODULE "mxStack"

/* Name of the package or module that provides the extensions C API.
   If the extension is used inside a package, provide the complete
   import path. */
#define MXSTACK_API_MODULE "mx.Stack"

/* --- No servicable parts below this line ----------------------*/

/* Include generic mx extension header file */
#include "mxh.h"

/* Include Python compatibility header file */
#include "mxpyapi.h"

#ifdef MX_BUILDING_MXSTACK
# define MXSTACK_EXTERNALIZE MX_EXPORT
#else
# define MXSTACK_EXTERNALIZE MX_IMPORT
#endif

#ifdef __cplusplus
extern "C" {
#endif

/* --- Stack Object ------------------------------------------*/

typedef struct {
    PyObject_HEAD
    Py_ssize_t size;		/* Number of items allocated */
    Py_ssize_t top;		/* Index of top element */
    PyObject **array;		/* Pointer to the stack array */
} mxStackObject;

/* Type checking macro */

#define mxStack_Check(v) \
        (((mxStackObject *)(v))->ob_type == mxStack.Stack_Type)

/* Some (unsafe) macros to access the most important parts */

#define mxStack_GET_SIZE(v) (((mxStackObject *)v)->top+1)
#define mxStack_GET_ITEM(v,i) (((mxStackObject *)v)->stack[i])

/* --- C API ----------------------------------------------------*/

/* C API for usage by other Python modules */
typedef struct {
	 
    /* Type object for Stack() */
    PyTypeObject *Stack_Type;

    /* Create a new empty stack object with at least size entries
       alredy allocated. */
    mxStackObject *(*mxStack_New)(Py_ssize_t size);

    /* Create a new empty stack object from the sequence v */
    mxStackObject *(*mxStack_FromSequence)(PyObject *v);

    /* Push a Python object onto the stack. The reference count is increased
       by one. Stacks only grow, they never shrink again. */
    int (*mxStack_Push)(mxStackObject *stack,
			PyObject *v);
    
    /* Pop an object from the stack. Ownership is passed to the caller.
       Note: This doesn't cause the allocated stack size to change. */
    PyObject *(*mxStack_Pop)(mxStackObject *stack);
    
    /* Return a the stacks content as tuple. */
    PyObject *(*mxStack_AsTuple)(mxStackObject *stack);
    
    /* Return a the stacks content as list. */
    PyObject *(*mxStack_AsList)(mxStackObject *stack);

    /* Pop the topmost n entries from the stack and return them as
       tuple. If there are not enough entries only the available ones
       are returned.  */
    PyObject *(*mxStack_PopMany)(mxStackObject *stack,
				 Py_ssize_t n);

    /* Push the entries from sequence onto the stack. */
    int (*mxStack_PushMany)(mxStackObject *stack,
			    PyObject *sequence);

    /* Clear the stack. */
    int (*mxStack_Clear)(mxStackObject *stack);

    /* Get the number of entries in the stack. */
    Py_ssize_t (*mxStack_Length)(mxStackObject *stack);

    /* Gets the item index from the stack without popping it off the
       stack. Negative indices work just like for Python lists. Entry
       0 is the bottom most entry, -1 the top most.  */
    PyObject *(*mxStack_GetItem)(mxStackObject *stack,
				 Py_ssize_t index);

} mxStackModule_APIObject;

#ifndef MX_BUILDING_MXSTACK

/* Interfacestructure to C API for other modules.
   Call mxStack_ImportModuleAPI() to initialize this
   structure. After that usage is simple:

   PyObject *v;
	
   v = mxStack.Stack_New(0);
   if (!v)
       goto onError;
   ...

*/

static 
mxStackModule_APIObject mxStack;

/* You *must* call this before using any of the functions in
   mxStack and check its outcome; otherwise all accesses will
   result in a segfault. Returns 0 on success. */

#ifndef DPRINTF
# define DPRINTF if (0) printf
#endif

static
int mxStack_ImportModuleAndAPI(void)
{
    PyObject *mod, *v = 0;
    void *api;
    
    DPRINTF("Importing the %s C API...\n",MXSTACK_API_MODULE);
    mod = PyImport_ImportModule(MXSTACK_API_MODULE);
    if (mod == NULL)
	goto onError;
    DPRINTF(" module found\n");
    v = PyObject_GetAttrString(mod,MXSTACK_MODULE"API");
    if (v == NULL)
	goto onError;
    Py_DECREF(mod);
    DPRINTF(" API object found\n");
    api = PyCObject_AsVoidPtr(v);
    if (api == NULL)
	goto onError;
    Py_DECREF(v);
    memcpy(&mxStack,api,sizeof(mxStack));
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
