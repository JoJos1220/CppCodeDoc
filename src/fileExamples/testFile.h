#ifndef TESTFILE_H
#define TESTFILE_H

/*-----------------------------------------------------------------------------
 * Include Libarys Section
 * ----------------------------------------------------------------------------
*/
#include <iostream>


/**
 * @brief TestClass::TestClass -->> TODO: Add your description here
 */
TestClass::TestClass(){} /* TestClass::TestClass() */


/**
 * @brief TestClass::~TestClass -->> TODO: Add your description here
 */
TestClass::~TestClass(){} /* TestClass::~TestClass() */


/**
 * @brief testFunctionWithNoParams -->> TODO: Add your description here
 */
void testFunctionWithNoParams(){
    std::cout << "testFunctionWithNoParams" << std::endl;
} /* testFunctionWithNoParams() */


/**
 * @brief testFunctionWithParams -->> TODO: Add your description here
 * @param a TODO
 * @param b TODO
 * @note Note that!
 * @see See that!
 * @warning Warning that!
 */
void testFunctionWithParams(int a, int b){
    std::cout << "testFunctionWithParams" << std::endl;
} /* testFunctionWithParams() */


/**
 * @brief Doing some commenting on the function
 * @param a TODO
 * @param b TODO
 */
void AnothertestFunctionWithParams(double a, int b){
    std::cout << "testFunctionWithParams" << std::endl;
} /* AnothertestFunctionWithParams() */


/**
 * @brief testFunctionWithReturn -->> TODO: Add your description here
 * @return TODO
 */
int testFunctionWithReturn(){
    std::cout << "testFunctionWithReturn" << std::endl;
    return 0;
} /* testFunctionWithReturn() */


/**
 * @brief testFunc -->> TODO: Add your description here
 * @return TODO
 */
double testFunc(){
    return 0;
} /* testFunc() */


/**
 * @brief twoLinedFunctionParameterDefinitionTest -->> TODO: Add your description here
 * @param thisIsAVeryLongFirstVariableToTest TODO
 * @param thisisAnotherveryLongVariablteToTest TODO
 */
void twoLinedFunctionParameterDefinitionTest(int thisIsAVeryLongFirstVariableToTest,
    double thisisAnotherveryLongVariablteToTest){
} /* twoLinedFunctionParameterDefinitionTest() */

#endif // test_nvsMock.h
