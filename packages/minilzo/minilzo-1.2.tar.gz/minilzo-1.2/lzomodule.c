#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "minilzo.h"


#undef UNUSED
#define UNUSED(var)     ((void)&var)

static PyObject *LzoError;


#define M_LZO1X_1 1
#define M_LZO1X_1_15 2
#define M_LZO1X_999 3

static /* const */ char compress__doc__[] =
"compress bytes using LZO1X, returning bytes\n";
static /* const */ char decompress__doc__[] =
"decompress bytes, the uncompressed size should be passed as second argument (which is know when parsing lzop structure)\n";
static /* const */ char lzo_adler32__doc__[] =
"adler32 checksum.\n";


static PyObject *
compress(PyObject *dummy, PyObject *args)
{
  PyObject *result;
  lzo_voidp wrkmem = NULL;

  const lzo_bytep in;
  lzo_bytep out;
  
  Py_ssize_t in_len;
  Py_ssize_t out_len;
  lzo_uint new_len;

  int err;
  UNUSED(dummy);

  if (!PyArg_ParseTuple(args, "s#", &in, &in_len))
    return NULL;

  out_len = in_len + in_len / 64 + 16 + 3;

  if ((long unsigned int)in_len > LZO_UINT_MAX || (long unsigned int)out_len > LZO_UINT_MAX) {
    PyErr_SetString(LzoError, "Size is larger than LZO_UINT_MAX");
    return NULL;
  }

  result = PyBytes_FromStringAndSize(NULL, out_len);
  if (result == NULL)
    return PyErr_NoMemory();

  wrkmem = (lzo_voidp) PyMem_Malloc(LZO1X_1_MEM_COMPRESS);
  if (wrkmem == NULL) {
    Py_DECREF(result);
    return PyErr_NoMemory();
  }
  out = (lzo_bytep) PyBytes_AS_STRING(result);
  new_len = out_len;
  err = lzo1x_1_compress(in, (lzo_uint)in_len, out, &new_len, wrkmem);

  PyMem_Free(wrkmem);
  if (err != LZO_E_OK || (Py_ssize_t)new_len > out_len)
  {
    /* this should NEVER happen */
    Py_DECREF(result);
    PyErr_Format(LzoError, "Error %i while compressing data", err);
    return NULL;
  }

  if ((Py_ssize_t)new_len < out_len)
   _PyBytes_Resize(&result, (Py_ssize_t)new_len); 

  return result;

}

static PyObject *
decompress(PyObject *dummy, PyObject *args)
{
  PyObject *result;

  lzo_bytep in;
  lzo_bytep out;

  Py_ssize_t in_len;
  Py_ssize_t out_len;
  lzo_uint new_len;

  int err;
  UNUSED(dummy);
  
  if (!PyArg_ParseTuple(args, "s#n", &in, &in_len, &out_len))
    return NULL;

  if ((long unsigned int)in_len > LZO_UINT_MAX || (long unsigned int)out_len > LZO_UINT_MAX) {
    PyErr_SetString(LzoError, "Size is larger than LZO_UINT_MAX");
    return NULL;
  }

  result = PyBytes_FromStringAndSize(NULL, out_len);
  if (result == NULL)
    return PyErr_NoMemory();

  out = (lzo_bytep) PyBytes_AS_STRING(result);
  new_len = out_len;
  err = lzo1x_decompress_safe(in, (lzo_uint)in_len, out, &new_len, NULL);

  if (err != LZO_E_OK || (Py_ssize_t)new_len > out_len) {
      Py_DECREF(result);
      PyErr_SetString(LzoError, "Decompression failed");
      return NULL;
  }

  if ((Py_ssize_t)new_len < out_len)
   _PyBytes_Resize(&result, (Py_ssize_t)new_len); 

  return result;

}

static PyObject *
adler32(PyObject *dummy, PyObject *args)
{
  lzo_uint32 value = 1;
  const lzo_bytep in;
  Py_ssize_t len;

  if (!PyArg_ParseTuple(args, "s#|I", &in, &len, &value))
    return NULL;

  if (len > 0) {
    value = lzo_adler32(value, in, len);
  }
  return PyLong_FromLong(value);
}


/***********************************************************************
// main
************************************************************************/

static /* const */ PyMethodDef methods[] =
{
    {"compress", (PyCFunction)compress, METH_VARARGS, compress__doc__},
    {"decompress", (PyCFunction)decompress, METH_VARARGS, decompress__doc__},
    {"adler32", (PyCFunction)adler32, METH_VARARGS, lzo_adler32__doc__},
    {NULL, NULL, 0, NULL}
};


static /* const */ char module_documentation[]=
"This is a python library deals with lzo files compressed with lzop.\n\n";


static struct PyModuleDef _minilzo = {
  PyModuleDef_HEAD_INIT,
  "_minilzo",
  module_documentation,
  -1,
  methods
};
PyMODINIT_FUNC PyInit__minilzo() {
  PyObject *m, *d;
  if (lzo_init() != LZO_E_OK)
    return NULL;
  m = PyModule_Create(&_minilzo);
  if (m == NULL)
    return NULL;
  d = PyModule_GetDict(m);
  LzoError = PyErr_NewException("_minilzo.error", NULL, NULL);
  PyDict_SetItemString(d, "error", LzoError);
  return m;
}
