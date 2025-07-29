
/* * * * * * * * * * * * * * *
 * Zisland-Finder C++ Core   *
 * Source code of ZcurvePy   *
 *                           *
 * @author  ZT Zhang, F Gao  *
 * @date    2025-05-05       *
 * @version 0.0.1            *
 * * * * * * * * * * * * * * */

#include"ZislandFinder.h"
#define PCC_CONSTANT 3.4641016151

/* Constructor of RegionNode */
RegionNode::RegionNode(int start, int end) {
    this->next = nullptr;
    this->start = start;
    this->end = end;
}

/* Find island regions by a sliding window calculating PCC. */
/*
 * @param values y-values of 2D curves.
 * @param length Length of y-value array.
 * @param locs   Locations of found islands.
 * @param window Window size of the algorithm.
 * @param minPCC Threshold of PCC.
 * 
 * @return count of islands.
 */
static int findIsland(
    const float *values, 
    const int length,
    const int window,
    const float minPCC,
    RegionNode *root
) {
    // Window size-related constants
    const double lxx = sqrt(window);
    const int maxIndex = window - 1;
    // Values for PCC calculation
    double xySum = 0.0, ySum = 0.0, y2Sum = 0.0;

    // Initialization of sliding window
    for (int i = 0; i < window; i ++) {
        xySum += i * (double) values[i];
        ySum += (double) values[i];
        y2Sum += (double) values[i] * values[i]; 
    }

    // Initialization of PCC calculating
    double lxy = xySum / maxIndex - ySum / 2;
    double lyy = sqrt(y2Sum - ySum * ySum / window);
    double pcc = PCC_CONSTANT * lxy / lyy / lxx;
    
    bool recording = pcc > minPCC; // Recording switch
    // The start point of a new island and count of islands
    int start = 0, count = 0;

    RegionNode *nextNode = root;
    const int stop = length - window;
    for (int winStart = 0, winEnd = window; winStart < stop; winStart ++, winEnd ++) {
        // Update the sum values of the next sliding window
        ySum += values[winEnd] - values[winStart];
        xySum += window * values[winEnd] - ySum;
        y2Sum += values[winEnd] * values[winEnd] - values[winStart] * values[winStart];

        // Calculate the PCC value of the next sliding window
        lxy = xySum / maxIndex - ySum / 2;
        lyy = sqrt(y2Sum - ySum * ySum / window);
        pcc = PCC_CONSTANT * lxy / lyy / lxx;

        if (recording && pcc <= minPCC) {
            nextNode->next = new RegionNode(start, winEnd + 1);
            nextNode = nextNode->next;
            recording = false;
            count ++;
        } else if (!recording && pcc > minPCC) {
            start = winStart + 1;
            recording = start > nextNode->end;
            if (!recording) nextNode->end = winEnd + 1;
        }
    }

    // Finally operation
    if (recording) {
        nextNode->next = new RegionNode(start, length);
        count ++;
    }

    // Refine
    nextNode = root;
    int minPoint, maxPoint, endPoint, subLen;
    float minValue, maxValue;
    while(nextNode->next) {
        nextNode = nextNode->next;
        endPoint = nextNode->end;
        minPoint = nextNode->start, minValue = values[minPoint];
        maxPoint = nextNode->end, maxValue = values[maxPoint];
        
        for (int i = minPoint + 1; i < endPoint; i ++) {
            if (values[i] > maxValue)
                maxPoint = i, maxValue = values[i];
            else if (values[i] < minValue)
                minPoint = i, minValue = values[i];
        }
        
        nextNode->start = minPoint;
        nextNode->end = maxPoint;
    }

    return count;
}

#ifdef __cplusplus
extern "C" {
#endif

/* ZcurvePy.find_island */
PyObject* ZcurvePy_findIsland(PyObject* self, PyObject* args, PyObject *kw) {
    import_array();
    static char *kwlist[] = {"curve", "window", "min_pcc", NULL};
    int window = 50000;
    float minPCC = 0.98;
    PyObject *input_array;
    PyArrayObject *np_array = NULL, *temp_array = NULL;
    const float *c_array;
    npy_intp length;

    if (!PyArg_ParseTupleAndKeywords(args, kw, "O|if", kwlist, &input_array, &window, &minPCC))
        return NULL;

    if (!PyArray_Check(input_array)) {
        PyErr_SetString(PyExc_TypeError, "Input must be a NumPy array");
        return NULL;
    }

    np_array = (PyArrayObject *) input_array;

    if (PyArray_NDIM(np_array) != 1) {
        PyErr_SetString(PyExc_ValueError, "Array must be 1-dimensional");
        return NULL;
    }

    if (PyArray_TYPE(np_array) != NPY_FLOAT32) {
        PyErr_SetString(PyExc_TypeError, "Array must be of float32 type");
        return NULL;
    }

    if (!PyArray_ISCONTIGUOUS(np_array)) {
        temp_array = (PyArrayObject *) PyArray_GETCONTIGUOUS(np_array);
        if (!temp_array) {
            PyErr_SetString(PyExc_RuntimeError, "Failed to make array contiguous");
            return NULL;
        }
        np_array = temp_array;
    }

    c_array = (float *) PyArray_DATA(np_array);
    length = PyArray_DIM(np_array, 0);

    RegionNode *root = new RegionNode(NULL, -1);
    int count = findIsland(c_array, length, window, minPCC, root);
    PyObject *results = PyList_New(count);

    int i = 0;
    RegionNode *nextNode = root->next;
    while (nextNode) {
        PyObject *region = Py_BuildValue("(i,i)", nextNode->start, nextNode->end);
        PyList_SET_ITEM(results, i, region);
        root = nextNode;
        nextNode = root->next;
        delete root;
        i ++;
    }

    if (temp_array) Py_DECREF(temp_array);

    return results;
}

#ifdef __cplusplus
}
#endif