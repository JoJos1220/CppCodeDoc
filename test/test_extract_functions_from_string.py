# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys, os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import extract_functions_from_string

def test_function_parsing_with_comments():
    test_code = """
    #ifndef TEST_PARSER_H
    #define TEST_PARSER_H

    /*-------------------------------------------------------
    * Include Section
    *-------------------------------------------------------*/

    #include <iostream>
    #include <string>

    /*-------------------------------------------------------
    * Global VAriables
    *-------------------------------------------------------*/
    int test = 0;

    /*-------------------------------------------------------
     * Doing some commenting on the function
     * ------------------------------------------------------
    */
    void AnothertestFunctionWithParams(double a, int b){
        std::cout << "testFunctionWithParams" << std::endl;
    } /* AnothertestFunctionWithParams() */

    void NoCommentFunction(){
        // no doc
    }

    /* Orphan comment block */
    #include <iostream>

    // This should be ignored during parsing!!!

    void shouldNotHaveComment(){
    }

    
    /*-----------------------------------------------------------------------------
    * AuthManager::generateRandomToken() -- Generate Random Token for Passwort Reset
    * ----------------------------------------------------------------------------
    */
    String AuthManager::generateRandomToken() {
        return "none";
    } /* AuthManager::generateRandomToken() */

    
    DefaultEnum::ForTesting AuthManager::randomTestFunction() {
        return DefaultEnum::ForTesting;
    } 

    bool generatePasswordResetToken(const char* username) {
        return true;}

    ThisisAClass::ThisisAClass() {}

    ThisisAnotherClass::~ThisisAnotherClass() {}

    bool Function::twoLinedFunctionDefinitionTest(const String &myname, const String &anothername, const String &alsoanothername,
                                const char *outputline, int &simpleInt, int &AnotherSimpleInt) {
        return false;
    }

    /*-----------------------------------------------------------------------------
    * digitalFASTRead(): Function to read a GPIO Pin State as fast alternative to digitalRead()
    * ----------------------------------------------------------------------------
    */
    int digitalFASTRead(uint8_t pin) {
        if (pin == 40) {
            return false;
        }/* if() */
        return state;
    }/* digitalFASTRead() */

    LED::LED(byte pin) : _pin(pin){
    }

    /**-------------------------------------------------------
    * @brief doxygenTestComment
    *-------------------------------------------------------*/
    static void testFunction(int a /* = 1 */) {
        // test function
    } /* testFunction() */

    // return a sub-json struct
    String jsonExtract(const String& json, const String& nameArg){
        
        while(start < json.length() && next == ' ') { // filters blanks before value if there

        }
        
        if(next == '\"'){
            //Serial.println(".. a string");
            start = start + 1;
            stop = json.indexOf('"', start);
        }
        else if(next == '['){
            //Serial.println(".. a list");
            int count = 1;
            int i = start;
            stop = i + 1;
        }
        else if(next == '{'){
            //Serial.println(".. a struct");
            int count = 1;
            int i = start;

            stop = i + 1;
        }
        else if(next == 't'){
            //Serial.println("... a boolean true");
            int i = start;
        } 
        else if(next == 'f' ){
            //Serial.println("... a boolean false");
            int i = start;
            
            if(json.charAt(i) == 'f' && json.charAt(i + 1) == 'a' && json.charAt(i + 2) == 'l' && json.charAt(i + 3) == 's' && json.charAt(i + 4) == 'e')
            {
                stop = i + 4;
            }
            else {
                stop = i;
            }	
        } 
        else if(next == 'n' ){
            //Serial.println("... a null");
            int i = start;
        }  
        else if(next == '.' || next == '-' || ('0' <= next  && next <= '9')){
            //Serial.println(".. a number");
            stop = i;
        }
        return json.substring(start, stop);
    }

    // Funktion zum Lesen aus der Datei
    static std::map<std::string, std::vector<uint8_t>> readFromFile() {
        std::map<std::string, std::vector<uint8_t>> dataMap;
        return dataMap;
    }

    // Test Präprocessor directive
    #ifdef TEST_PREPROC
    void testPreProc() {
        //do nothing
    }
    #endif

    /*--------------------------
    * Test braces in second line
    *----------------------------
    */
    void testBracesInSecondLine()
    {
        // do nothing
    }

    class test{
        public:
            test() : operand1(0), operand2(0)
            {
                // Constructor implementation
            }
    }

    
    /*-----------------------------------------------------------------------------
     * File::File() Assingment Operator
     * ----------------------------------------------------------------------------
     */
    File &operator=(const File &other)
    {
        return *this;
    }

    
    bool config(IPAddress local_ip, IPAddress gateway, IPAddress subnet, IPAddress dns1 = (uint32_t)0x00000000, IPAddress dns2 = (uint32_t)0x00000000){

        return true;
    }

    ClassExample& operator *= (const ClassExample& q) {
        ClassExample controll(
        return (*this = controll);
    }

    Vector operator + (const float anotherValue) const { /* funtctional - 
		description of the function */

        return Vector(a, b, c);
	}

    Vector operator * (const float a, const Vector& b) { return b * a; }
    Vector operator + (const float a, const Vector& b) { return b + a; }
 
    uint8_t hex_c(uint8_t   n) {    // convert '0'..'9','A'..'F' to 0..15
        return n;
    }

    void            clear() { _last_velocity   = 0; }

    void SSEWrapper::setup(void (*SSEhandleRequest)(AsyncWebServerRequest *request)) {
        // All Webserver Handler Requests has to be specified here

    }

    LED::LED(byte pin /* within pin class there is a commend! */) {
        _pin = pin;
    }

    template <class T> uint16_t  testObject(uint16_t data, const T &value) {return n;}

    template <class T>
    uint16_t  AnotherObjectClassInstance(uint16_t data, const T &value) {return n;}

    template <typename T, typename U> void foo(T t, U u) {}

    #endif // TEST_PARSER_H
    """

    result = extract_functions_from_string(test_code)

    assert result[0]['name'] == "AnothertestFunctionWithParams"
    assert "Doing some commenting" in result[0]['comment']
    assert result[0]['isDoxygenComment'] == False
    assert result[1]['name'] == "NoCommentFunction"
    assert result[1]['comment'] == ""
    assert result[2]['name'] == "shouldNotHaveComment"
    assert result[2]['comment'] == ""
    expected_comment = """    /*-----------------------------------------------------------------------------
    * AuthManager::generateRandomToken() -- Generate Random Token for Passwort Reset
    * ----------------------------------------------------------------------------
    */"""
    assert result[3]['comment'] == expected_comment
    assert result[3]['name'] == "AuthManager::generateRandomToken"
    assert result[3]['return_type'] == "String"
    assert result[4]['return_type'] == "DefaultEnum::ForTesting"
    assert result[5]['return_type'] == "bool"
    assert result[5]['params'] == "const char* username"
    assert result[6]['return_type'] == ""
    assert result[6]['params'] == ""
    assert result[6]['name'] == "ThisisAClass::ThisisAClass"
    assert result[7]['return_type'] == ""
    assert result[7]['params'] == ""
    assert result[7]['name'] == "ThisisAnotherClass::~ThisisAnotherClass"
    assert result[8]['name'] == "Function::twoLinedFunctionDefinitionTest"
    assert result[8]['return_type'] == "bool"
    assert result[8]['params'] == "const String &myname, const String &anothername, const String &alsoanothername, const char *outputline, int &simpleInt, int &AnotherSimpleInt"
    assert result[9]['name'] == "digitalFASTRead"
    assert result[9]['return_type'] == "int"
    assert result[9]['params'] == "uint8_t pin"
    assert result[10]['name'] == "LED::LED"
    assert result[10]['return_type'] == ""
    assert result[10]['params'] == "byte pin"
    assert result[11]['isDoxygenComment'] == True
    assert result[11]['return_type'] == "static void"
    assert result[12]['name'] == "jsonExtract"
    assert result[12]['return_type'] == "String"
    assert result[12]['params'] == "const String& json, const String& nameArg"
    assert result[12]['comment'] == "// return a sub-json struct" 
    assert result[12]['isDoxygenComment'] == False
    assert result[13]['name'] == "readFromFile"
    assert result[13]['return_type'] == "static std::map<std::string, std::vector<uint8_t>>"
    assert result[14]['name'] == "testPreProc"
    assert result[14]['comment'] == "// Test Präprocessor directive"
    assert result[15]['name'] == "testBracesInSecondLine"
    expected_comment = """    /*--------------------------
    * Test braces in second line
    *----------------------------
    */"""
    assert result[15]['comment'] == expected_comment
    assert result[15]['return_type'] == "void"
    assert result[15]['params'] == ""
    assert result[15]['isDoxygenComment'] == False
    assert result[16]['name'] == "test"
    assert result[17]['name'] == "operator="
    assert result[17]['params'] == "const File &other"
    assert result[18]['name'] == "config"
    assert result[18]['return_type'] == "bool"
    assert result[18]['name'] == "config"
    assert result[18]['params'] == "IPAddress local_ip, IPAddress gateway, IPAddress subnet, IPAddress dns1 = (uint32_t)0x00000000, IPAddress dns2 = (uint32_t)0x00000000"
    assert result[19]['name'] == "operator *="
    assert result[19]['params'] == "const ClassExample& q"
    assert result[20]['name'] == "operator +"
    assert result[20]['params'] == "const float anotherValue"
    assert result[21]['name'] == "operator *"
    assert result[21]['params'] == "const float a, const Vector& b"
    assert result[21]['return_type'] == "Vector"
    assert result[22]['name'] == "operator +"
    assert result[22]['params'] == "const float a, const Vector& b"
    assert result[22]['return_type'] == "Vector"
    assert result[23]['name'] == "hex_c"
    assert result[24]['name'] == "clear"
    assert result[25]['name'] == "SSEWrapper::setup"
    assert result[25]['params'] == "void (*SSEhandleRequest)(AsyncWebServerRequest *request)"
    assert result[26]['name'] == "LED::LED"
    assert result[26]['params'] == "byte pin"
    assert result[26]['return_type'] == ""
    assert result[26]['isDoxygenComment'] == False
    assert result[27]['name'] == "testObject"
    assert result[27]['params'] == "uint16_t data, const T &value"
    assert result[27]['return_type'] == "uint16_t"
    assert result[27]['templateParams'] == "<class T>"  
    assert result[28]['name'] == "AnotherObjectClassInstance"
    assert result[28]['params'] == "uint16_t data, const T &value"
    assert result[28]['return_type'] == "uint16_t"
    assert result[28]['isDoxygenComment'] == False
    assert result[28]['templateParams'] == "<class T>"
    assert result[29]['name'] == "foo"
    assert result[29]['params'] == "T t, U u"
    assert result[29]['return_type'] == "void"
    assert result[29]['isDoxygenComment'] == False
    assert result[29]['templateParams'] == "<typename T, typename U>"
    
    assert len(result) == 30
