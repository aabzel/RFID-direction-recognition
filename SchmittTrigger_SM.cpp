
#include "SchmittTrigger_SM.hpp"
#include "RFID_H800_SM.hpp"
#include "Main_API.hpp"
#include "DBM_SM.hpp"
#include "Utils_API.hpp"


U16 dfltTreashold = DFLT_THRESHOLD;

SchmittTrigger::SchmittTrigger()
{
  Reset();
}

void SchmittTrigger::Reset()
{
  currState      = HYST_ST_UNDEF;
  threshold      = dfltTreashold;
  outPut         = 0;
  status         = 0;
  borderCrossing = 0;
  IDnum          = 0;
}


//------------------------------------------------------------------------
enHYST_event SchmittTrigger::GetEvent(I16 firRssiDiff, U8 stat)
{
  status = stat;
  
  if (threshold < firRssiDiff)
  {
    inEvent = HYST_EV_UP;
  }
  else if (firRssiDiff < -threshold)
  {
    inEvent = HYST_EV_DOWN;
  }
  else
  {
    inEvent = HYST_EV_MID;
  }
  
  return inEvent;
}




enHYST_state SchmittTrigger::GetState()
{
  if ((inEvent<HYST_CNT_EVENTS) && (currState< HYST_CNT_STATES))
  {
    currState = HYST_tableState[inEvent][currState];
  }
  else
  {
    Reset();
    return currState;
  }
  return currState;
}


I8 SchmittTrigger::DoAction()
{
  enHYST_action action;
  
  if ((inEvent<HYST_CNT_EVENTS) && (currState< HYST_CNT_STATES))
  {
    action = HYST_tableAction[inEvent][currState];
    
    if (HYST_ACT_DIR_UP == action)
    {
      outPut = 1; // "dirUp"
      borderCrossing=1;
      if(status & 0x40) IDnum |= 0x8000;
      registerEvent(SENESYS_KEY_ENTERED_EVENT, TAG_CROSS, IDnum, 1);
    }
    
    if (HYST_ACT_DIR_DOWN == action)
    {
      outPut = -1;  // "dirDown"
      borderCrossing=1;
      if(status & 0x40) IDnum |= 0x8000;
      registerEvent(SENESYS_KEY_ENTERED_EVENT, TAG_CROSS, IDnum, 0);
    }
  }
  else
  {
  }
  return outPut;
}

I8 SchmittTrigger::GetAction()
{
  return outPut;
}

const enHYST_state SchmittTrigger::HYST_tableState[HYST_QNT_EVENTS][HYST_QNT_STATES] =
{
//  0                  1                2                3                  4                     5                  6                    7                 8                  9     
//  HYST_ST_UNDEF_UP   HYST_ST_MID_UP   HYST_ST_DOWN_UP  HYST_ST_UNDEF_MID  HYST_ST_UP_MID        HYST_ST_DOWN_MID   HYST_ST_UNDEF_DOWN   HYST_ST_UP_DOWN   HYST_ST_MID_DOWN   HYST_ST_UNDEF     
  { HYST_ST_UNDEF_UP,  HYST_ST_MID_UP , HYST_ST_DOWN_UP, HYST_ST_MID_UP   , HYST_ST_MID_UP  ,     HYST_ST_MID_UP  ,  HYST_ST_DOWN_UP   ,  HYST_ST_DOWN_UP , HYST_ST_DOWN_UP ,  HYST_ST_UNDEF_UP   },  // HYST_EV_UP
  { HYST_ST_UP_MID  ,  HYST_ST_UP_MID , HYST_ST_UP_MID , HYST_ST_UNDEF_MID, HYST_ST_UP_MID  ,     HYST_ST_DOWN_MID,  HYST_ST_DOWN_MID  ,  HYST_ST_DOWN_MID, HYST_ST_DOWN_MID,  HYST_ST_UNDEF_MID  },  // evMid
  { HYST_ST_UP_DOWN ,  HYST_ST_UP_DOWN, HYST_ST_UP_DOWN, HYST_ST_MID_DOWN , HYST_ST_MID_DOWN,     HYST_ST_MID_DOWN,  HYST_ST_UNDEF_DOWN,  HYST_ST_UP_DOWN , HYST_ST_MID_DOWN,  HYST_ST_UNDEF_DOWN }   // HYST_EV_DOWN           
};

const enHYST_action SchmittTrigger::HYST_tableAction[HYST_QNT_EVENTS][HYST_QNT_STATES] =
{
//  0                    1                     2                   3                    4                  5                 6                   7                 8                 9     
//  HYST_ST_UNDEF_UP     HYST_ST_MID_UP        HYST_ST_DOWN_UP     HYST_ST_UNDEF_MID    HYST_ST_UP_MID     HYST_ST_DOWN_MID  HYST_ST_UNDEF_DOWN  HYST_ST_UP_DOWN   HYST_ST_MID_DOWN  HYST_ST_UNDEF     
  { HYST_ACT_NONE,       HYST_ACT_NONE    ,    HYST_ACT_NONE,      HYST_ACT_NONE,       HYST_ACT_NONE,     HYST_ACT_DIR_UP,  HYST_ACT_DIR_UP,   HYST_ACT_DIR_UP,  HYST_ACT_DIR_UP,  HYST_ACT_NONE   }, // HYST_EV_UP
  { HYST_ACT_NONE,       HYST_ACT_NONE    ,    HYST_ACT_NONE,      HYST_ACT_NONE,       HYST_ACT_NONE,     HYST_ACT_NONE  ,  HYST_ACT_NONE,     HYST_ACT_NONE,    HYST_ACT_NONE,    HYST_ACT_NONE   }, // HYST_EV_MID
  { HYST_ACT_DIR_DOWN,   HYST_ACT_DIR_DOWN,    HYST_ACT_DIR_DOWN,  HYST_ACT_NONE,       HYST_ACT_DIR_DOWN, HYST_ACT_NONE  ,  HYST_ACT_NONE,     HYST_ACT_NONE,    HYST_ACT_NONE,    HYST_ACT_NONE   }  // HYST_EV_DOWN
};



