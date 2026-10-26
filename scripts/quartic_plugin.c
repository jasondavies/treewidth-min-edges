/* Adapt the existing verified checker to genquarticg's OUTPROC hook.
 * Register tw_quartic_summary with atexit via genquarticg's PLUGIN_INIT.
 * Unlike geng, genquarticg has no SUMMARY hook. The exported numwritten
 * provides an independent generator count to compare with callback calls.
 */
#define TW_MAXN 17
#define TW_TARGET 7
#include "treewidth.c"

extern nauty_counter numwritten;

void tw_quartic_summary(void)
{
    tw_summary(numwritten, 0.0); /* Generator reports its own elapsed CPU time. */
}
