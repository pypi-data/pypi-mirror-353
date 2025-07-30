import uuid
from datetime import datetime
import pytz
UTC = pytz.utc
from project.models_spartaqube import PaletteColors
from project.sparta_6b7c630ead.sparta_42b75ebdb3 import qube_eeee71e162 as qube_eeee71e162
DEFAULT_PALETTE = [{'color': 'rgba(255, 99, 132, 0.8)'}, {'color':
    'rgba(255, 159, 64, 0.8)'}, {'color': 'rgba(255, 205, 86, 0.8)'}, {
    'color': 'rgba(75, 192, 192, 0.8)'}, {'color':
    'rgba(54, 162, 235, 0.8)'}, {'color': 'rgba(153, 102, 255, 0.8)'}, {
    'color': 'rgba(201, 203, 207, 0.8)'}]


def sparta_9d03e023f2(user_obj) ->list:
    """
    This function returns the default palette
    """
    if user_obj.is_anonymous:
        return DEFAULT_PALETTE
    palette_colors_set = PaletteColors.objects.filter(user=user_obj,
        is_default=True, is_delete=False).all()
    if palette_colors_set.count() > 0:
        palette_colors_obj = palette_colors_set[0]
        default_palette = palette_colors_obj.palette
        default_palette += DEFAULT_PALETTE
    else:
        default_palette = DEFAULT_PALETTE
    return default_palette


def sparta_512b138d77(json_data, user_obj) ->dict:
    """
    Load my palettes
    """
    palette_colors_set = PaletteColors.objects.filter(user=user_obj,
        is_delete=False).all().order_by('-is_default')
    palette_list = []
    for palette_obj in palette_colors_set:
        palette_list.append({'name': palette_obj.name, 'palette_id':
            palette_obj.palette_id, 'palette': palette_obj.palette,
            'is_default': palette_obj.is_default})
    return {'res': 1, 'palette_list': palette_list}


def sparta_511ce48be5(json_data, user_obj) ->dict:
    """
    Create a new palette
    """
    palette = json_data['palette']
    is_default = json_data['is_default']
    date_now = datetime.now().astimezone(UTC)
    palette_id = str(uuid.uuid4())
    if is_default:
        PaletteColors.objects.filter(user=user_obj, is_delete=False).update(
            is_default=False)
    PaletteColors.objects.create(palette_id=palette_id, user=user_obj,
        palette=palette, name=json_data['name'], is_default=is_default,
        last_update=date_now, date_created=date_now)
    return {'res': 1}


def sparta_b29c54e1bf(json_data, user_obj) ->dict:
    """
    Use a palette as default
    """
    PaletteColors.objects.filter(user=user_obj, is_delete=False).update(
        is_default=False)
    palette_id = json_data['palette_id']
    palette_colors_set = PaletteColors.objects.filter(user=user_obj,
        palette_id=palette_id, is_delete=False).all()
    if palette_colors_set.count() > 0:
        palette_colors_obj = palette_colors_set[0]
        palette_colors_obj.is_default = True
        palette_colors_obj.last_update = datetime.now().astimezone(UTC)
        palette_colors_obj.save()
    return {'res': 1}


def sparta_609469fb8d(json_data, user_obj) ->dict:
    """
    Delete palette
    """
    palette_id = json_data['palette_id']
    palette_colors_set = PaletteColors.objects.filter(user=user_obj,
        palette_id=palette_id, is_delete=False).all()
    if palette_colors_set.count() > 0:
        palette_colors_obj = palette_colors_set[0]
        palette_colors_obj.is_delete = True
        palette_colors_obj.last_update = datetime.now().astimezone(UTC)
        palette_colors_obj.save()
    return {'res': 1}

#END OF QUBE
