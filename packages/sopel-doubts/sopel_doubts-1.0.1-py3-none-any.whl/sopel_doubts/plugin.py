"""Press X to doubt.

Originally released under The Unlicense by xnaas at
https://git.actionsack.com/xnaas/sopel-doubts
"""
from sopel import plugin


# yes, both cases of the double struck X need to be included; they are caseless,
# so a case-insensitive regex can't match both with just one.
@plugin.rule(r"^[XⓍ𝕏𝕩]$")
def x_to_doubt(bot, trigger):
	bot.action("doubts")
