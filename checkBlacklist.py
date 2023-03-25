import re


def isNotBlacklisted(filename):
    formatterFilename = filename[0:-4]

    if (not filename.endswith('.png')):
        formatterFilename = filename

    blacklist = [
        'lava_flow.',
        'lava_still',
        'soul_campfire_log_lit',
        'stonecutter_saw',
        'water_flow',
        'water_still',
        'water_overlay',
        'air',
        'piston_inner',
        'podzol_side',
        'bamboo_stalk',
        'frosted_ice_1',
        'frosted_ice_2',
        'frosted_ice_3',
        'dropper_front_vertical',
        'dispenser_front_vertical',
        'beehive_end',
        'brewing_stand_base',
        'dragon_egg',
        'beacon',
        'smooth_stone_slab_side',
        'chorus_plant'
    ]

    if (re.search('campfire_log_lit|flow|front_on|nether_portal|structure_block|jigsaw|comparator|repeater|culk_catalyst_side_bloom|chiseled_bookshelf|bamboo|hopper|item_frame|cauldron|shulker_box|fletching_table|daylight|farmland|table|lightning_rod', formatterFilename)):
        return False

    if (re.search('bottom|top|command|nylium', formatterFilename)):
        return False

    if (re.search('glass|destroy|debug|lectern|grass', formatterFilename)):
        return False

    if (formatterFilename in blacklist):
        return False

    return True
