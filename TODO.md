==========================================================================================
OFFEN:

Konstruktor/Destruktor footer-comments schneiden einen buchstaben ab - why?
    - Dürfte definitiv nur ein Konstruktor/Destruktor prolbem sein! Tritt auch bei anderer Klasse exakt so auf, dass erstes zeichen abgeschniten ist!
Why ist überhaupt ein return wert vorhanden bei einen konstruktor/destruktor?

/**
 * @brief LED::LED(byte pin): Constructor Function of LED Class Instance
 * @param pin TODO
 * @return TODO
 */
LED::LED(byte pin){
  _pin = pin;
}/* ED::LED() */


/**
 * @brief LED::~LED(): Destructor Function of LED Class Instance
 * @return TODO
 */
LED::~LED(void){

}/* ED::~LED() */

-----------------------------------------------------------------------------------------

footer comment issue found - wrong brace counted for comment:

/**
 * @brief OLEDMainMenu() Function for Menu Navigation called with seperate Task Function
 * @param _selected TODO
 * @param _parMaxSpeed TODO
 * @param _parAccel TODO
 */
void OLEDMainMenu(int _selected, float* _parMaxSpeed, float* _parAccel){
  bool updated = false;
  u8g2.firstPage();
  do {
    u8g2.setFont(u8g2_font_ncenB10_tr);

    // Set MAX Shown Menu Entrys depending on MaxMenuCount() Elements from given const list
    int i_max = 0;
    if(getMaxMenuCount() < MAX_SHOWN_MENU_Entrys){
      i_max = getMaxMenuCount();
    }else{
      i_max = MAX_SHOWN_MENU_Entrys;
    }

    // within the For LOOP the Menu Items are placed dynamically!
    // Menu Header & Design is done after this for loop!
    if((getMenuSelected() != MENUACCSETTING) && (getMenuSelected() != MENUSPEEDSETTING) && (getMenuSelected() != MENUPICDELAYSETTING)){
      for(int i = 0; i<i_max; i++){
        int menuItemIndex = (_selected +i) % getMaxMenuCount();
        u8g2.setFont(u8g2_font_ncenB10_tr);
        // If Selected menu, is current Menu -->> Draw a Frame on the Menu-Item
        if(menuItemIndex == _selected) {
          // set Font == BOLT
          u8g2.setFontMode(1);
          u8g2.drawFrame(0, 20 + 16 * i, u8g2.getDisplayWidth(), 16);
        }else{
          // set Font to NORMAL
          u8g2.setFontMode(0);
        }
        if(getMenuSelected() == MENUMAIN){
            u8g2.drawStr(5, 32 + 16 * i, menuMAIN_items[menuItemIndex]);           
        }else if(getMenuSelected() == MENUAUTOMODE){
            u8g2.drawStr(5, 32 + 16 * i, menuAutoMode_items[menuItemIndex]);   
        }else if(getMenuSelected() == MENUHANDMODE){
            u8g2.drawStr(5, 32 + 16 * i, menuHandMode_items[menuItemIndex]);                          
        }else if(getMenuSelected() == MENUSETTINGS){
            u8g2.drawStr(5, 32 + 16 * i, menuSETTINGS_items[menuItemIndex]);             
        }else if(getMenuSelected() == MENUAUTOMODESETTINGS){
            u8g2.drawStr(5, 32 + 16 * i, menuAtuoModeSettings_items[menuItemIndex]);   
        }/*else if(getMenuSelected() == MENUACCSETTING){
            Not in Menu Settings Included!
        }*//*else if(getMenuSelected() == MENUSPEEDSETTING){
            Not in Menu Settings Included!
        }*/else if(getMenuSelected() == MENUTESTSCREENSHOT){
            u8g2.drawStr(5, 32 + 16 * i, menuTestBLEScreens_items[menuItemIndex]);              
        }else if(getMenuSelected() == MENUAUTOMODESTEPPERANGLE){
            u8g2.drawStr(5, 32 + 16 * i, menuStepperAngle_items[menuItemIndex]);  
        }else if(getMenuSelected() == MENUPICTUREDELAY){

          if((strcmp(menuPicDelay_items[menuItemIndex], placeHolder) == 0)){
            // Set the Cursor, based on Menu Item Number called
            u8g2.setCursor(5, 32 + 16 * i);
            u8g2.print(systemParameters.pictureDelay,10);
            u8g2.print(" ms");
          }else{
            u8g2.drawStr(5, 32 + 16 * i, menuPicDelay_items[menuItemIndex]);                          
          }

        }else if(getMenuSelected() == MENUACCELERATION){

          if((strcmp(menuSTEPaCC_items[menuItemIndex], placeHolder) == 0)){
            // Set the Cursor, based on Menu Item Number called
            u8g2.setCursor(5, 32 + 16 * i);
            u8g2.print(systemParameters.maxStepperAccel,1);
            u8g2.print(" steps/s2");
          }else{
            u8g2.drawStr(5, 32 + 16 * i, menuSTEPaCC_items[menuItemIndex]);                          
          }

        }else if(getMenuSelected() == MENUSPEED){
          if((strcmp(menuSTEPvEL_items[menuItemIndex], placeHolder) == 0)){
            // Set the Cursor, based on Menu Item Number called
            u8g2.setCursor(5, 32 + 16 * i);
            u8g2.print(systemParameters.maxStepperSpeed,1);
            u8g2.print(" steps/s");
          }else{
            u8g2.drawStr(5, 32 + 16 * i, menuSTEPvEL_items[menuItemIndex]);                          
          }
        }
      }
    }
    // Set Display Header & Parameter Changes here:
    if(getMenuSelected() == MENUMAIN){
      u8g2.drawStr(5, 12, menuMAIN_Header);           
    }else if(getMenuSelected() == MENUSETTINGS){
      u8g2.drawStr(5, 12, menuSETTINGS_Header);             
    }else if(getMenuSelected() == MENUAUTOMODE){
      u8g2.drawStr(5, 12, menuAutoMode_Header);    
    }else if(getMenuSelected() == MENUHANDMODE){
      u8g2.drawStr(5, 12, menuHandMode_Header);          
    } else if(getMenuSelected() == MENUACCSETTING){
      u8g2.drawStr(5, 12, menuAccSettings_Header);
      if(!updated){   
        systemParameters.maxStepperAccel = systemParameters.maxStepperAccel + _selected;
        if(systemParameters.maxStepperAccel < MINSTEPPERACCELERATION){
          systemParameters.maxStepperAccel = MINSTEPPERACCELERATION;
        }else if(systemParameters.maxStepperAccel > MAXSTEPPERACCELERATION){
          systemParameters.maxStepperAccel = MAXSTEPPERACCELERATION;
        }
        updated = true; // Set Parameter Update to TRUE
      }
      u8g2.setCursor(5,32);
      u8g2.print(systemParameters.maxStepperAccel,1);
      u8g2.print(" steps/s2");
    }else if(getMenuSelected() == MENUSPEEDSETTING){
      u8g2.drawStr(5, 12, menuVelSettings_Header);
      if(!updated){   
        systemParameters.maxStepperSpeed = systemParameters.maxStepperSpeed + _selected;
        if(systemParameters.maxStepperSpeed < MINSTEPPERSPEED){
          systemParameters.maxStepperSpeed = MINSTEPPERSPEED;
        }else if(systemParameters.maxStepperSpeed > MAXSTEPPERSPEED){
          systemParameters.maxStepperSpeed = MAXSTEPPERSPEED;
        }
        updated = true; // Set Parameter Update to TRUE
      }
      u8g2.setCursor(5,32);
      u8g2.print(systemParameters.maxStepperSpeed,1);
      u8g2.print(" steps/s");        
    }else if(getMenuSelected() == MENUTESTSCREENSHOT){
      u8g2.drawStr(5, 12, menuTestBLEScreens_Header);           
    }else if(getMenuSelected() == MENUSPEED){
      u8g2.drawStr(5, 12, menuSpeed_Header);    
    }else if(getMenuSelected() == MENUAUTOMODESETTINGS){
      u8g2.drawStr(5, 12, menuAutoModeSettings_Header);    
    }else if(getMenuSelected() == MENUACCELERATION){
      u8g2.drawStr(5, 12, menuAccSettings_Header); 
    }else if(getMenuSelected() == MENUAUTOMODESTEPPERANGLE){
      u8g2.drawStr(5, 12, menuStepperAngle_Header);    
    }else if(getMenuSelected() == MENUPICTUREDELAY){
      u8g2.drawStr(5,12, menuPicDelay_Header);
    }else if(getMenuSelected() == MENUPICDELAYSETTING){
      u8g2.drawStr(5, 12, menuPictureDelay_Header);
      if(!updated){   
        systemParameters.pictureDelay = systemParameters.pictureDelay + _selected;
        if(systemParameters.pictureDelay < MINPICTUREDELAY){
          systemParameters.pictureDelay = MINPICTUREDELAY;
        }else if(systemParameters.pictureDelay > MAXDPICTUREDELAY){
          systemParameters.pictureDelay = MAXDPICTUREDELAY;
        }
        updated = true; // Set Parameter Update to TRUE
      }
      u8g2.setCursor(5,32);
      u8g2.print(systemParameters.pictureDelay,10);
      u8g2.print(" ms");        
    }
    // Corner Illumination Effect:
    // Left UP
    u8g2.drawLine(0, 0, 5, 0);
    u8g2.drawLine(0, 0, 0, 5);

    // Right UP
    u8g2.drawLine(122, 0, 127, 0);
    u8g2.drawLine(127, 0, 127, 5);

    // Left DOWN
    u8g2.drawLine(0, 58, 0, 63);
    u8g2.drawLine(0, 63, 5, 63);

    // Right DOWN
    u8g2.drawLine(122, 63, 127, 63);
    u8g2.drawLine(127, 63, 127, 58);

  } while (u8g2.nextPage());/* OLEDMainMenu() */

} // OLEDMainMenu()

-----------------------------------------------------------------------------------------

nachstehend, Footer Comment is always added, also if a footer comment already exists!

/**
 * @brief Class: MyCallbacks::onDisconnect() BLE Function
 * @param pServer TODO
 */
void MyCallbacks::onDisconnect(BLEServer* pServer){
    connected = false;
} // MyCallbacks::onDisconnect()/* MyCallbacks::onDisconnect() */



==========================================================================================
ERLEDIGT:

-----------------------------------------------------------------------------------------

Nachstehend aus minifiglightning system SSEWrapper::setup -->> Komische Parameter darstellung wird NICHT erfolgreich erkannt und sauber inline kommentiert!!!

/**
 * @brief SSEWrapper::setup() -- Setup Method
 * @param *request) TODO
 */
void SSEWrapper::setup(void (*SSEhandleRequest)(AsyncWebServerRequest *request)) {
  // All Webserver Handler Requests has to be specified here

}/* SSEWrapper::setup() */

-----------------------------------------------------------------------------------------

nachstehendes kommentar am Zeilenende verursacht parser issues!

uint8_t hex_c(uint8_t   n) {    // convert '0'..'9','A'..'F' to 0..15
  n -= '0';
  if(n>9)  n -=   7;
  n &= 0x0F;
  return n;
} 

-----------------------------------------------------------------------------------------

nachstehend void clear() findet der parser nicht!!!

class LeadFilter {
public:
     LeadFilter() :
        _last_velocity(0) {
    }

    // setup min   and max radio values in CLI
    int32_t         get_position(int32_t pos, int16_t   vel, float lag_in_seconds = 1.0);
    void            clear() { _last_velocity   = 0; }

private:
    int16_t         _last_velocity;

};

-----------------------------------------------------------------------------------------

das wird nicht korrekt extrahiert wenn cast innerhalb des konstruktors verwendet werden!

    bool config(IPAddress local_ip, IPAddress gateway, IPAddress subnet, IPAddress dns1 = (uint32_t)0x00000000, IPAddress dns2 = (uint32_t)0x00000000){

        return true;
    }

-----------------------------------------------------------------------------------------

Inkorrektes einfügen von footer coments wenn z.B. innerhalb vom sourcecode ebenso mit curly-brackets gearbeitet wird! Nachstehender code aus HTTP_CLIENT_MOCK.h

/**
 * @brief void addHeader(const String& name, const String& value, bool first = false, bool replace = true);
 * @param &name TODO
 * @param &value TODO
 * @param first TODO – default value if not overloaded: false
 * @param replace TODO – default value if not overloaded: true
 */
    void addHeader(const String &name, const String &value, bool first = false, bool replace = true)
    {
        std::cout << "HTTPClient:Mock add header: " << name.c_str() << " with value: " << value.c_str() << std::endl;

        // not allow set of Header handled by code
        if (!name.equalsIgnoreCase(F("Connection")) &&
            !name.equalsIgnoreCase(F("User-Agent")) &&
            !name.equalsIgnoreCase(F("Host")) &&
            !(name.equalsIgnoreCase(F("Authorization")) && _base64Authorization.length())) {

            String headerLine = "\\\"";
            headerLine += name;
            headerLine += "\\\": \\\"";
            headerLine += value;
            headerLine += "\\\"";

            if (_headers.length() == 0)
            {
                // Wenn _headers leer ist, initialisiere ein JSON-Objekt
                _headers = "{" + headerLine + "}";
            }
            else
            {
                // JSON-Objekt aktualisieren
                if (replace)
                {
                    // Header ersetzen, falls vorhanden
                    int headerStart = _headers.indexOf("\\\"" + name + "\\\": ");
                    if (headerStart != -1)
                    {
                        int headerEnd = _headers.indexOf(',', headerStart);
                        if (headerEnd == -1)
                        {
                            headerEnd = _headers.indexOf('}', headerStart);
                        }
                        if (headerEnd != -1)
                        {
                            // Entferne den bestehenden Eintrag
                            _headers = _headers.substring(0, headerStart) + _headers.substring(headerEnd + 1);
                            // Bereinige das Komma am Ende, falls nötig
                            if (_headers[headerStart - 1] == ',' && headerStart > 0)
                            {
                                _headers.remove(headerStart - 1, 1);
                            }
                        }
                    }
                }

                // Header hinzufügen
                if (first)
                {
                    // Header an den Anfang hinzufügen
                    _headers = "{" + headerLine + ", " + _headers.substring(1);
                }
                else
                {
                    // Header ans Ende hinzufügen (vor der abschließenden `}`)
                    int closingBraceIndex = _headers.lastIndexOf('}');
                    if (closingBraceIndex != -1)
                    {
                        _headers = _headers.substring(0, closingBraceIndex) + ", " + headerLine + "}";
                    }
                }/* addHeader() */
            }
        }
    }

-----------------------------------------------------------------------------------------
   parameter parsing funktioniert nicht mit initialwert:

   /**
   * @brief sendRequest -->> Add your description here
   * @param type TODO
   * @param NULL TODO
   * @param 0 TODO
   * @return TODO
   */
      int sendRequest(const char* type, uint8_t* payload = NULL, size_t _size = 0){
-----------------------------------------------------------------------------------------

==========================================================================================