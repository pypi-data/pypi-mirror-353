/* * * * * * * * * * * * * * * * * * * *
 *  ZcurvePy Source Code               *
 *                                     *
 *  @author      Zhang ZT, Gao F       *
 *  @copyright   Copyright 2025 TUBIC  *
 *  @date        2025-02-25            *
 *  @version     1.6.0                 *
 * * * * * * * * * * * * * * * * * * * */

// Supported Python Version: >= 3.9
#ifndef ZCURVEPY_APIS
#define ZCURVEPY_APIS

#define PY_SSIZE_T_CLEAN

#include<thread>
#include<vector>
#include<random>
#include<algorithm>
#include<cstdio>

#include<Python.h>
#include<numpy/arrayobject.h>
#include"ZcurvePyCore.h"

/* Keyword 'k' for ZcurvePy.BatchZcurveEncoder */
extern PyObject *keyK;
/* Keyword 'phase' for ZcurvePy.BatchZcurveEncoder */
extern PyObject *keyPhase;
/* Keyword 'freq' for ZcurvePy.BatchZcurveEncoder */
extern PyObject *keyFreq;
/* Keyword 'local' for ZcurvePy.BatchZcurveEncoder */
extern PyObject *keyLocal;
/* Keyword 'hyper_params' for ZcurvePy.BatchZcurveEncoder */
extern PyObject *keyHyper;
/* Keyword 'n_jobs' for ZcurvePy.BatchZcurveEncoder */
extern PyObject *keyNJobs;
/* ZcurvePy main module object*/
extern PyObject *_ZcurvePy;
/* Bio.SeqRecord.SeqRecord (BioPython) type object */
extern PyObject *SeqRecord;
/* Python Type Object ZcurveEncoder*/
extern PyTypeObject ZcurveEncoderType;
/* Python Type Object ZcurvePlotter*/
extern PyTypeObject ZcurvePlotterType;
/* Python Type Object BatchZcurveEncoder*/
extern PyTypeObject BatchZcurveEncoderType;
/* Python Type Object BatchZcurvePlotter*/
extern PyTypeObject BatchZcurvePlotterType;
#ifdef __cplusplus
extern "C" {
#endif
/* shuffle C/C++ API able to handle many-type Python objects, like str, Seq and SeqRecord */
PyObject *ZcurvePy_shuffle(PyObject *, PyObject *, PyObject *);
/* decoding Z-curves */
PyObject *ZcurvePy_decode(PyObject *, PyObject *, PyObject *);
#ifdef __cplusplus
}
#endif
#endif