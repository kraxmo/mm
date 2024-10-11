# mm
Advanced Dungeons &amp; Dragons 1.0 melee manager

This currently runs in CLI to track combat between defined combatants (friends and foes)

Active combatants and all relevant database information currently stored in Access database (plan to convert to sqlite or Snowflake in future)

Combat tracking is round-based. Encounters have rounds, and rounds have initiative-ordered attacks consisting of one (1) attacker and one (1) defender.

Spell use and attacks vs. multiple opponents occur during attack with a 0 to-hit roll on d20
