/* * * * * * * * * * * * * * *
 * Zisland-Finder C++ Core   *
 * Source code of ZcurvePy   *
 *                           *
 * @author  ZT Zhang, F Gao  *
 * @date    2025-05-05       *
 * @version 0.0.1            *
 * * * * * * * * * * * * * * */

#ifndef ZISLAND_FINDER
#define ZISLAND_FINDER

#include<vector>
#include<cmath>
#include<Python.h>
#include<numpy/arrayobject.h>
#include<algorithm>

/* Island region list node */
class RegionNode {
    public:
    RegionNode *next;  // Next RegionNode
    int start, end; // Start and end point of region
    RegionNode(int, int);
};

#ifdef __cplusplus
extern "C" {
#endif

/* ZcurvePy.find_island */
PyObject* ZcurvePy_findIsland(PyObject*, PyObject*, PyObject *);

#ifdef __cplusplus
}
#endif
#endif