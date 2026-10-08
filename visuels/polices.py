"""Police des planches de contrôle (grille des variantes, planches de bannières) : la même sur Linux, Windows et macOS.
Ces planches servent à choisir ; elles ne sont pas publiées, donc la police système suffit."""
import os
from PIL import ImageFont
_ICI = os.path.dirname(os.path.abspath(__file__))
_GRAS = ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 'C:/Windows/Fonts/arialbd.ttf',
         '/System/Library/Fonts/Supplemental/Arial Bold.ttf', os.path.join(_ICI, '..', 'assets', 'fonts', 'Montserrat-ExtraBold.ttf')]
_NORMAL = ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 'C:/Windows/Fonts/arial.ttf',
           '/System/Library/Fonts/Supplemental/Arial.ttf', os.path.join(_ICI, '..', 'assets', 'fonts', 'Montserrat-SemiBold.ttf')]
def police(taille, gras=False):
    for f in (_GRAS if gras else _NORMAL):
        if os.path.exists(f):
            return ImageFont.truetype(f, taille)
    return ImageFont.load_default()
