#ifndef TESTFILE_H
#define TESTFILE_H

/*-----------------------------------------------------------------------------
 * Include Libarys Section
 * ----------------------------------------------------------------------------
*/
#include <iostream>

TestClass::TestClass(){}

TestClass::~TestClass(){}

void testFunctionWithNoParams(){
    std::cout << "testFunctionWithNoParams" << std::endl;
}

void testFunctionWithParams(int a, int b){
    std::cout << "testFunctionWithParams" << std::endl;
}

/*-------------------------------------------------------
 * Doing some commenting on the function
 * ------------------------------------------------------
*/
void AnothertestFunctionWithParams(double a, int b){
    std::cout << "testFunctionWithParams" << std::endl;
} /* AnothertestFunctionWithParams() */

int testFunctionWithReturn(){
    std::cout << "testFunctionWithReturn" << std::endl;
    return 0;
} /* testFunctionWithReturn() */

double testFunc(){
    return 0;
} /* testFunc() */

void twoLinedFunctionParameterDefinitionTest(int thisIsAVeryLongFirstVariableToTest,
    double thisisAnotherveryLongVariablteToTest){
}

#endif // test_nvsMock.h