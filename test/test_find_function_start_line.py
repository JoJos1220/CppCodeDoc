# CppCodeDoc — Licensed under the GNU General Public License v3.0 (GPLv3-or-later)
# SPDX-License-Identifier: GPLv3-or-later
# Copyright (C) 2025 Jojo1220
# See https://www.gnu.org/licenses/gpl-3.0.html

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.formatter.code_parser import find_function_start_line

def test_single_line_function():
    code = """\
int testFunction(int a) {
    return a;
}
"""
    assert find_function_start_line(code, "testFunction", "int a") == 0

def test_multiline_function():
    code = """\
bool exampleFunction(
    int a,
    float b
) 
{
    return true;
}
"""
    assert find_function_start_line(code, "exampleFunction") == 0

def test_const_override_function():
    code = """\
virtual std::string toString(
) const override 
{
    return "text";
}
"""
    assert find_function_start_line(code, "toString") == 0

def test_function_not_found():
    code = """\
int unrelatedFunction() {
    return 0;
}
"""
    assert find_function_start_line(code, "nonexistentFunction") == -1

def test_constructor():
    code = """\
MyClass::MyClass() 
{
    // Konstruktor
}
"""
    assert find_function_start_line(code, "MyClass::MyClass") == 0

def test_destructor():
    code = """\
MyClass::~MyClass()
{
    // Destruktor
}
"""
    assert find_function_start_line(code, "MyClass::~MyClass") == 0

def test_function_with_templates():
    code = """\
template<typename T>
T add(T a, T b) 
{
    return a + b;
}
"""
    # function start line is a 0-based incrementing index!
    assert find_function_start_line(code, "add") == 1

def test_function_with_pointer_reference_and_space():
    code = """\
bool  complicatedFunc ( const MyType& obj, MyType* ptr ) noexcept 
{
    return true;
}
"""
    assert find_function_start_line(code, "complicatedFunc") == 0


def test_function_with_comment():
    code = """\
/*-----------------------------------------------------------------------------
 * pythonTest -->> Add your description here
 * ----------------------------------------------------------------------------
*/
void pythonTest(const char* str, char sep, byte* bytes, int maxBytes, int base) {
    for (int i = 0; i < 700; i++) {
        bytes[i] = "";  
        str++;                                // Point to next character after separator
    }
}
"""
    assert find_function_start_line(code, "pythonTest") == 4

def test_specific_led_function_with_comment():
    code = """\
/*-----------------------------------------------------------------------------
 * LED::read(): Function to read LED State
 * ----------------------------------------------------------------------------
*/
bool LED::read(void) {
  return digitalFASTRead(_pin);

} /* LED::read() */
"""
    assert find_function_start_line(code, "LED::read") == 4

def test_call_class_function_bevor_definition():
    code = """\
void NotHing::nothingToDo(int a) {
    _test = NotHing::MoreToDo(a);
}

int NotHing::MoreToDo(int a) {
    return a;
}

"""
    assert find_function_start_line(code, "NotHing::MoreToDo") == 4


def test_specific_authmanger_function():
    code = """\
void AuthManager::saveUser(const char* username, const char* password_hash, uint8_t role) {
    bool userExists = false;
    saveUsersToFile(_userFilePath);
}

/*-----------------------------------------------------------------------------
 * AuthManager::saveUser() -- Function for writing/updating user data to file
 * ----------------------------------------------------------------------------
*/
void AuthManager::saveUser(StaticUser user) {
    saveUser(user.username, user.password_hash, user.role);
} /* Authmanager::saveUser() */
"""
    assert find_function_start_line(code, "AuthManager::saveUser") == 0
    assert find_function_start_line(code, "AuthManager::saveUser", "const char* username, const char* password_hash, uint8_t role") == 0
    assert find_function_start_line(code, "AuthManager::saveUser", "StaticUser user") == 9

def test_enhanced_code_pattern_beacuse_of_issues():
    code = """\
/*-----------------------------------------------------------------------------
 * CulLogger::initializeUsers() -- Function for Initizializing of users. Maybe - 
 * later - from NVS Storage or Parameter File
 * ----------------------------------------------------------------------------
*/
void AuthManager::loadUsersFromFile(const char* _filePath){
    // Hier wird dann auf nvs Storage oder Parameter File zugegriffen und der HASH ausgelesen!!!
    //
    // "Admin": "d033e22ae348aeb5660fc2140aec35850c4da997",  # SHA1("admin")
    // "User": "12dea96fec20593566ab75692c9949596833adc9"  # SHA1("user")
    //
    userList.clear(); // clear list until beginning

    if (!sdWrapper.checkFileExists(_filePath)) {
        DEBUG_SERIAL.printf("%sFile /users.json not found!\r\n", AUTH_MSG);
        return;
    }

    File file;
    if (!sdWrapper.openFile(file, _filePath, "r")) {
        DEBUG_SERIAL.printf("%sError opening file /users.json!\r\n", AUTH_MSG);
        return;
    }

    String jsonLine;

    while(file.available()){
        if (userList.size() >= MAX_USERS) {
            DEBUG_SERIAL.printf("%sMax users reached!\r\n", AUTH_MSG);
            file.close();
            break;
        }

        jsonLine = file.readStringUntil('\n');
        jsonLine = jsonRemoveWhiteSpace(jsonLine);
        DEBUG_SERIAL.printf("%suserLine from users.json: %s\r\n", AUTH_MSG, jsonLine.c_str());

        if (jsonLine.length() == 0) {
            DEBUG_SERIAL.printf("%sEmpty line found!\r\n", AUTH_MSG);
            continue; // Going on if line is empty!
        }

        StaticUser newUser;
        String username = jsonExtract(jsonLine, "username");
        String passwordHash = jsonExtract(jsonLine, "password_hash");
        String roleStr = jsonExtract(jsonLine, "role");
        
        strncpy(newUser.username, username.c_str(), MAX_USERNAME_LEN);
        newUser.username[MAX_USERNAME_LEN] = '\0';
        
        strncpy(newUser.password_hash, passwordHash.c_str(), SHA1_HASH_LEN);
        newUser.password_hash[SHA1_HASH_LEN] = '\0';
        
        newUser.role = static_cast<uint8_t>(roleStr.toInt());
        
        DEBUG_SERIAL.printf("%sAdding user from users.json to userList: %s , %s, %i \r\n", AUTH_MSG, newUser.username, newUser.password_hash, newUser.role);
        userList.push_back(newUser);

    }

    file.close();

    DEBUG_SERIAL.printf("%sloadUsersFromFile() - done!\r\n", AUTH_MSG);
        
} /* AuthManager::initializeUsers() */

/*-----------------------------------------------------------------------------
 * AuthManager::saveUser() -- Function for writing/updating user data to file
 * ----------------------------------------------------------------------------
*/
void AuthManager::saveUser(const char* username, const char* password_hash, uint8_t role) {
    bool userExists = false;

    for (StaticUser& user : userList) {
        if (strcmp(user.username, username) == 0) {
            strncpy(user.password_hash, password_hash, SHA1_HASH_LEN);
            user.password_hash[SHA1_HASH_LEN] = '\0';
            user.role = role;
            userExists = true;
            DEBUG_SERIAL.printf("%sUser %s updated!\r\n", AUTH_MSG, username);
            break;
        }
    }

    if (!userExists) {
        if (userList.size() >= MAX_USERS) {
            DEBUG_SERIAL.printf("%sMax users reached!\r\n", AUTH_MSG);
            return;
        }

        // Checking Users out of Static Fallback List
        for (uint8_t i = 0; i < staticUserCount; i++) {
            if (strcmp(staticUsers[i].username, username) == 0) {
                DEBUG_SERIAL.printf("%sSTatic User added to File for further Login with different Password thend efault!!\r\n", AUTH_MSG);
            }
        }

        StaticUser newUser;
        strncpy(newUser.username, username, MAX_USERNAME_LEN);
        newUser.username[MAX_USERNAME_LEN] = '\0';
        strncpy(newUser.password_hash, password_hash, SHA1_HASH_LEN);
        newUser.password_hash[SHA1_HASH_LEN] = '\0';
        newUser.role = role;

        userList.push_back(newUser);
    }

    saveUsersToFile(_userFilePath);
} /* AuthManager::saveUser() */

/*-----------------------------------------------------------------------------
 * AuthManager::saveUser() -- Function for writing/updating user data to file
 * ----------------------------------------------------------------------------
*/
void AuthManager::saveUser(StaticUser user) {
    saveUser(user.username, user.password_hash, user.role);
} /* Authmanager::saveUser() */

/*-----------------------------------------------------------------------------
 * AuthManager::deleteUser() -- Clearing User out of File
 * ----------------------------------------------------------------------------
*/
void AuthManager::deleteUser(const char* username) {
    for (auto it = userList.begin(); it != userList.end(); ++it) {
        if (strcmp(it->username, username) == 0) {
            userList.erase(it);
            saveUsersToFile(_userFilePath);
            DEBUG_SERIAL.printf("%sUser %s deleted in File!\r\n", AUTH_MSG, username);
            return;
        }
    }
    // Checking Users out of Static Fallback List
    for (uint8_t i = 0; i < staticUserCount; i++) {
        if (strcmp(staticUsers[i].username, username) == 0) {
            DEBUG_SERIAL.printf("%sStatic User cannot be deleted!!\r\n", AUTH_MSG);
        }
    }
    DEBUG_SERIAL.printf("%sUser %s not found!\r\n", AUTH_MSG, username);
} /* AuthManager::deleteUser() */
"""

    assert find_function_start_line(code, "AuthManager::saveUser", "StaticUser user") == 125

def test_const_dest_one_liner():
    code = """\
    ImageControl(){;};
    ~ImageControl(){;};
"""
    res = find_function_start_line(code, "ImageControl")
    assert  res == 0, f"ImageControl: Constructor not found: {res}"
    res = find_function_start_line(code, "~ImageControl")
    assert res == 1, f"~ImageControl: Destructor not found: {res}"

def test_map_vector_variable():
    code = """\
// Funktion zum Lesen aus der Datei
static std::map<std::string, std::vector<uint8_t>> readFromFile() {
    int test = 0;
    return 0;
}
"""
    assert find_function_start_line(code, "readFromFile") == 1


def test_function_multiple_occurrences():
    code = """\
// Erste Variante
void pythonTest() {
    // Inhalt
}

#ifdef __cplusplus
    // Zweite (a) Variante
    void pythonTest(int a) {
        // Inhalt
    }

#else
    // Zweite (b) Variante
    void pythonTest(int a) {
        // Inhalt
    }
#endif

// Dritte Variante
void pythonTest(const char* str, char sep, byte* bytes, int maxBytes, int base) {
    for (int i = 0; i < 700; i++) {
        bytes[i] = "";
    }
}
"""
    # Checking three assertions:
    # 1. Without params
    assert find_function_start_line(code, "pythonTest", "", occurrence=1) == 1

    # 2. Parameter (int a)
    assert find_function_start_line(code, "pythonTest", "int a", occurrence=2) == 13

    # 3. Parameter (long signature)
    assert find_function_start_line(code, "pythonTest", "const char* str, char sep, byte* bytes, int maxBytes, int base", occurrence=1) == 19


def test_function_inside_if_else_block():
    code = """\
/**
 * @brief TODO ESPFlashDebuggingFunction description.
 * @param void - No Parameter defined!
 */
#if !defined(NATIVE_ENVIRONMENT)
void ESPFlashDebuggingFunction(void) {
    DEBUG_SERIAL.printf("a");
}/* ESPFlashDebuggingFunction() */
#else
void ESPFlashDebuggingFunction(void){;}/* ESPFlashDebuggingFunction() */
#endif
"""
    assert find_function_start_line(code, "ESPFlashDebuggingFunction", "void", occurrence=1) == 5
    assert find_function_start_line(code, "ESPFlashDebuggingFunction", "void", occurrence=2) == 9

def test_function_double_function_with_different_parameters():
    code = """\
//do nothing
int begin(const char* test){
    return 0;
}

int begin(){
    return 0;
}
"""
    assert find_function_start_line(code, "begin", "const char* test", occurrence=1) == 1
    assert find_function_start_line(code, "begin", "", occurrence=1) == 5


def test_function_double_function_with_mixed_default_parameters():
    code = """\
//do nothing
bool config(IPAddress local_ip, IPAddress gateway, IPAddress subnet, IPAddress dns1 = (uint32_t)0x00000000, IPAddress dns2 = (uint32_t)0x00000000){

    return true;
}

int begin(){
    return 0;
}
"""

    assert find_function_start_line(code, "config", "IPAddress local_ip, IPAddress gateway, IPAddress subnet, IPAddress dns1 = (uint32_t)0x00000000, IPAddress dns2 = (uint32_t)0x00000000", occurrence=1) == 1

def test_function_custom_operator_pattern():
    code = """\
ClassExample& operator *= (const ClassExample& q) {
    ClassExample controll(
    return (*this = controll);
}

Vector operator + (const float anotherValue) const {
	return Vector(a, b, c);
}

Vector operator * (const float a, const Vector& b) { return b * a; }
Vector operator + (const float a, const Vector& b) { return b + a; }

"""
    assert find_function_start_line(code, "operator *=", "const ClassExample& q", occurrence=1) == 0
    assert find_function_start_line(code, "operator +", "const float anotherValue", occurrence=1) == 5
    assert find_function_start_line(code, "operator *", "const float a, const Vector& b", occurrence=1) == 9

def test_function_with_inline_comment():
    code = """\
void antotherFunction(int a , int b /* = 1 */){
    return;
}
"""
    assert find_function_start_line(code, "antotherFunction", "int a , int b", occurrence=1) == 0

def test_function_with_specific_pointer_variables():
    code = """\
#if defined(USE_FASTLED_TOOLS) || defined(USE_FASTLED_BACKLIGHT)
  /* some FastLED wrapper functions for Adafruit NeoPixel library */
  uint32_t ColorRGB(uint8_t r, uint8_t g, uint8_t b) {
    return ((r << 16) | (g << 8) | b);
  }

  void ColorToRGB(uint32_t color, uint8_t* r, uint8_t* g, uint8_t* b) {
    *r = (color >> 16) & 0xff;
    *g = (color >> 8)  & 0xff;
    *b = (color >> 0 ) & 0xff;
  }

  void nscale8(Adafruit_NeoPixel* instance, uint16_t num_leds, uint8_t scale) {
    if(instance == nullptr)
      return;
    uint8_t r, g, b;
  }
"""
    assert find_function_start_line(code, "ColorRGB", "uint8_t r, uint8_t g, uint8_t b", occurrence=1) == 2
    assert find_function_start_line(code, "ColorToRGB", "uint32_t color, uint8_t* r, uint8_t* g, uint8_t* b", occurrence=1) == 6
    assert find_function_start_line(code, "noFunctionTest", "uint8_t blabla", occurrence=1) == -1
    assert find_function_start_line(code, "nscale8", "Adafruit_NeoPixel* instance, uint16_t num_leds, uint8_t scale", occurrence=1) == 12