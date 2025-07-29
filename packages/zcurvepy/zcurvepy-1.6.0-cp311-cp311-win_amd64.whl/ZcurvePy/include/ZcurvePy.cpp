/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy Source Code               *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-02-25            *
 *  @version     1.6.0                 *
 * * * * * * * * * * * * * * * * * * * */
#include "ZcurvePyCore.h"
#include "ZcurvePyAPIs.h"
#include "ZislandFinder.h"

/* Methods definition of _ZcurvePy module */
static PyMethodDef _ZcurvePy_methods[] = {
    {"shuffle", (PyCFunction) ZcurvePy_shuffle, METH_VARARGS|METH_KEYWORDS, NULL},
    {"decode", (PyCFunction) ZcurvePy_decode, METH_VARARGS|METH_KEYWORDS, NULL},
    {"find_island", (PyCFunction) ZcurvePy_findIsland, METH_VARARGS|METH_KEYWORDS, NULL},
    {NULL, NULL, 0, NULL}
};

/* Definition of _ZcurvePy module */
static struct PyModuleDef _ZcurvePyModule = {
    PyModuleDef_HEAD_INIT,
    "_ZcurvePy",
    NULL,
    -1,
    _ZcurvePy_methods
};

/* Init function of _ZcurvePy */
PyMODINIT_FUNC PyInit__ZcurvePy(void) {
    /* Import necessary third-party modules */
    PyObject *Bio_module = PyImport_ImportModule("Bio.SeqRecord");
    PyObject *json_module = PyImport_ImportModule("json");
    SeqRecord = PyObject_GetAttrString(Bio_module, "SeqRecord");
    Py_DECREF(Bio_module);
    Py_DECREF(json_module);

    /* Key for BatchZcurveEncoder to parse parameters */
    keyK = Py_BuildValue("s", "k");
    keyPhase = Py_BuildValue("s", "phase");
    keyFreq = Py_BuildValue("s", "freq");
    keyLocal = Py_BuildValue("s", "local");
    keyHyper = Py_BuildValue("s", "hyper_params");
    keyNJobs = Py_BuildValue("s", "n_jobs");

    /* Init the _ZcurvePy module object */
    if (
        PyType_Ready(&ZcurveEncoderType) < 0 ||
        PyType_Ready(&ZcurvePlotterType) < 0 ||
        PyType_Ready(&BatchZcurveEncoderType) < 0 ||
        PyType_Ready(&BatchZcurvePlotterType) < 0
    ) return NULL;
    _ZcurvePy = PyModule_Create(&_ZcurvePyModule);
    if (_ZcurvePy == NULL)
        return NULL;
    
    /* Load Python type objects to the module */
    Py_INCREF(&ZcurveEncoderType);
    Py_INCREF(&ZcurvePlotterType);
    Py_INCREF(&BatchZcurveEncoderType);
    Py_INCREF(&BatchZcurvePlotterType);

    if (!PyModule_AddObject(_ZcurvePy, "ZcurveEncoder", (PyObject *) &ZcurveEncoderType))
    if (!PyModule_AddObject(_ZcurvePy, "ZcurvePlotter", (PyObject *) &ZcurvePlotterType))
    if (!PyModule_AddObject(_ZcurvePy, "BatchZcurveEncoder", (PyObject *) &BatchZcurveEncoderType))
    if (!PyModule_AddObject(_ZcurvePy, "BatchZcurvePlotter", (PyObject *) &BatchZcurvePlotterType))
        return _ZcurvePy;

    Py_DECREF(&ZcurveEncoderType);
    Py_DECREF(&ZcurvePlotterType);
    Py_DECREF(&BatchZcurveEncoderType);
    Py_DECREF(&BatchZcurvePlotterType);
    Py_DECREF(_ZcurvePy);

    return NULL;
}