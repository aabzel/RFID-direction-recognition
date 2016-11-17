#ifndef __SCHMITT_TRIGGER_SM_HEADER
#define __SCHMITT_TRIGGER_SM_HEADER

#include "variables.h"

#include "FreeRTOS.h"

#include "task.h"


#define DFLT_THRESHOLD (7)

extern U16 dfltTreashold; 

// Hysteresis events
// Inputs for the Hysteresis state machime
typedef enum
{
 HYST_EV_UP,     //0 
 HYST_EV_MID,    //1
 HYST_EV_DOWN,   //2
 
 HYST_CNT_EVENTS //3
}enHYST_event;


// Hysteresis states of the Hysteresis state machine
typedef enum
{
 HYST_ST_UNDEF_UP,   //0
 HYST_ST_MID_UP,     //1
 HYST_ST_DOWN_UP,    //2
 HYST_ST_UNDEF_MID,  //3
 HYST_ST_UP_MID,     //4
 HYST_ST_DOWN_MID,   //5
 HYST_ST_UNDEF_DOWN, //6
 HYST_ST_UP_DOWN,    //7
 HYST_ST_MID_DOWN,   //8
 HYST_ST_UNDEF,      //9
 
 HYST_CNT_STATES     //10
}enHYST_state;

// HYST actions outputs for the HYST state machime
typedef enum
{
 HYST_ACT_NONE,     //0
 HYST_ACT_DIR_UP,   //1 
 HYST_ACT_DIR_DOWN, //2 

 HYST_CNT_ACTIONS   //3
}enHYST_action;

#define HYST_QNT_EVENTS (HYST_CNT_EVENTS )
#define HYST_QNT_STATES (HYST_CNT_STATES )
#define HYST_QNT_ACTIONS (HYST_CNT_ACTIONS)



class SchmittTrigger
{
  static const enHYST_state HYST_tableState[HYST_QNT_EVENTS][HYST_QNT_STATES];
  static const enHYST_action HYST_tableAction[HYST_QNT_EVENTS][HYST_QNT_STATES];

  enHYST_event inEvent;
  enHYST_state currState;

  I16 threshold;
  I8 outPut ;
  U8 status;
public:
  U32 IDnum;
  I8 borderCrossing;
  SchmittTrigger();
  enHYST_event GetEvent(I16 firRssiDiff, U8 stat);
  enHYST_state GetState();
  I8 DoAction();
  I8 GetAction();
  void Reset();
};


// extern void RST_process();

#endif // __SCHMITT_TRIGGER_SM_HEADER
