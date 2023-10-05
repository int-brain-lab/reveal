from reveal.api import RevealSite
import pandas as pd
from pathlib import Path
import webbrowser
import numpy as np
import pytest

ASSETS_PATH = Path(__file__).parent / "assets"

def test_basic():
    """
    Test a basic 4-panel site with static images.

    Compare to:
    https://s3.amazonaws.com/reveal.internationalbrainlab.org/basic_test.html
    """

    lu_path = ASSETS_PATH / "left_upper.png"
    ru_path = ASSETS_PATH / "right_upper.png"
    ll_path = ASSETS_PATH / "left_lower.png"
    rl_path = ASSETS_PATH / "right_lower.png"

    arr = np.empty((2,2), object)

    arr[0, 0] = {"image_path": lu_path, "title": "Left Upper"}
    arr[0, 1] = {"image_path": ru_path, "title": "Right Upper"}
    arr[1, 0] = {"image_path": ll_path, "title": "Left Lower"}
    arr[1, 1] = {"image_path": rl_path, "title": "Right Lower"}
    
    df = pd.DataFrame(arr)

    rs = RevealSite(df, "basic_test")

    # bad theme should fail
    with pytest.raises(ValueError):
        rs.build(theme="bla")

    # default theme here
    rs.build(theme="white")
    rs.open()

def test_basic_compare():
    """
    Test a basic 4-panel site with comparison sliders.

    Compare to: 
    https://s3.amazonaws.com/reveal.internationalbrainlab.org/basic_test_slider.html
    """

    lu_path = ASSETS_PATH / "left_upper.png"
    ru_path = ASSETS_PATH / "right_upper.png"
    ll_path = ASSETS_PATH / "left_lower.png"
    rl_path = ASSETS_PATH / "right_lower.png"

    lu_path_cmp = ASSETS_PATH / "left_upper_compare.png"
    ru_path_cmp = ASSETS_PATH / "right_upper_compare.png"
    ll_path_cmp = ASSETS_PATH / "left_lower_compare.png"
    rl_path_cmp = ASSETS_PATH / "right_lower_compare.png"

    arr = np.empty((2,2), object)

    arr[0, 0] = {"image_path": lu_path,
                 "image_path_compare": lu_path_cmp, 
                 "title": "Left Upper",}
    arr[0, 1] = {"image_path": ru_path, 
                 "image_path_compare": ru_path_cmp, 
                 "title": "Right Upper"}
    arr[1, 0] = {"image_path": ll_path,
                 "image_path_compare": ll_path_cmp, 
                 "title": "Left Lower"}
    arr[1, 1] = {"image_path": rl_path,
                 "image_path_compare": rl_path_cmp, 
                 "title": "Right Lower"}
    
    df = pd.DataFrame(arr)

    rs = RevealSite(df, "basic_test_slider")
    rs.build()
    rs.open()





